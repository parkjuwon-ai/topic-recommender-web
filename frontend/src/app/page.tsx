// src/app/page.tsx
import Link from "next/link";

export default function HomePage() {
  return (
    <div className="body-card flex w-full flex-col gap-4">
      <h1 className="text-xl font-semibold tracking-tight text-slate-50">
        오늘은 어떤 글을 써볼까요?
      </h1>
      <p className="text-sm text-slate-300">
        관심사 + 트렌드를 섞어서 글감을 추천해주는 북엔드 토픽 루프입니다.
      </p>

      <div className="mt-2 flex flex-wrap gap-3 text-sm">
        <Link href="/topics" className="btn-primary">
          글감 추천 보러가기
        </Link>
        <Link
          href="/sessions"
          className="inline-flex items-center justify-center rounded-full border border-slate-600 px-4 py-2 text-sm text-slate-200 hover:bg-slate-800"
        >
          내가 고른 글감 보기
        </Link>
      </div>
    </div>
  );
}

