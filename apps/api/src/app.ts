import "dotenv/config";
import "@/common/di/container";
import { Elysia } from "elysia";
import { predictController } from "@/modules/predict";
import { validateEnv } from "./env";
import { HttpErrorResponses } from "@/types/response";
import { logger } from "@/common/logger";
import { corsPlugin, swaggerPlugin } from "@/common/plugins";

validateEnv();

export const app = new Elysia()
  .use(corsPlugin)
  .use(swaggerPlugin)
  .get("/health", () => ({ status: "ok", timestamp: new Date().toISOString() }))
  .group("/api", (api) =>
    api
      .guard({
        response: HttpErrorResponses,
      })
      .use(predictController)
    )
  .listen(parseInt(process.env.PORT!));;

logger.info(`Bookscanner API running at http://${app.server?.hostname}:${app.server?.port}`);

if (process.env.NODE_ENV === "development") {
  logger.info(
    `Swagger docs available at http://${app.server?.hostname}:${app.server?.port}/swagger`,
  );
}

// Export app type for Eden Treaty
export type App = typeof app;
