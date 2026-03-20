import { swagger } from "@elysiajs/swagger";
import { Elysia } from "elysia";

/**
 * Elysia plugin for Swagger/OpenAPI documentation.
 */
export const swaggerPlugin = new Elysia({ name: "swagger" }).use(
  swagger({
    documentation: {
      info: {
        title: "Bookscanner API",
        version: "1.0.0",
      },
    },
  }),
);
