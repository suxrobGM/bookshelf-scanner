import { t, type Static, type TSchema } from "elysia";

/**
 * Error response schema for API error responses
 */
export const ErrorResponseSchema = t.Object({
  code: t.Number(),
  message: t.String(),
  details: t.Optional(t.Unknown()),
});

/**
 * Pagination info schema
 */
export const PaginationSchema = t.Object({
  /** Current page number, starting from 1 */
  page: t.Number(),
  /** Number of items per page */
  limit: t.Number(),
  /** Total number of items */
  total: t.Number(),
  /** Total number of pages */
  totalPages: t.Number(),
});

/**
 * Creates a paginated response schema with items array and pagination info
 */
export const PaginatedResponseSchema = <T extends TSchema>(itemSchema: T) =>
  t.Object({
    items: t.Array(itemSchema),
    pagination: PaginationSchema,
  });

/**
 * Generic message response for operations that don't return data
 */
export const MessageResponseSchema = t.Object({
  message: t.String(),
});

/**
 * Common response types and error presets for API routes
 */
export const HttpErrorResponses = {
  400: t.Object(
    { code: t.Number(), message: t.String(), details: t.Optional(t.Unknown()) },
    { description: "Bad Request" },
  ),
  401: t.Object(
    { code: t.Number(), message: t.String(), details: t.Optional(t.Unknown()) },
    { description: "Unauthorized" },
  ),
  403: t.Object(
    { code: t.Number(), message: t.String(), details: t.Optional(t.Unknown()) },
    { description: "Forbidden" },
  ),
  404: t.Object(
    { code: t.Number(), message: t.String(), details: t.Optional(t.Unknown()) },
    { description: "Not Found" },
  ),
  409: t.Object(
    { code: t.Number(), message: t.String(), details: t.Optional(t.Unknown()) },
    { description: "Conflict" },
  ),
};

export const GoneErrorSchema = {
  410: t.Object(
    { code: t.Number(), message: t.String(), details: t.Optional(t.Unknown()) },
    { description: "Gone" },
  ),
};

export const TooManyRequestsErrorSchema = {
  429: t.Object(
    { code: t.Number(), message: t.String(), details: t.Optional(t.Unknown()) },
    { description: "Too Many Requests" },
  ),
};

export type ErrorResponse = Static<typeof ErrorResponseSchema>;
export type MessageResponse = Static<typeof MessageResponseSchema>;
export type Pagination = Static<typeof PaginationSchema>;

const _PaginatedSchemaForType = PaginatedResponseSchema(t.Unknown());
export type PaginatedResponse<T> = Omit<Static<typeof _PaginatedSchemaForType>, "items"> & {
  items: T[];
};
