import { treaty } from "@elysiajs/eden";
import type { App } from "@bookscanner/api"

export function createApiClient(
  baseUrl: string,
  options?: NonNullable<Parameters<typeof treaty<App>>[1]>,
) {
  return treaty<App>(baseUrl, options);
}

export type ApiClient = ReturnType<typeof createApiClient>;
