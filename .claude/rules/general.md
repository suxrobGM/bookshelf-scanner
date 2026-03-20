# General Rules

## Commands


## Comments

- Don't add inline comments that restate what the code already says. Only comment to explain **why**, not **what**. If the code needs a comment to explain what it does, rename the variable or extract a function instead.
- Add brief JSDoc (`/** ... */`) for public functions — one-liner description is enough. Skip `@param` / `@returns` when types already convey the meaning.

## File Size Guideline

Aim for ~300–350 LOC per file as a soft ceiling. If a service or controller grows past this, look for extraction opportunities (repository, helper, or splitting the module). Schema and repository files are naturally shorter.
