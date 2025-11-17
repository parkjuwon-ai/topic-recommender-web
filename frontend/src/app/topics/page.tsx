// src/app/topics/page.tsx
import Link from "next/link";

const MOCK_TOPICS = [
  {
    id: "temp-1",
    title: "백과/상식/퀴즈 × 추천 시스템 프로젝트 회고 돌아보기",
    trendScore: 38,
    finalScore: 0.69,
  },
  {
    id: "temp-2",
    title: "목표 설정/OKR/버킷리스트 × 2025년 학습 회고",
    trendScore: 45,
    finalScore: 0.72,
  },
];

export default function TopicsPage() {
  return (
    <div className="w-full space-y-4">
      <h1 className="text-lg font-semibold">오늘의 글감 추천 (임시)</h1>
      <p className="text-sm text-slate-300">
        지금은 목업 데이터입니다. 나중에 백엔드의{" "}
        <code>/topics/recommend</code> 응답을 그대로 붙일 예정이에요.
      </p>

      <div className="space-y-3">
        {MOCK_TOPICS.map((t) => (
          <Link
            key={t.id}
            href={`/topics/${t.id}`}
            className="block body-card hover:border-sky-500/70"
          >
            <div className="flex items-start justify-between gap-4">
              <div>
                <h2 className="text-sm font-medium text-slate-50">
                  {t.title}
                </h2>
                <p className="mt-1 text-xs text-slate-400">
                  트렌드 지수: {t.trendScore} / 100 · 최종 점수:{" "}
                  {t.finalScore.toFixed(2)}
                </p>
              </div>
              <span className="rounded-full bg-sky-500/10 px-3 py-1 text-xs text-sky-400">
                추천 보기
              </span>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}

