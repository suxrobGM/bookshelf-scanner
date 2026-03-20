import { t } from "elysia";

export const PredictBodySchema = t.Object({
  file: t.File({
    type: ["image/jpeg", "image/png", "image/webp"],
    maxSize: "10m",
  }),
});
