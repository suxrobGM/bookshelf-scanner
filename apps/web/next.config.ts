import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  cacheComponents: true,
  reactCompiler: true,
  typedRoutes: true,
  transpilePackages: ["@bookscanner/shared"],
};

export default nextConfig;
