import type { Metadata, Viewport } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Nexus AI | Neural Intelligence Platform",
  description: "Advanced multi-agent AI system for research analysis and intelligent report generation. Powered by cutting-edge neural networks.",
  keywords: ["AI", "Neural Network", "Research", "Analysis", "Multi-Agent", "Report Generation"],
  authors: [{ name: "Nexus AI Team" }],
  openGraph: {
    title: "Nexus AI | Neural Intelligence Platform",
    description: "Advanced multi-agent AI system for research analysis and intelligent report generation.",
    type: "website",
  },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  themeColor: "#06b6d4",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN" suppressHydrationWarning className="dark">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;800;900&family=Exo+2:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="antialiased min-h-screen">
        {/* Animated Background Elements */}
        <div className="fixed inset-0 pointer-events-none overflow-hidden -z-10" aria-hidden="true">
          {/* Neural Orbs */}
          <div
            className="absolute w-[600px] h-[600px] rounded-full opacity-30 blur-[100px] animate-float"
            style={{
              background: 'radial-gradient(circle, rgba(6, 182, 212, 0.4) 0%, transparent 70%)',
              top: '-10%',
              left: '-10%',
            }}
          />
          <div
            className="absolute w-[500px] h-[500px] rounded-full opacity-20 blur-[80px] animate-float"
            style={{
              background: 'radial-gradient(circle, rgba(139, 92, 246, 0.4) 0%, transparent 70%)',
              bottom: '-15%',
              right: '-5%',
              animationDelay: '2s',
            }}
          />
          <div
            className="absolute w-[400px] h-[400px] rounded-full opacity-15 blur-[60px] animate-float"
            style={{
              background: 'radial-gradient(circle, rgba(59, 130, 246, 0.35) 0%, transparent 70%)',
              top: '40%',
              right: '20%',
              animationDelay: '4s',
            }}
          />

          {/* Scan Line Effect */}
          <div
            className="absolute w-full h-[2px] opacity-5"
            style={{
              background: 'linear-gradient(90deg, transparent, rgba(6, 182, 212, 0.8), transparent)',
              animation: 'scan-line 8s linear infinite',
            }}
          />
        </div>

        {/* Main Content */}
        <main className="relative z-0">
          {children}
        </main>
      </body>
    </html>
  );
}
