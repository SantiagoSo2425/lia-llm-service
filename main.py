import os
import psycopg2
from pgvector.psycopg2 import register_vector
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import ollama

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://lia:lia1234@localhost:5432/lia_db")
client = ollama.Client(host=OLLAMA_HOST)

app = FastAPI(title="LIA LLM Service")

class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    response: str
    context_used: list[str]

SYSTEM_PROMPT = """Eres LIA, un asistente especializado en gestión documental 
de laboratorios acreditados bajo ISO 17025. Ayudas a técnicos y auditores a 
encontrar documentos, bitácoras, protocolos y evidencias de calibración.
Responde siempre en español, de forma precisa y concisa.
Usa únicamente el contexto proporcionado para responder. Si no encuentras 
la información en el contexto, indícalo claramente."""

def get_context(query: str, top_k: int = 3) -> list[str]:
    try:
        resp = client.embeddings(model="nomic-embed-text", prompt=query)
        embedding = resp["embedding"]
        conn = psycopg2.connect(DATABASE_URL)
        register_vector(conn)
        cur = conn.cursor()
        cur.execute("""
            SELECT contenido FROM documentos
            ORDER BY embedding <-> %s::vector
            LIMIT %s
        """, (embedding, top_k))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return [row[0] for row in rows]
    except Exception:
        return []

@app.get("/health")
def health():
   return {"status": "ok", "model": "gemma3:1b"}

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        context_chunks = get_context(request.query)
        context_text = "\n\n".join(context_chunks) if context_chunks else "Sin contexto disponible."

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "system", "content": f"Contexto de documentos:\n{context_text}"},
            {"role": "user", "content": request.query}
        ]

        response = client.chat(
           model="gemma3:1b",
            messages=messages,
            options={"num_predict": 150, "num_thread":2}
        )
        return ChatResponse(
            response=response["message"]["content"],
            context_used=context_chunks
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
