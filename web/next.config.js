/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',

  // Note: API proxying is now handled by /src/app/api/v1/[...path]/route.ts
  // This works in both development and production standalone mode
};

module.exports = nextConfig;
