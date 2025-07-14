import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  eslint: {
    // Disable ESLint during builds
    ignoreDuringBuilds: true,
  },
  typescript: {
    // Disable TypeScript errors during builds (since we already checked with tsc)
    ignoreBuildErrors: false,
  },
  // Configure for Railway deployment
  output: 'standalone',
  // Allow API proxy to AgentX backend
  async rewrites() {
    return [
      {
        source: '/api/agentx/:path*',
        destination: `${process.env.AGENTX_API_URL || 'http://localhost:8000'}/:path*`,
      },
    ]
  },
  // Environment variables that can be used in the browser
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || '/api/agentx',
  },
};

export default nextConfig;