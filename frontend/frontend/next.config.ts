import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  // Promoted from `experimental` to stable in Next.js 16.
  typedRoutes: true,
};

export default nextConfig;
