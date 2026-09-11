/** @type {import('next').NextConfig} */
const nextConfig = {
  allowedDevOrigins: [process.env.HOST_IP || 'localhost'],
};

module.exports = nextConfig;