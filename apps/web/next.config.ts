import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: 'standalone', // Required for Docker deployment
  experimental: {
    turbo: {
      enabled: false, // Disable Turbopack for build (use Webpack)
    },
  },
  /* config options here */
};

export default nextConfig;
