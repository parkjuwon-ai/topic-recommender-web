import type { Metadata } from "next";
import Link from "next/link";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Bookend Topic Lab",
  description: "관심사와 트렌드를 섞어서 글감을 추천해주는 실험용 앱",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko">
      <body
        className={`${geistSans.variable} ${geistMono.variable} bg-slate-950 text-slate-50 antialiased`}
      >
        <div className="min-h-screen flex flex-col">
          {/* 상단 헤더 */}
          <header className="border-b border-slate-800 bg-slate-900/60 backdrop-blur">
            <div className="mx-auto flex w-full max-w-5xl items-center justify-between px-4 py-3">
              {/* 로고 / 서비스명 */}
              <Link href="/" className="flex items-center gap-2">
                <span className="text-sm font-semibold tracking-tight text-slate-50">
                  Bookend Topic Lab
                </span>
              </Link>

              {/* 상단 네비게이션 */}
              <nav className="flex items-center gap-4 text-sm text-slate-300">
                <Link href="/topics" className="hover:text-white">
                  Topics
                </Link>
                <Link href="/sessions" className="hover:text-white">
                  Sessions
                </Link>
              </nav>
            </div>
          </header>

          {/* 메인 컨텐츠 영역 */}
          <main className="mx-auto flex w-full max-w-5xl flex-1 px-4 py-6">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}

