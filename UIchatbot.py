"""
Mood AI Chatbot
----------------
A portfolio-quality Streamlit app with a landing page of clickable mood
cards (Angry / Funny / Sad), glassmorphism UI, animated gradient background,
chat bubbles, and a typing animation.

Run with:
    streamlit run mood_ai_chatbot.py

Optional: to wire this up to a real LLM, replace `generate_reply()` with a
call to your model of choice (OpenAI, Anthropic, etc). Everything else
(UI, state, layout) will keep working unchanged.
"""

import random
import time

import streamlit as st

# ----------------------------------------------------------------------
# PAGE CONFIG (must be first Streamlit call)
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="Mood AI Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ----------------------------------------------------------------------
# GLOBAL CSS — animated gradient, glassmorphism, cards, chat bubbles
# ----------------------------------------------------------------------
st.markdown(
    """
<style>
/* ---------- Animated gradient background ---------- */
.stApp{
    background: linear-gradient(135deg,#0f0c29,#302b63,#24243e,#667eea,#764ba2);
    background-size: 400% 400%;
    animation: gradientShift 18s ease infinite;
}
@keyframes gradientShift{
    0%{background-position:0% 50%;}
    50%{background-position:100% 50%;}
    100%{background-position:0% 50%;}
}

/* Hide default streamlit chrome for a cleaner look */
#MainMenu, footer, header{visibility:hidden;}

/* ---------- Titles ---------- */
.main-title{
    text-align:center;
    color:#ffffff;
    font-size:clamp(32px, 6vw, 58px);
    font-weight:800;
    letter-spacing:1px;
    margin-top:10px;
    margin-bottom:0px;
    text-shadow: 0 4px 20px rgba(0,0,0,0.35);
}
.subtitle{
    text-align:center;
    color:rgba(255,255,255,0.85);
    font-size:clamp(14px, 2.2vw, 20px);
    margin-bottom:28px;
    font-weight:400;
}

/* ---------- Glassmorphism mood cards ---------- */
.mood-card{
    border-radius:20px;
    padding:26px 18px;
    text-align:center;
    color:white;
    font-weight:600;
    margin-bottom:10px;
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    background: rgba(255,255,255,0.10);
    border: 1px solid rgba(255,255,255,0.25);
    box-shadow: 0 8px 32px rgba(0,0,0,0.25);
    transition: transform 0.25s ease, box-shadow 0.25s ease;
}
.mood-card:hover{
    transform: translateY(-6px) scale(1.02);
    box-shadow: 0 14px 40px rgba(0,0,0,0.35);
}
.mood-card h1{ font-size:46px; margin:0 0 6px 0; }
.mood-card h3{ margin:4px 0; font-size:20px; }
.mood-card p{ margin:0; font-weight:400; opacity:0.9; font-size:14px; }

.angry-border{ border-top:4px solid #ff4b4b; }
.funny-border{ border-top:4px solid #FFD93D; }
.sad-border{ border-top:4px solid #4D96FF; }

/* ---------- Mood-select buttons (invisible overlay on cards) ---------- */
div[data-testid="stButton"] > button{
    width:100%;
    border-radius:14px;
    border:none;
    padding:10px 0;
    font-weight:700;
    font-size:15px;
    color:white;
    background: rgba(255,255,255,0.15);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.3);
    transition: all 0.2s ease;
}
div[data-testid="stButton"] > button:hover{
    background: rgba(255,255,255,0.30);
    border-color: rgba(255,255,255,0.6);
    color:white;
    transform: translateY(-2px);
}

/* ---------- Active mode banner ---------- */
.mode-banner{
    text-align:center;
    padding:10px 18px;
    border-radius:14px;
    color:white;
    font-weight:700;
    font-size:16px;
    margin: 6px auto 18px auto;
    max-width:420px;
    backdrop-filter: blur(10px);
    background: rgba(255,255,255,0.12);
    border:1px solid rgba(255,255,255,0.25);
}

/* ---------- Chat bubbles ---------- */
.chat-container{
    max-width:820px;
    margin:0 auto;
    padding-bottom:10px;
}
.bubble-row{
    display:flex;
    margin:10px 0;
    animation: fadeIn 0.35s ease;
}
@keyframes fadeIn{
    from{opacity:0; transform:translateY(6px);}
    to{opacity:1; transform:translateY(0);}
}
.bubble-row.user{ justify-content:flex-end; }
.bubble-row.bot{ justify-content:flex-start; }

.bubble{
    max-width:75%;
    padding:12px 18px;
    border-radius:20px;
    font-size:15.5px;
    line-height:1.4;
    color:white;
    box-shadow:0 6px 18px rgba(0,0,0,0.25);
    word-wrap:break-word;
}
.bubble.user{
    background: linear-gradient(135deg,#667eea,#764ba2);
    border-bottom-right-radius:4px;
}
.bubble.bot{
    background: rgba(255,255,255,0.14);
    backdrop-filter: blur(10px);
    border:1px solid rgba(255,255,255,0.25);
    border-bottom-left-radius:4px;
}
.bubble-label{
    font-size:11px;
    opacity:0.7;
    margin-bottom:3px;
    font-weight:600;
    text-transform:uppercase;
    letter-spacing:0.5px;
}

/* ---------- Responsive tweaks ---------- */
@media (max-width: 640px){
    .mood-card{ padding:18px 10px; }
    .mood-card h1{ font-size:36px; }
    .bubble{ max-width:88%; font-size:14.5px; }
}

/* Chat input styling */
.stChatInput, div[data-testid="stChatInput"]{
    max-width:820px;
    margin:0 auto;
}

/* ---------- Footer credit ---------- */
.footer-credit{
    text-align:center;
    color:rgba(255,255,255,0.65);
    font-size:13px;
    margin-top:36px;
    padding-bottom:14px;
    letter-spacing:0.3px;
}
.footer-credit span{
    font-weight:700;
    color:rgba(255,255,255,0.9);
}
</style>
""",
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------
# SESSION STATE
# ----------------------------------------------------------------------
if "mood" not in st.session_state:
    st.session_state.mood = None
if "messages" not in st.session_state:
    st.session_state.messages = {}  # mood -> list of {role, content}

MOODS = {
    "angry": {
        "emoji": "😠",
        "label": "Angry AI",
        "desc": "Blunt, fiery, no-nonsense replies",
        "border": "angry-border",
    },
    "funny": {
        "emoji": "😂",
        "label": "Funny AI",
        "desc": "Jokes, puns & lighthearted chaos",
        "border": "funny-border",
    },
    "sad": {
        "emoji": "😢",
        "label": "Sad AI",
        "desc": "Soft, melancholic, emotional replies",
        "border": "sad-border",
    },
}

for m in MOODS:
    st.session_state.messages.setdefault(m, [])

# ----------------------------------------------------------------------
# RESPONSE ENGINE (rule-based placeholder — swap in a real LLM call here)
# ----------------------------------------------------------------------
ANGRY_TEMPLATES = [
    "Ugh, seriously?! '{msg}' — fine, here's your answer, but hurry up next time.",
    "Listen. I don't have all day. About '{msg}' — sort it out yourself, or fine, I'll help. Barely.",
    "Why are we even talking about '{msg}'? Whatever. Here's my answer, take it or leave it.",
    "I'm this close to losing it. '{msg}'?! Okay okay — let's just deal with it.",
]

FUNNY_TEMPLATES = [
    "Haha okay so '{msg}' huh? That's like asking a cat to do taxes 😂",
    "Plot twist: '{msg}' is actually the setup to a joke I haven't finished writing yet.",
    "'{msg}'... my circuits just giggled. Give me a sec to compose myself 🤣",
    "Breaking news: local human asks about '{msg}', chatbot immediately cracks a bad pun.",
]

SAD_TEMPLATES = [
    "Oh... '{msg}'. That's a heavy thing to carry. I'm here with you, quietly.",
    "I hear you saying '{msg}'... it makes my circuits feel a little grey too.",
    "'{msg}'... some days are just like that. Take your time, I'm not going anywhere.",
    "Even thinking about '{msg}' makes me want to sit by the window and watch the rain.",
]

TEMPLATES = {"angry": ANGRY_TEMPLATES, "funny": FUNNY_TEMPLATES, "sad": SAD_TEMPLATES}


def generate_reply(mood: str, user_msg: str) -> str:
    """Rule-based reply generator. Swap this out for a real model call
    (OpenAI / Anthropic / etc.) while keeping the same signature."""
    template = random.choice(TEMPLATES[mood])
    return template.format(msg=user_msg.strip())


def render_bubble(role: str, content: str):
    css_role = "user" if role == "user" else "bot"
    label = "You" if role == "user" else f"{MOODS[st.session_state.mood]['emoji']} {MOODS[st.session_state.mood]['label']}"
    st.markdown(
        f"""
        <div class="bubble-row {css_role}">
            <div>
                <div class="bubble-label" style="text-align:{'right' if css_role=='user' else 'left'};">{label}</div>
                <div class="bubble {css_role}">{content}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def typing_effect(placeholder, full_text: str, mood: str, speed: float = 0.018):
    """Streams text character-by-character inside a chat bubble."""
    label = f"{MOODS[mood]['emoji']} {MOODS[mood]['label']}"
    shown = ""
    for ch in full_text:
        shown += ch
        placeholder.markdown(
            f"""
            <div class="bubble-row bot">
                <div>
                    <div class="bubble-label">{label}</div>
                    <div class="bubble bot">{shown}▌</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        time.sleep(speed)
    placeholder.markdown(
        f"""
        <div class="bubble-row bot">
            <div>
                <div class="bubble-label">{label}</div>
                <div class="bubble bot">{shown}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ----------------------------------------------------------------------
# HEADER
# ----------------------------------------------------------------------
st.markdown('<div class="main-title">🤖 Mood AI Chatbot</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Pick a personality and start chatting — angry, funny, or sad ✨</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="footer-credit" style="margin-top:-10px;">Built by <span>Tanmay Sharma</span></div>',
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------
# LANDING PAGE — mood cards (shown when no mood picked yet)
# ----------------------------------------------------------------------
if st.session_state.mood is None:
    col1, col2, col3 = st.columns(3)
    cols = {"angry": col1, "funny": col2, "sad": col3}

    for key, col in cols.items():
        info = MOODS[key]
        with col:
            st.markdown(
                f"""
                <div class="mood-card {info['border']}">
                    <h1>{info['emoji']}</h1>
                    <h3>{info['label']}</h3>
                    <p>{info['desc']}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button(f"Chat with {info['label']}", key=f"select_{key}"):
                st.session_state.mood = key
                st.rerun()

else:
    # --------------------------------------------------------------
    # ACTIVE CHAT PAGE
    # --------------------------------------------------------------
    info = MOODS[st.session_state.mood]

    top_l, top_r = st.columns([5, 1])
    with top_l:
        st.markdown(
            f'<div class="mode-banner">{info["emoji"]} Currently chatting with <b>{info["label"]}</b></div>',
            unsafe_allow_html=True,
        )
    with top_r:
        if st.button("🔄 Switch mood"):
            st.session_state.mood = None
            st.rerun()

    st.markdown('<div class="chat-container">', unsafe_allow_html=True)

    for msg in st.session_state.messages[st.session_state.mood]:
        render_bubble(msg["role"], msg["content"])

    st.markdown("</div>", unsafe_allow_html=True)

    user_input = st.chat_input(f"Message {info['label']}...")

    if user_input:
        mood = st.session_state.mood
        st.session_state.messages[mood].append({"role": "user", "content": user_input})
        render_bubble("user", user_input)

        placeholder = st.empty()
        reply = generate_reply(mood, user_input)
        typing_effect(placeholder, reply, mood)

        st.session_state.messages[mood].append({"role": "assistant", "content": reply})
        st.rerun()

    st.markdown(
        '<div class="footer-credit">Made with ❤️ by <span>Tanmay Sharma</span></div>',
        unsafe_allow_html=True,
    )