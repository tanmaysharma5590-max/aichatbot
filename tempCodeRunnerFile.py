

chat_model = ChatHuggingFace(llm=llm)

result = chat_model.invoke("what is data science ?")

print(result.content)