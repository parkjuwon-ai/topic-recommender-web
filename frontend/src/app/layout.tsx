// src/app/layout.tsx
import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "BOOKEND",
  description: "BOOKEND · SENTENCIFY · MUNCH 허브",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ko">
      <body className="min-h-screen bg-neutral-200 text-slate-900">
        {children}
      </body>
    </html>
  );
}

