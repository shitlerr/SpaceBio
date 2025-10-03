# space_biology_chatbot.py
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load your OPTIMIZED space biology knowledge base
try:
    with open("space_biology_knowledge_optimized.txt", "r", encoding="utf-8") as f:
        knowledge_base = f.read()
    print("✅ Optimized Space Biology knowledge base loaded successfully!")
    print(f"📚 Knowledge base size: {len(knowledge_base)} characters")
    
    # Split knowledge base into individual documents for smarter searching
    documents = [doc.strip() for doc in knowledge_base.split("---") if doc.strip()]
    print(f"📄 Loaded {len(documents)} research documents")
    
except FileNotFoundError:
    print("❌ Error: space_biology_knowledge_optimized.txt not found!")
    print("Please run data_preparation.py first to create the knowledge base.")
    exit()

print("\n🚀 NASA Space Biology Expert Chatbot Ready!")
print("Type 'quit' or 'exit' to end the conversation\n")

def find_relevant_documents(question, documents, max_docs=3):
    """
    Find the most relevant documents for a question using simple keyword matching
    """
    question_lower = question.lower()
    relevant_docs = []
    
    # Simple keyword matching - you can make this smarter later
    for doc in documents:
        doc_lower = doc.lower()
        # Count how many question words appear in the document
        keyword_matches = sum(1 for word in question_lower.split()
                            if len(word) > 3 and word in doc_lower)
        
        if keyword_matches > 0:
            relevant_docs.append((doc, keyword_matches))
    
    # Sort by relevance (most matches first)
    relevant_docs.sort(key=lambda x: x[1], reverse=True)
    
    # Return top documents
    return [doc for doc, score in relevant_docs[:max_docs]]

def chat_with_space_expert():
    conversation_history = []
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ["quit", "exit", "bye"]:
                print("Bot: Thank you for chatting about space biology! 🚀")
                break
                
            if not user_input:
                continue

            print("🔍 Searching for relevant research...")
            
            # Find only relevant documents for this specific question
            relevant_docs = find_relevant_documents(user_input, documents)
            
            if not relevant_docs:
                # If no specific matches, use a few general documents
                relevant_docs = documents[:2]
                print("📖 Using general space biology knowledge...")
            else:
                print(f"📚 Found {len(relevant_docs)} relevant research papers...")
            
            # Combine relevant documents
            context = "\n\n".join(relevant_docs)
            
            # Create a focused prompt
            prompt = f"""Based on this NASA space biology research:

{context}

Question: {user_input}

Please provide a concise answer focused on the research above. If the research doesn't contain relevant information, say so."""

            # Use minimal messages for faster response
            messages = [
                {"role": "system", "content": "You are a helpful NASA Space Biology Expert. Answer questions based on the provided research context."},
                {"role": "user", "content": prompt}
            ]

            print("🤔 Generating response...")
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=400,  # Shorter responses for speed
                temperature=0.7
            )

            reply = response.choices[0].message.content
            print("\nBot:", reply)
            print("-" * 50)

            # Keep conversation history short
            conversation_history.append({"role": "user", "content": user_input})
            conversation_history.append({"role": "assistant", "content": reply})
            
            if len(conversation_history) > 6:  # Keep only last 3 exchanges
                conversation_history = conversation_history[-6:]

        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Please try again with a different question.")

if __name__ == "__main__":
    chat_with_space_expert()
