import os
import psycopg2
from pgvector.psycopg2 import register_vector
from pypdf import PdfReader
import ollama

DB_URL = os.getenv("DATABASE_URL", "postgresql://lia:lia1234@localhost:5432/lia_db")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
client = ollama.Client(host=OLLAMA_HOST)

def get_conn():
    conn = psycopg2.connect(DB_URL)
    return conn

def setup_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    conn.commit()
    register_vector(conn)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS documentos (
            id SERIAL PRIMARY KEY,
            archivo TEXT,
            chunk_index INTEGER,
            contenido TEXT,
            embedding vector(768)
        );
    """)
    conn.commit()
    cur.close()
    conn.close()
    print("✅ Base de datos lista")


def chunk_text(text, size=500, overlap=50):
    words = text.split()
    chunks = []
    for i in range(0, len(words), size - overlap):
        chunks.append(" ".join(words[i:i + size]))
    return chunks

def index_pdf(filepath):
    print(f"📄 Indexando: {filepath}")
    reader = PdfReader(filepath)
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    chunks = chunk_text(text)

    conn = get_conn()
    cur = conn.cursor()

    for i, chunk in enumerate(chunks):
        resp = client.embeddings(model="nomic-embed-text", prompt=chunk)
        embedding = resp["embedding"]
        cur.execute(
            "INSERT INTO documentos (archivo, chunk_index, contenido, embedding) VALUES (%s, %s, %s, %s)",
            (filepath, i, chunk, embedding)
        )
        print(f"  chunk {i+1}/{len(chunks)} indexado")

    conn.commit()
    cur.close()
    conn.close()
    print(f"✅ {filepath} indexado completo")

if __name__ == "__main__":
    setup_db()
    # Indexar todos los PDFs en ./docs
    import glob
    os.makedirs("docs", exist_ok=True)
    pdfs = glob.glob("docs/*.pdf")
    if not pdfs:
        print("⚠️  No hay PDFs en ./docs — agrega documentos y vuelve a correr")
    for pdf in pdfs:
        index_pdf(pdf)
