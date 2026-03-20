import { createClient } from "@connectrpc/connect";
import { createGrpcTransport } from "@connectrpc/connect-node";
import { PredictionService } from "@/generated/bookscanner/v1/prediction_pb";

const transport = createGrpcTransport({
  baseUrl: process.env.AI_SERVICE_URL!,
});

export const predictionClient = createClient(PredictionService, transport);
