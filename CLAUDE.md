# Bookshelf Scanner

AI-powered book spine recognition app. Upload a bookshelf photo, get back segmented spines and extracted text.

## Architecture

Bun monorepo with Turborepo orchestration:

- **llama-server** — Gemma 3 4B vision inference via llama.cpp CLI. Port 4000.
- **apps/ai-service** — Python gRPC server (YOLO 26x + OpenCV). Port 4001. Managed with PDM. Calls llama-server for OCR. Models and dataset stored under `apps/ai-service/models/` and `apps/ai-service/dataset/`.
- **apps/api** — Elysia.js gateway with tsyringe DI. Port 4002. Talks to AI service via Connect (gRPC-web).
- **apps/web** — Next.js 16 (App Router) + MUI v7 + Emotion. Port 4003.
- **packages/shared** — Eden Treaty API client factory + shared types.
- **proto/** — Protobuf definitions. Generate with `bun run proto:generate` (Buf v2).

Data flow: Web (4003) → POST multipart → API (4002) → Connect stream → AI Service (4001) → llama-server (4000) → stream back as NDJSON.

## Commands

```bash
bun install              # install all workspace deps
bun run dev              # start web + api via turbo
bun run dev:all          # start all three services (includes ai-service via pdm)
bun run dev:web          # start web only
bun run dev:api          # start api only
bun run dev:ai           # start ai-service only (pdm run serve)
bun run build            # build all
bun run proto:generate   # regenerate protobuf code (buf generate)
```

AI service (from `apps/ai-service/`):

```bash
pdm install              # install Python deps
pdm run llama-server     # start llama-server on port 4000
pdm run serve            # start gRPC server on port 4001
```

## Code Style

- Prettier handles formatting (100 char width, double quotes, trailing commas, LF line endings, sorted imports).
- Auto-formatted on Edit/Write via Claude hook — no manual formatting needed.
- See `.claude/rules/` for detailed conventions.
