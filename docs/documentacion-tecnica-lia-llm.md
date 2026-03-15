# Documentación Técnica — LIA LLM Service

## 1. Arquitectura general

El servicio implementa un pipeline RAG (Retrieval-Augmented Generation) compuesto por dos flujos principales:

```
[Usuario] -> [API FastAPI]
                |
                |---> [Servicio de Indexación]
                |         └─ Extrae texto del PDF
                |         └─ Genera embeddings (sentence-transformers)
                |         └─ Almacena chunks + vectores en pgvector
                |
                └---> [Servicio de Consulta RAG]
                          └─ Genera embedding de la pregunta
                          └─ Búsqueda semántica en pgvector (top-k chunks)
                          └─ Construye prompt con contexto recuperado
                          └─ Llama a Ollama (Llama 3.2 3B)
                          └─ Retorna respuesta al usuario
```

---

## 2. Endpoints de la API

### POST /index

Indexa un documento PDF en la base de datos vectorial.

**Request:**
- `Content-Type: multipart/form-data`
- Body: archivo PDF (`file`)

**Response:**
```json
{
  "message": "Documento indexado exitosamente",
  "chunks_indexed": 142,
  "document": "NTC-ISO-IEC-17025.pdf"
}
```

| Código HTTP | Descripción |
|---|---|
| 200 | Indexación exitosa |
| 422 | Archivo no válido o no es PDF |
| 500 | Error interno al procesar el documento |

---

### POST /query

Realiza una consulta en lenguaje natural sobre los documentos indexados.

**Request:**
```json
{
  "question": "¿Qué requisitos exige la norma para la trazabilidad de mediciones?",
  "top_k": 5
}
```

| Campo | Tipo | Requerido | Descripción |
|---|---|---|---|
| `question` | string | Sí | Pregunta en lenguaje natural |
| `top_k` | integer | No (default: 5) | Número de chunks de contexto a recuperar |

**Response:**
```json
{
  "answer": "Según la sección 6.4.7 de la NTC-ISO/IEC 17025, los laboratorios deben...",
  "sources": [
    {
      "chunk_id": "17025_sec6_chunk3",
      "text": "...",
      "similarity_score": 0.91
    }
  ],
  "model": "llama3.2:3b",
  "response_time_seconds": 118.4
}
```

| Código HTTP | Descripción |
|---|---|
| 200 | Consulta exitosa |
| 400 | Pregunta vacía o inválida |
| 503 | Ollama no disponible |

---

### GET /health

Verifica el estado del servicio.

**Response:**
```json
{
  "status": "ok",
  "ollama": "connected",
  "db": "connected",
  "model": "llama3.2:3b"
}
```

---

### GET /documents

Lista los documentos indexados.

**Response:**
```json
{
  "documents": [
    {
      "name": "NTC-ISO-IEC-17025.pdf",
      "chunks": 142,
      "indexed_at": "2026-03-14T18:30:00"
    }
  ]
}
```

---

## 3. Pipeline RAG — Detalle técnico

### 3.1. Indexación

1. **Extracción de texto:** `PyMuPDF (fitz)` extrae el texto de cada página del PDF.
2. **Fragmentación (chunking):** El texto se divide en chunks de ~500 tokens con 50 tokens de solapamiento para preservar contexto entre fragmentos.
3. **Generación de embeddings:** Se usa el modelo `all-MiniLM-L6-v2` de `sentence-transformers` (384 dimensiones).
4. **Almacenamiento:** Cada chunk y su vector se guardan en PostgreSQL con la extensión `pgvector`, usando un índice HNSW para búsquedas aproximadas eficientes.

### 3.2. Consulta

1. **Embedding de la pregunta:** La pregunta del usuario se transforma al mismo espacio vectorial con `all-MiniLM-L6-v2`.
2. **Búsqueda semántica:** Se ejecuta una consulta de similitud coseno en pgvector para recuperar los `top_k` chunks más relevantes.
3. **Construcción del prompt:**

```
[SYSTEM]
Eres un asistente técnico del laboratorio LIA. Responde usando únicamente
la información del contexto proporcionado. Si la respuesta no está en el
contexto, indícalo claramente. Cita la sección del documento cuando sea posible.

[CONTEXTO]
{chunks recuperados}

[PREGUNTA]
{pregunta del usuario}
```

4. **Generación:** El prompt se envía a Ollama (Llama 3.2 3B) vía HTTP en `localhost:11434/api/generate`.
5. **Respuesta:** Se retorna la respuesta del modelo junto con los chunks fuente y el score de similitud.

---

## 4. Base de datos — Esquema pgvector

```sql
CREATE TABLE document_chunks (
    id          SERIAL PRIMARY KEY,
    document    VARCHAR(255) NOT NULL,
    chunk_index INTEGER NOT NULL,
    content     TEXT NOT NULL,
    embedding   VECTOR(384),
    created_at  TIMESTAMP DEFAULT NOW()
);

CREATE INDEX ON document_chunks
USING hnsw (embedding vector_cosine_ops);
```

---

## 5. Variables de entorno

| Variable | Descripción | Default |
|---|---|---|
| `DATABASE_URL` | URL de conexión a PostgreSQL | — |
| `OLLAMA_BASE_URL` | URL del servidor Ollama | `http://localhost:11434` |
| `EMBEDDING_MODEL` | Modelo de embeddings | `all-MiniLM-L6-v2` |
| `CHUNK_SIZE` | Tamaño de fragmentos en tokens | `500` |
| `CHUNK_OVERLAP` | Solapamiento entre chunks | `50` |
| `TOP_K_DEFAULT` | Chunks a recuperar por defecto | `5` |

---

## 6. Limitaciones conocidas (v1.0)

- **Tiempo de respuesta:** Aproximadamente 2 minutos en CPU. Se resuelve con Jetson Orin Nano.
- **Sin streaming:** La respuesta llega completa. Streaming planificado para v1.1.
- **Idioma:** Optimizado para español técnico.
- **Formatos:** Solo PDF en v1.0. DOCX e imágenes escaneadas (OCR) en fases futuras.
