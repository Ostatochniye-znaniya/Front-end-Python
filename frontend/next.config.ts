/** @type {import('next').NextConfig} */
const nextConfig = {
    // Добавляем базовый путь
  basePath: '/csh',

  // Если нужно, чтобы статика тоже была с префиксом
  assetPrefix: '/csh',

  reactStrictMode: true,
  swcMinify: true,

  // Для продакшена
  output: 'standalone',
}

module.exports = nextConfig