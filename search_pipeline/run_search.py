from search_pipeline.rag_chain import answer_question

while True:
    #Asking user input
    query = input("\nAsk your question: ")

    #Exit condition
    if query.lower() == "exit":
        break

    #Geting answer from RAG
    answer = answer_question(query)

    #Print final answer
    print("\n🤖 Final Answer:\n")
    print(answer)
    print("-" * 50)
