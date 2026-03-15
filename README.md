# LIA LLM Service

Microservicio de búsqueda inteligente con IA para el **Proyecto LIA** (Laboratorios acreditados ISO 17025 - ITM). Implementa un pipeline RAG (Retrieval-Augmented Generation) usando un modelo de lenguaje local (Llama 3.2 3B) para que técnicos y auditores puedan consultar documentación técnica en lenguaje natural.

---

## Stack tecnológico

| Componente | Tecnología |
|---|---|
| API | FastAPI (Python) |
| Modelo LLM | Llama 3.2 3B via Ollama |
| Base de datos vectorial | PostgreSQL + pgvector |
| Embeddings | sentence-transformers |
| Contenerización | Docker + Docker Compose |

---

## Requisitos previos

- Docker y Docker Compose instalados
- Ollama instalado localmente (https://ollama.com)
- Python 3.11+ (si se ejecuta sin Docker)
- PostgreSQL con extensión `pgvector`

---

## Instalación y ejecución

### 1. Clonar el repositorio

```bash
git clone https://github.com/SantiagoSo2425/lia-llm-service.git
cd lia-llm-service
```

### 2. Descargar el modelo LLM

```bash
ollama pull llama3.2:3b
```

### 3. Configurar variables de entorno

Crear un archivo `.env` en la raíz del proyecto:

```env
DATABASE_URL=postgresql://usuario:password@localhost:5432/lia_db
OLLAMA_BASE_URL=http://localhost:11434
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

### 4. Levantar con Docker Compose

```bash
docker-compose up --build
```

La API quedará disponible en `http://localhost:8000`.  
Documentación interactiva (Swagger): `http://localhost:8000/docs`

---

## Uso básico

**Indexar un documento:**

```bash
curl -X POST http://localhost:8000/index \
  -F "file=@NTC-ISO-IEC-17025.pdf"
```

**Realizar una consulta:**

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "¿Qué requisitos exige la norma para la calibración de equipos?"}'
```

---

## Estructura del proyecto

```
lia-llm-service/
├── app/
│   ├── main.py
│   ├── routes/
│   │   ├── query.py
│   │   └── index.py
│   ├── services/
│   │   ├── llm.py
│   │   ├── rag.py
│   │   └── embeddings.py
│   └── db/
│       └── vector_store.py
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── .env.example
```

---

## Rendimiento

| Entorno | Tiempo de respuesta |
|---|---|
| VM Ubuntu 24.04 (CPU) | ~2 min |
| Jetson Orin Nano (GPU Ampere) | ~8-10 seg (proyectado) |
| Jetson Orin Nano + TensorRT-LLM | ~3-4 seg (fase futura) |

El microservicio está preparado para migrar al Jetson Orin Nano sin modificaciones de código.

---

## Estado del proyecto

- [x] VM Ubuntu 24.04 configurada
- [x] Llama 3.2 3B desplegado con Ollama
- [x] Pipeline RAG completo (FastAPI + pgvector)
- [x] NTC-ISO/IEC 17025 indexada como documento de prueba
- [x] Dockerizado y versionado en GitHub
- [ ] Migración a Jetson Orin Nano
- [ ] Optimización con TensorRT-LLM

---

## Autor

Santiago Suárez Osorio — Semillero de Investigación, ITM  
Proyecto LIA — Componente IA/LLM
