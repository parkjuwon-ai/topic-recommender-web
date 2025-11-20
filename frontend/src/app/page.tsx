// src/app/page.tsx
"use client";

import { useRouter } from "next/navigation";

export default function HomePage() {
  const router = useRouter();

  const goSentencify = () => {
    router.push("/sentencify");
  };

  return (
    <div className="flex min-h-screen justify-center">
      <div className="flex w-full max-w-6xl flex-col px-6 py-6">
        {/* 상단 BOOKEND 로고 */}
        <header className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-orange-500">
            <span className="text-xs font-bold text-white">B</span>
          </div>
          <span className="text-lg font-semibold tracking-tight">
            BOOKEND
          </span>
        </header>

        {/* 중앙 카드 */}
        <main className="mt-10 flex flex-1 items-center justify-center">
          <section className="w-full rounded-[32px] bg-white px-10 py-10 shadow-[0_24px_60px_rgba(15,23,42,0.08)]">
            <div className="flex flex-col gap-6">
              {/* 서비스 3개 행 */}
              <div className="grid gap-8 md:grid-cols-3">
                {/* SENTENCIFY 카드 */}
                <button
                  type="button"
                  onClick={goSentencify}
                  className="group flex flex-col items-start gap-2 text-left"
                >
                  <div className="flex items-center gap-2">
                    <div className="flex h-8 w-8 items-center justify-center rounded-full bg-purple-600 text-white">
                      ✶
                    </div>
                    <span className="text-base font-semibold tracking-tight text-slate-900">
                      SENTENCIFY
                    </span>
                  </div>
                  <p className="text-xs text-slate-500">
                    SENTENCIFY: AI 문장 교정 서비스
                    <br />
                    복잡한 문장을 매끄럽게 다듬어줘요.
                  </p>
                  <span className="text-[11px] text-purple-500 group-hover:underline">
                    바로가기 →
                  </span>
                </button>

                {/* BOOKEND 카드 */}
                <div className="flex flex-col items-start gap-2">
                  <div className="flex items-center gap-2">
                    <div className="h-8 w-8 rounded-full bg-orange-500" />
                    <span className="text-base font-semibold tracking-tight text-slate-900">
                      BOOKEND
                    </span>
                  </div>
                  <p className="text-xs text-slate-500">
                    BOOKEND: 지식을 입체적으로 정리하고
                    <br />
                    작가처럼 집필하는 D2C 출판실.
                  </p>
                  <span className="text-[11px] text-slate-400">
                    곧 만나볼 수 있어요
                  </span>
                </div>

                {/* MUNCH 카드 */}
                <div className="flex flex-col items-start gap-2">
                  <div className="flex items-center gap-2">
                    <span className="text-xl font-extrabold tracking-tight">
                      MUNCH
                    </span>
                    <span className="text-[10px] tracking-widest text-slate-500">
                      PRESS
                    </span>
                  </div>
                  <p className="text-xs text-slate-500">
                    MUNCH PRESS: 유튜브의 압축된 콘텐츠를
                    <br />
                    더 깊게 읽어가는 아카이브.
                  </p>
                  <span className="text-[11px] text-slate-400">
                    자세히 알아보기 (준비중)
                  </span>
                </div>
              </div>

              {/* 가운데 로그인 버튼 */}
              <div className="flex justify-center">
                <button
                  type="button"
                  onClick={goSentencify}
                  className="rounded-full bg-orange-500 px-8 py-2 text-sm font-semibold text-white shadow-md shadow-orange-500/40 transition hover:bg-orange-400"
                >
                  로그인
                </button>
              </div>
            </div>
          </section>
        </main>
      </div>
    </div>
  );
}

