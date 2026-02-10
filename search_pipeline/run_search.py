from search_pipeline.rag_chain import answer_question

while True:
    query = input("\nAsk your question: ")

    if query.lower() == "exit":
        break

    answer = answer_question(query)

    print("\n🤖 Final Answer:\n")
    print(answer)
    print("-" * 50)