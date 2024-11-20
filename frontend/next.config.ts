const nextConfig = {
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://nginx:80/:path*',
      },
    ];
  },
};

module.exports = nextConfig;
