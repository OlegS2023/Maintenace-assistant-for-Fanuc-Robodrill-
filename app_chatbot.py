import streamlit as st
import chromadb
import ollama
from sentence_transformers import SentenceTransformer
import re

# strona
st.set_page_config(page_title="Fanuc Robodrill Expert", page_icon="🤖")
st.title("🤖 Fanuc Robodrill AI Expert")
st.markdown("Witaj! Jestem Twoim asystentem technicznym. Przeanalizowałem instrukcję obsługi i pomogę Ci naprawić maszynę.")

# CACHOWANIE (PRZYSPIESZENIE)
@st.cache_resource
def load_resources():
    model_emb = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    client = chromadb.PersistentClient(path="robodrill_db")
    collection = client.get_collection("robodrill")
    return model_emb, collection

model_emb, collection = load_resources()

# FUNKCJA RAG
def get_ai_response(user_query):
    # 1. Retrieval
    query_emb = model_emb.encode([user_query]).tolist()
    results = collection.query(query_embeddings=query_emb, n_results=5)
    
    context_parts = []
    chapters = set()
    for i in range(len(results['documents'][0])):
        context_parts.append(f"[Rozdział: {results['metadatas'][0][i]['chapter']}]\n{results['documents'][0][i]}")
        chapters.add(results['metadatas'][0][i]['chapter'])
    
    full_context = "\n\n".join(context_parts)

    # 2. Prompt
    prompt = f"""
    You are a Fanuc Robodrill machine service expert.

    Your task is to help the technician repair the machine using the following manual excerpts.

    RULES:
    1. Answer in a specific and technically accurate manner.
    2. If the excerpts contain a table or list of steps, present them clearly.
    3. If you don't find the answer in the text, honestly state that the manual doesn't provide a solution for this error.
    4. Answer in English, with original technical names and error codes.

    Instruction chunks:
    {full_context}

    Technician question: 
    {user_query}

    Expert answer:
    """

    # 3. Generation
    response = ollama.generate(model='llama3', prompt=prompt)
    return response['response'], chapters

# interfejs + inicjalizacja czatu
if "messages" not in st.session_state:
    st.session_state.messages = []

# Wyświetlanie historii
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("W czym mogę pomóc? (np. Błąd AL-24)"):
    # Dodanie pytania użytkownika do historii
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generowanie odpowiedzi asystenta
    with st.chat_message("assistant"):
        with st.spinner("Przeszukuję instrukcję i generuję odpowiedź..."):
            ai_text, sources = get_ai_response(prompt)
            st.markdown(ai_text)
            st.info(f"📚 Wiedza zaczerpnięta z sekcji: {', '.join(sources)}")
    
    # Dodaj odpowiedź asystenta do historii
    st.session_state.messages.append({"role": "assistant", "content": ai_text})