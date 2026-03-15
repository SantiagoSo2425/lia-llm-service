# Informe de Avance — Proyecto LIA
## Componente IA/LLM — Sprint 1

**Fecha:** 14 de marzo de 2026  
**Responsable:** Santiago Suárez  Osorio
**Semillero:** Investigación   DataOps — ITM

---

## 1. Objetivo del sprint

Implementar y validar el prototipo funcional del microservicio LLM para el Proyecto LIA, siguiendo la arquitectura RAG propuesta en el informe técnico de hardware (Raspberry Pi 5 vs. Jetson Orin Nano).

---

## 2. Logros del sprint

### Infraestructura

- Configuración de VM con Ubuntu 24.04 como entorno de desarrollo y pruebas.
- Instalación y configuración de Ollama para gestión del modelo LLM local.
- Despliegue del modelo Llama 3.2 3B como motor de inferencia principal.

### Pipeline RAG

- Microservicio en FastAPI con pipeline RAG completamente funcional.
- Integración de pgvector sobre PostgreSQL para almacenamiento y búsqueda vectorial.
- Generación de embeddings con sentence-transformers (all-MiniLM-L6-v2).

### Indexación y pruebas

- Indexación exitosa de la NTC-ISO/IEC 17025 como documento de prueba (base normativa del laboratorio).
- Validación de consultas técnicas en lenguaje natural con respuestas que citan fragmentos reales de la norma.
- Endpoints funcionales: `/index`, `/query`, `/health`, `/documents`.

### DevOps

- Stack completo dockerizado con Docker Compose.
- Código versionado en GitHub: `github.com/SantiagoSo2425/lia-llm-service`.

---

## 3. Métricas del sprint

| Métrica | Valor actual |
|---|---|
| Tiempo de respuesta promedio | ~2 minutos |
| Chunks indexados (NTC-ISO 17025) | ~142 |
| Endpoints implementados | 4 |
| Cobertura de pruebas | Manual (casos de auditoría básicos) |

---

## 4. Limitación principal

El tiempo de respuesta actual (~2 minutos por consulta) se debe a que la VM ejecuta el modelo únicamente en CPU, sin aceleración GPU. Esta limitación es conocida y esperada en esta fase de prototipado, y está directamente relacionada con el hardware disponible.

---

## 5. Proyección de rendimiento con hardware objetivo

| Escenario | Tiempo de respuesta |
|---|---|
| VM actual (CPU) | ~2 min |
| Jetson Orin Nano + llama.cpp | ~8-10 seg |
| Jetson Orin Nano + TensorRT-LLM (fase futura) | ~3-4 seg |

Con el Jetson Orin Nano (GPU Ampere) y la optimización adicional mediante TensorRT-LLM y cuantización INT4, el sistema puede alcanzar tiempos de 3-4 segundos por consulta, lo que lo hace completamente viable para uso en auditorías en tiempo real. El microservicio está preparado para migrar a ese hardware sin modificaciones de código. Ese trabajo de optimización está identificado como una fase futura una vez llegue el hardware.

---

## 6. Próximos pasos (Sprint 2)

1. Implementar streaming de respuestas para mejorar la percepción de velocidad.
2. Ampliar el corpus documental: indexar bitácoras, protocolos y reportes de ensayo reales de LIA.
3. Migrar el servicio al Jetson Orin Nano y medir latencia real con GPU.
4. Implementar OCR para soporte de imágenes escaneadas.
5. Realizar pruebas con auditores usando casos reales de auditorías pasadas del laboratorio.

---

## 7. Repositorio y entregables

- **Código fuente:** `github.com/SantiagoSo2425/lia-llm-service`
- **Documentación técnica:** incluida en el repositorio (`/docs`)
- **Informe técnico de hardware:** entregado en sprint anterior

---

*Semillero de investigación — Instituto Tecnológico Metropolitano, 2026.*
