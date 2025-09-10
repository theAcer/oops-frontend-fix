/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  images: {
    unoptimized: true,
  },

  // Force Next.js to skip LightningCSS (native binding) and use PostCSS instead
  experimental: {
    optimizeCss: false,
  },

  async rewrites() {
    const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000';
    console.log(`[Next.js Config] Using backend URL for rewrites: ${backendUrl}`); // Added log
    return [
      {
        source: '/api/:path*',
        destination: `${backendUrl}/api/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;