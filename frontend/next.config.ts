import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://api:8000/:path*' // Proxy to FastAPI
      }
    ]
  }
};

export default nextConfig;