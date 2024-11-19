import {ApplicationConfig, provideExperimentalZonelessChangeDetection} from "@angular/core";
import {provideHttpClient} from "@angular/common/http";
import {provideRouter} from "@angular/router";
import {routes} from "./app.routes";

export const appConfig: ApplicationConfig = {
  providers: [provideRouter(routes), provideHttpClient(), provideExperimentalZonelessChangeDetection()],
};
