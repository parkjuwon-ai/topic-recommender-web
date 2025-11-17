// src/app/topics/[id]/page.tsx
import Link from "next/link";

type Props = {
  params: { id: string };
};

export default function TopicDetailPage({ params }: Props) {
  const { id } = params;

  return (
    <div className="body-card w-full space-y-4">
      <p className="text-xs text-slate-400 font-mono">topic_id: {id}</p>
      <h1 className="text-lg font-semibold">
        (임시) 선택한 글감 상세 페이지
      </h1>
      <p className="text-sm text-slate-300">
        나중에 여기서 <code>/topics/recommend</code>에서 받은 토픽의{" "}
        <strong>title/description/trend_score</strong>를 보여주고,
        &quot;이 주제로 세션 시작하기&quot; 버튼을 눌러{" "}
        <code>/sessions</code>로 POST 할 거야.
      </p>

      <div className="flex gap-3">
        <button className="btn-primary" disabled>
          이 주제로 세션 만들기 (예정)
        </button>
        <Link
          href="/topics"
          className="inline-flex items-center rounded-full border border-slate-700 px-4 py-2 text-xs text-slate-300 hover:bg-slate-800"
        >
          목록으로
        </Link>
      </div>
    </div>
  );
}

