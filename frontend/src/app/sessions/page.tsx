// src/app/sessions/page.tsx
export default function SessionsPage() {
  return (
    <div className="body-card w-full space-y-4">
      <h1 className="text-lg font-semibold">내 세션 목록 (임시)</h1>
      <p className="text-sm text-slate-300">
        백엔드의 <code>/sessions/me</code> 응답을 여기 테이블/카드로 깔끔하게
        보여줄 예정입니다.
      </p>
      <ul className="list-disc pl-5 text-sm text-slate-400">
        <li>선택한 topic 제목</li>
        <li>input_keyword / use_trend / selected_format</li>
        <li>created_at (언제 시작한 세션인지)</li>
      </ul>
    </div>
  );
}

