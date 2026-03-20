# Bookshelf Scanner

AI-powered book spine recognition app. Upload a bookshelf photo, get back segmented spines and extracted text.

## Architecture

Bun monorepo with Turborepo orchestration:

- **apps/web** — Next.js 16 (App Router) + MUI v7 + Emotion. Port 4002.
- **apps/api** — Elysia.js gateway with tsyringe DI. Port 4000. Talks to AI service via Connect (gRPC-web).
- **apps/ai-service** — Python gRPC server (YOLO 11x + OpenCV). Port 4001. Managed with PDM.
- **packages/shared** — Eden Treaty API client factory + shared types.
- **proto/** — Protobuf definitions. Generate with `bun run proto:generate` (Buf v2).

Data flow: Web → POST multipart → API (Elysia) → Connect stream → AI Service → stream back as NDJSON.

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
pdm run serve            # start gRPC server
```

## Code Style

- Prettier handles formatting (100 char width, double quotes, trailing commas, LF line endings, sorted imports).
- Auto-formatted on Edit/Write via Claude hook — no manual formatting needed.
- See `.claude/rules/` for detailed conventions.
