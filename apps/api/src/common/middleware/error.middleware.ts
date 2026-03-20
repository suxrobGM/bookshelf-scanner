import { Elysia } from "elysia";
import { HttpError } from "@/common/errors";
import { logger } from "@/common/logger";
import type { ErrorResponse } from "@/types/response";

const isProduction = process.env.NODE_ENV === "production";

function createErrorResponse(code: number, message: string, details?: unknown): ErrorResponse {
  return details !== undefined ? { code, message, details } : { code, message };
}

function getRouteInfo(request: Request): { method: string; path: string } {
  const url = new URL(request.url);
  return { method: request.method, path: url.pathname };
}

/**
 * Global error handling plugin.
 * Catches unhandled errors and returns consistent JSON error responses.
 */
export const errorMiddleware = new Elysia({ name: "error-handler" }).onError(
  { as: "global" },
  ({ code, error, set, request }) => {
    const route = getRouteInfo(request);

    if (error instanceof HttpError) {
      set.status = error.statusCode;
      logger.warn({ statusCode: error.statusCode, message: error.message, ...route }, "HTTP error");
      return createErrorResponse(error.statusCode, error.message);
    }

    switch (code) {
      case "VALIDATION":
        set.status = 400;
        logger.warn({ statusCode: 400, ...route, message: error.message }, "Validation error");
        return createErrorResponse(400, "Validation error", error.message);
      case "PARSE":
        set.status = 400;
        logger.warn({ statusCode: 400, ...route }, "Malformed request body");
        return createErrorResponse(400, "Malformed request body");
      case "NOT_FOUND":
        set.status = 404;
        return createErrorResponse(404, "Not found");
      default: {
        const errorMessage = error instanceof Error ? error.message : String(error);

        logger.error(
          {
            code,
            message: errorMessage,
            ...route,
            ...(isProduction ? {} : { stack: (error as Error).stack }),
          },
          "Unhandled error",
        );

        set.status = 500;
        return createErrorResponse(500, "Internal server error");
      }
    }
  },
);
