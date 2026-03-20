import { createApiClient } from "@bookscanner/shared";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:4000";
export const client = createApiClient(API_URL);
