# API Rules (apps/api)

Applies when working in `apps/api/`.

## Structure

- **`common/`** — Cross-cutting: DI container, errors, logger, middleware, plugins, services.
- **`modules/<feature>/`** — Feature domains. Each module has: `controller.ts`, `service.ts`, `schema.ts`, `index.ts` (barrel).
- **`types/`** — Shared request/response types and pagination.
- **`generated/`** — Auto-generated protobuf code. Never edit manually.

## Conventions

- Use Elysia plugins for reusable functionality (CORS, Swagger, auth, etc.).
- Use Typebox schemas for request/response validation — these also power Swagger docs.
- Register services in the tsyringe DI container (`common/di/container.ts`).
- Use the custom error classes from `common/errors/` (BadRequestError, NotFoundError, etc.) — the global error middleware handles them.
- Use the Pino logger from `common/logger/` — never `console.log`.

## Streaming

- Use `ReadableStream` to stream responses from gRPC back to the client.
- Stream format is NDJSON (newline-delimited JSON).

## Adding a New Module

1. Create `modules/<name>/` with controller, service, schema, and barrel index.
2. Register any new services in the DI container.
3. Mount the controller in `app.ts` inside the `/api` group.
