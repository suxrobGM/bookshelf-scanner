# Web Rules (apps/web)

Applies when working in `apps/web/`.

## Structure

- **`app/`** — Next.js App Router pages and layouts.
- **`components/`** — React components.
- **`hooks/`** — Custom React hooks.
- **`lib/`** — Utilities (API client init, helpers).
- **`types/`** — TypeScript type definitions.
- **`theme.ts`** — MUI theme configuration.

## Conventions

- Use MUI v7 components for all UI — no raw HTML elements for things MUI provides (Button, TextField, Box, etc.).
- Use Emotion for custom styling via MUI's `sx` prop or `styled()`.
- Use the Eden Treaty client from `lib/api.ts` for type-safe API calls.
- Use App Router conventions: `page.tsx` for routes, `layout.tsx` for layouts, `"use client"` directive for client components.
- React 19 — prefer server components by default; add `"use client"` only when needed (hooks, event handlers, browser APIs).

## Streaming

- Use `ReadableStream` reader to consume NDJSON streams from the API.
- Parse each line as a separate JSON object.

## React Component Guidelines

- Use named exports instead of default exports for React components.
- Keep components focused and reusable — if a component grows too large, look for opportunities to extract smaller subcomponents.
- Use TypeScript interfaces for component props, and prefer `interface` over `type` for object shapes.
- Always declare the return type of React components as `ReactElement` for better type safety.
- Use `props` to declare component props and use property deconstruction in the body at the top level for better readability.
- Avoid deconstructing props in the function signature to keep it clean and focused on the component's purpose.
