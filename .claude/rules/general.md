# General Rules

## Commands

- Use `bun` as the package manager — never `npm` or `yarn`.
- Use `bunx` instead of `npx` for running CLI tools.
- Run tasks through Turborepo when available (`bun run dev`, `bun run build`, `bun run typecheck`).

## TypeScript

- Strict mode is on everywhere — never use `any` or `as` casts unless truly unavoidable.
- Use path aliases (`@/...`) for intra-app imports; use `workspace:*` for cross-package imports.
- Prefer `interface` for object shapes, `type` for unions/intersections.

## Comments

- Don't add inline comments that restate what the code already says. Only comment to explain **why**, not **what**. If the code needs a comment to explain what it does, rename the variable or extract a function instead.
- Add brief JSDoc (`/** ... */`) for public functions — one-liner description is enough. Skip `@param` / `@returns` when types already convey the meaning.

## File Size Guideline

Aim for ~300-350 LOC per file as a soft ceiling. If a service or controller grows past this, look for extraction opportunities (repository, helper, or splitting the module). Schema and repository files are naturally shorter.

## Formatting

Prettier is configured and runs automatically via a Claude hook on Edit/Write. Do not manually format code. Key settings: 100 char width, double quotes, trailing commas, LF endings, sorted imports.
