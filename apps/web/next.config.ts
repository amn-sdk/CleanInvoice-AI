import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: 'standalone', // Required for Docker deployment
  experimental: {
    // @ts-ignore - Temporarily disable Turbopack for build stability
    webpackBuildWorker: true,
  },
  /* config options here */
};

export default nextConfig;
