// src/app/sentencify/page.tsx
// src/app/sentencify/page.tsx
"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";

export default function SentencifyPage() {
  const router = useRouter();

  const goLogin = () => {
    router.push("/sentencify/login");
  };

  return (
    <div className="flex min-h-screen justify-center">
      <div className="flex w-full max-w-6xl flex-col px-6 py-6">
        {/* 상단 바 */}
        <header className="flex items-center justify-between">
          {/* 왼쪽: SENTENCIFY 로고 */}
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-purple-600 text-white">
              ✶
            </div>
            <span className="text-base font-semibold tracking-tight">
              SENTENCIFY
            </span>
          </div>

          {/* 중앙: 네비게이션 */}
          <nav className="hidden items-center gap-6 text-sm text-slate-700 md:flex">
            <button className="text-sm font-medium text-slate-900">
              에디터
            </button>
            <button className="text-sm text-slate-600">튜토리얼</button>
            <button className="text-sm text-slate-600">다운로드</button>
            <Link
              href="/topics"
              className="rounded-full border border-purple-200 bg-purple-50 px-3 py-1 text-[11px] font-medium text-purple-600"
            >
              글감 추천 실험실
            </Link>
          </nav>

          {/* 오른쪽: 언어, FAQ, 로그인 */}
          <div className="flex items-center gap-3">
            <button className="hidden items-center gap-1 text-xs text-slate-600 md:flex">
              🌐 <span>KO</span>
            </button>
            <button className="hidden text-xs text-slate-600 md:inline">
              FAQ
            </button>
            <div className="hidden rounded-lg border border-slate-300 bg-white px-2 py-1 text-[10px] text-slate-600 md:block">
              Chrome Web Store
            </div>
            <button
              onClick={goLogin}
              className="rounded-full bg-orange-500 px-4 py-1.5 text-xs font-semibold text-white shadow-md shadow-orange-500/30 hover:bg-orange-400"
            >
              로그인
            </button>
          </div>
        </header>

        {/* 중앙 콘텐츠 카드 (BOOKEND / SENTENCIFY / MUNCH 소개) */}
        <main className="mt-10 flex flex-1 items-start justify-center">
          <section className="w-full rounded-[32px] bg-white px-10 py-10 shadow-[0_24px_60px_rgba(15,23,42,0.08)]">
            <div className="flex flex-col gap-6">
              <div className="grid gap-8 md:grid-cols-3">
                {/* SENTENCIFY 소개 */}
                <div className="flex flex-col items-start gap-2">
                  <div className="flex items-center gap-2">
                    <div className="flex h-8 w-8 items-center justify-center rounded-full bg-purple-600 text-white">
                      ✶
                    </div>
                    <span className="text-base font-semibold tracking-tight text-slate-900">
                      SENTENCIFY
                    </span>
                  </div>
                  <p className="text-xs text-slate-500">
                    SENTENCIFY: AI 기반 문장 교정 서비스.
                    <br />
                    논문, 이메일, 블로그까지 매끄럽게 다듬어줘요.
                  </p>
                  <span className="text-[11px] text-purple-500">
                    크롬 확장 프로그램으로 바로 사용 가능
                  </span>
                </div>

                {/* BOOKEND 소개 */}
                <div className="flex flex-col items-start gap-2">
                  <div className="flex items-center gap-2">
                    <div className="h-8 w-8 rounded-full bg-orange-500" />
                    <span className="text-base font-semibold tracking-tight text-slate-900">
                      BOOKEND
                    </span>
                  </div>
                  <p className="text-xs text-slate-500">
                    BOOKEND: 관심사를 기반으로 트렌드와 자료를 모아
                    <br />
                    글감과 출판 기회를 연결하는 플랫폼.
                  </p>
                  <span className="text-[11px] text-slate-400">
                    곧 연동 예정
                  </span>
                </div>

                {/* MUNCH 소개 */}
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
                    MUNCH PRESS: 영상 콘텐츠의 핵심을
                    <br />
                    텍스트로 다시 곱씹는 실험 공간.
                  </p>
                  <span className="text-[11px] text-slate-400">
                    자세히 보기 (준비중)
                  </span>
                </div>
              </div>

              <div className="mt-2 text-[11px] text-slate-500">
                * 우측 상단 <span className="font-medium">로그인</span> 버튼을
                눌러 SENTENCIFY 계정으로 로그인할 수 있어요.
              </div>
            </div>
          </section>
        </main>
      </div>
    </div>
  );
}

