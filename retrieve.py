from retriever import Retriever

retriever = Retriever()
items = retriever.retrieve("Voetbal")


for item in range(len(items['ids'][0])):
    print(items["distances"][0][item])
    print(items['documents'][0][item])
    print(items['metadatas'][0][item])
    print("-------------------------")
