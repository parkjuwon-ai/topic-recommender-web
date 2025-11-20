// src/app/sentencify/login/page.tsx
"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE ?? "http://127.0.0.1:8000";

export default function SentencifyLoginPage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  async function handleGoogleLoginDebug() {
    try {
      setIsLoading(true);
      setErrorMsg(null);

      const resp = await fetch(`${API_BASE}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id_token: "debug" }),
      });

      if (!resp.ok) {
        const text = await resp.text();
        throw new Error(`Failed to fetch: ${resp.status} ${text}`);
      }

      const data = await resp.json();

      if (typeof window !== "undefined") {
        localStorage.setItem("access_token", data.access_token);
      }

      router.push("/topics");
    } catch (err: any) {
      console.error(err);
      setErrorMsg(err?.message ?? "Failed to fetch");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="flex min-h-screen justify-center bg-neutral-200">
      <div className="flex w-full max-w-6xl flex-col px-6 py-6">
        <main className="mt-10 flex flex-1 items-center justify-center">
          <div className="w-full max-w-md rounded-3xl bg-white px-8 py-10 shadow-[0_24px_60px_rgba(15,23,42,0.08)]">
            <h1 className="mb-6 text-center text-lg font-semibold text-slate-300">
              SENTENCIFY 로그인
            </h1>

            <button
              type="button"
              onClick={handleGoogleLoginDebug}
              disabled={isLoading}
              className="mb-3 flex w-full items-center justify-center rounded-full bg-purple-600 py-3 text-sm font-semibold text-white shadow-md shadow-purple-500/40 hover:bg-purple-500 disabled:cursor-not-allowed disabled:bg-slate-400"
            >
              {isLoading
                ? "로그인 중..."
                : "Google 계정으로 계속하기 (debug)"}
            </button>

            {errorMsg && (
              <p className="mt-1 text-center text-xs text-red-500">
                {errorMsg}
              </p>
            )}

            <p className="mt-4 text-center text-[11px] text-slate-400">
              실제 OAuth 붙이기 전까지는 debug용 Google 버튼으로 로그인합니다.
            </p>
          </div>
        </main>
      </div>
    </div>
  );
}

