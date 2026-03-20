import { t, type Static } from "elysia";

/**
 * ID parameter schema with string type ID
 */
export const StringIdParamSchema = t.Object({
  id: t.String(),
});

/**
 * ID parameter schema with number type ID
 */
export const NumberIdParamSchema = t.Object({
  id: t.Number(),
});

export type StringIdParam = Static<typeof StringIdParamSchema>;
export type NumberIdParam = Static<typeof NumberIdParamSchema>;
