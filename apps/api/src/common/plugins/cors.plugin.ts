import { cors } from "@elysiajs/cors";
import { Elysia } from "elysia";

/**
 * Elysia plugin for CORS configuration.
 */
export const corsPlugin = new Elysia({ name: "cors" }).use(
  cors({
    origin: process.env.CORS_ORIGINS?.split(",") ?? ["http://localhost:4001"],
    methods: ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    credentials: true,
  }),
);
