import { Value } from "@sinclair/typebox/value";
import { t, type Static } from "elysia";

const EnvSchema = t.Object({
  AI_SERVICE_URL: t.Optional(t.String({ default: "http://localhost:4001" })),
  PORT: t.Optional(t.String({ default: "4000" })),
  NODE_ENV: t.Optional(
    t.Union([t.Literal("development"), t.Literal("production"), t.Literal("staging")]),
  ),
  LOG_LEVEL: t.Optional(t.String({ default: "info" })),
});

export type Env = Static<typeof EnvSchema>;

declare global {
  namespace NodeJS {
    interface ProcessEnv extends Env {}
  }
}

/**
 * Validates environment variables against the defined schema.
 * Throws an error if validation fails, preventing the application from starting with invalid configuration.
 */
export function validateEnv(): void {
  const converted = Value.Convert(EnvSchema, { ...process.env });
  const defaults = Value.Default(EnvSchema, converted);
  const errors = [...Value.Errors(EnvSchema, defaults)];

  if (errors.length) {
    const messages = errors.map((e) => `  ${e.path.slice(1)}: ${e.message}`).join("\n");
    throw new Error(`Environment validation failed:\n${messages}`);
  }
}
