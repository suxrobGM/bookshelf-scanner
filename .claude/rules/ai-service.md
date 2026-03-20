# AI Service Rules (apps/ai-service)

Applies when working in `apps/ai-service/`.

## Structure

- **`src/server.py`** — gRPC server setup.
- **`src/servicer.py`** — `PredictionServicer` implementing the gRPC service.
- **`src/bookscanner_ai/`** — Core ML logic (predict.py, utils/).
- **`src/generated/`** — Auto-generated protobuf Python code. Never edit manually.

## Conventions

- Use PDM as the package manager (`pdm install`, `pdm add`).
- Python 3.14. Follow standard Python conventions (snake_case, type hints).
- ML models are lazy-loaded in the servicer `__init__`.
- gRPC responses are streamed (server-streaming RPC).
- Clean up temp files after processing.

## Protobuf

- Proto definitions live in `proto/bookscanner/v1/`.
- Regenerate with `bun run proto:generate` from the repo root.
- Never edit files in `src/generated/`.
