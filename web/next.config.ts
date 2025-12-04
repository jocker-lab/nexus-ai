import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // API 代理：将 /api/v1/* 请求代理到后端服务
  // 这样前端可以使用相对路径，无需关心后端的实际地址和端口
  async rewrites() {
    // 后端地址：优先使用环境变量，否则使用默认值
    const backendUrl = process.env.API_SERVER_URL || 'http://127.0.0.1:8080'

    return [
      {
        // 匹配所有 /api/v1/* 请求
        source: '/api/v1/:path*',
        // 代理到后端
        destination: `${backendUrl}/api/v1/:path*`,
      },
    ]
  },
};

export default nextConfig;
