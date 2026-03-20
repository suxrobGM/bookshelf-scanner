import type { PropsWithChildren, ReactElement } from "react";
import { CssBaseline } from "@mui/material";
import { AppRouterCacheProvider } from "@mui/material-nextjs/v16-appRouter";
import { ThemeProvider } from "@mui/material/styles";
import type { Metadata } from "next";
import theme from "@/theme";

export const metadata: Metadata = {
  title: "Bookshelf Scanner",
  description: "Upload a bookshelf image to detect and recognize book titles using AI",
};

export default function RootLayout(props: PropsWithChildren): ReactElement {
  const { children } = props;
  return (
    <html lang="en">
      <body>
        <AppRouterCacheProvider>
          <ThemeProvider theme={theme}>
            <CssBaseline />
            {children}
          </ThemeProvider>
        </AppRouterCacheProvider>
      </body>
    </html>
  );
}
