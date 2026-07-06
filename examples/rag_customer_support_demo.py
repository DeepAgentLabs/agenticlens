import os
import time
from openai import OpenAI

from agenticlens import profile, step


client = OpenAI()

DOCS = [
    "Refund policy: Customers can request a refund within 30 days of delivery.",
    "Refund policy: Items must be unused and in original packaging.",
    "Shipping policy: Standard shipping takes 5 to 7 business days.",
    "Shipping policy: Express shipping takes 2 to 3 business days.",
    "Order tracking: Customers can track orders using their order ID.",
    "Order tracking: If tracking is not updated for 48 hours, contact support.",
    "Return policy: Customers must generate a return label from their account.",
    "Return policy: Return pickup is available only in selected ZIP codes.",
    "Cancellation policy: Orders can be cancelled before shipment.",
    "Cancellation policy: Shipped orders cannot be cancelled.",
    "Payment policy: Refunds are processed to the original payment method.",
    "Payment policy: Refunds may take 5 to 10 business days.",
]

SYSTEM_PROMPT = """
You are a helpful customer support assistant.
Answer only using the provided context.
If the answer is not in the context, say you do not have enough information.
"""


def simple_retrieve(query: str, top_k: int = 10):
    query_words = set(query.lower().split())

    scored_docs = []
    for doc in DOCS:
        doc_words = set(doc.lower().split())
        score = len(query_words.intersection(doc_words))
        scored_docs.append((score, doc))

    scored_docs.sort(reverse=True, key=lambda x: x[0])
    return [doc for score, doc in scored_docs[:top_k] if score > 0]


def call_llm(user_question: str, context_chunks: list[str]):
    context = "\n".join(f"- {chunk}" for chunk in context_chunks)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"""
User question:
{user_question}

Retrieved context:
{context}

Give a clear answer.
""",
        },
    ]

    return client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0,
    )


def main():
    user_question = "Can I get a refund and how long will it take?"

    with profile("Real RAG Customer Support") as workflow:
        with step(
            "User Prompt",
            type="planner",
            prompt=user_question,
        ):
            pass

        with step(
            "Retrieve Policy Chunks",
            type="retriever",
            chunk_count=10,
            avg_tokens_per_chunk=35,
        ) as s:
            start = time.time()
            chunks = simple_retrieve(user_question, top_k=10)
            s.step.metrics.latency = time.time() - start
            s.step.metadata["retrieved_chunks"] = chunks
            s.step.metadata["chunk_count"] = len(chunks)
            print("\nRetrieved Chunks:")
            for chunk in chunks:
                print("-", chunk)
            chunks = simple_retrieve(user_question, top_k=10)

        with step(
            "Generate Answer",
            type="llm_call",
            provider="openai",
            model="gpt-4o-mini",
            prompt=SYSTEM_PROMPT,
        ) as s:
            start = time.time()
            response = call_llm(user_question, chunks)
            s.record(response)
            s.step.metrics.latency = time.time() - start

        answer = response.choices[0].message.content
        print("\nFinal Answer:")
        print(answer)

    print("\nWorkflow Summary:")
    print("Total tokens:", workflow.total_tokens)
    print("Total cost:", workflow.total_cost)


if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("Please set OPENAI_API_KEY before running this demo.")
    main()