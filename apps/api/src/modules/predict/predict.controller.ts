import { Elysia, t } from "elysia";
import { predictionClient } from "@/common/services/grpc-client";

export const predictController = new Elysia({ prefix: "/predict" }).post(
  async ({ body }) => {
    const file = body.file;
    const imageBuffer = new Uint8Array(await file.arrayBuffer());

    const stream = new ReadableStream({
      async start(controller) {
        const encoder = new TextEncoder();

        try {
          for await (const response of predictionClient.predict({
            imageData: imageBuffer,
            filename: file.name,
          })) {
            let result: { success: boolean; data?: string; error?: string };

            if (response.result.case === "segmentation") {
              // Convert raw bytes to base64 data URL
              const b64 = Buffer.from(
                response.result.value.segmentedImage,
              ).toString("base64");
              result = {
                success: true,
                data: `data:image/png;base64,${b64}`,
              };
            } else if (response.result.case === "book") {
              result = { success: true, data: response.result.value.rawText };
            } else if (response.result.case === "error") {
              result = {
                success: false,
                error: response.result.value.message,
              };
            } else {
              continue;
            }

            controller.enqueue(
              encoder.encode(JSON.stringify(result) + "\n"),
            );
          }
        } catch (err) {
          const errResult = {
            success: false,
            error: err instanceof Error ? err.message : String(err),
          };
          controller.enqueue(
            encoder.encode(JSON.stringify(errResult) + "\n"),
          );
        } finally {
          controller.close();
        }
      },
    });

    return new Response(stream, {
      headers: { "Content-Type": "application/json" },
    });
  },
  {
    body: t.Object({
      file: t.File(),
    }),
  },
);
