import { Elysia } from "elysia";
import { container } from "@/common/di/container";
import { PredictBodySchema } from "./predict.schema";
import { PredictService } from "./predict.service";

const predictService = container.resolve(PredictService);

export const predictController = new Elysia({ prefix: "/predict", tags: ["Prediction"] }).post(
  "/",
  async ({ body }) => {
    const imageBuffer = new Uint8Array(await body.file.arrayBuffer());
    const stream = predictService.createStream(imageBuffer, body.file.name);

    return new Response(stream, {
      headers: { "Content-Type": "application/x-ndjson" },
    });
  },
  {
    body: PredictBodySchema,
    detail: {
      summary: "Predict books from bookshelf image",
      description:
        "Upload a bookshelf image to segment individual books and recognize their titles. " +
        "Returns a newline-delimited JSON stream: first chunk is the segmented image (base64), " +
        "followed by one chunk per recognized book.",
    },
  },
);
