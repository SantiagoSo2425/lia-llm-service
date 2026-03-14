from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import ollama
import os
import ollama

client = ollama.Client(host=os.getenv("OLLAMA_HOST", "http://localhost:11434"))


app = FastAPI(title="LIA LLM Service")

class ChatRequest(BaseModel):
    query: str
    context: str = ""  # aquí irá el contexto RAG más adelante

class ChatResponse(BaseModel):
    response: str
    model: str

SYSTEM_PROMPT = """Eres LIA, un asistente especializado en gestión documental 
de laboratorios acreditados bajo ISO 17025. Ayudas a técnicos y auditores a 
encontrar documentos, bitácoras, protocolos y evidencias de calibración. 
Responde siempre en español, de forma precisa y concisa."""

@app.get("/health")
def health():
    return {"status": "ok", "model": "llama3.2:3b"}

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
        ]
        if request.context:
            messages.append({
                "role": "system",
                "content": f"Contexto de documentos relevantes:\n{request.context}"
            })
        messages.append({"role": "user", "content": request.query})

        response = ollama.chat(
            model="llama3.2:3b",
            messages=messages,
            options={"num_predict": 300}
        )
        return ChatResponse(
            response=response["message"]["content"],
            model="llama3.2:3b"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

