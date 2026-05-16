/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  // Add empty turbopack config to avoid Turbopack vs webpack conflict
  turbopack: {},
  webpack: (config, { dev }) => {
    if (dev) {
      config.cache = false;
    }
    return config;
  },
};

export default nextConfig;
