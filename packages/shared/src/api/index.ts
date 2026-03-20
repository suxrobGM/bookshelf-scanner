import type { App } from "@bookscanner/api";
import { treaty, type Treaty } from "@elysiajs/eden";

export type ApiClient = Treaty.Create<App>;
type ApiClientOptions = NonNullable<Parameters<typeof treaty>[1]>;

export function createApiClient(baseUrl: string, options?: ApiClientOptions): ApiClient {
  return treaty<App>(baseUrl, options);
}
