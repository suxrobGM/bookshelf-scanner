import type { ApiClient } from "@bookscanner/shared";

/** Eden-inferred predict endpoint group */
export type PredictApi = ApiClient["api"]["predict"];

/** Request body for POST /api/predict */
export type PredictBody = Parameters<PredictApi["post"]>[0];
