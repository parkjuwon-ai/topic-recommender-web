// src/app/login/page.tsx
export default function LoginPage() {
  return (
    <div className="body-card w-full">
      <h1 className="text-lg font-semibold mb-3">로그인 (임시)</h1>
      <p className="text-sm text-slate-300 mb-4">
        여기에는 나중에 북엔드/구글 로그인 버튼이 들어갑니다.
      </p>
      <button className="btn-primary" disabled>
        Google로 로그인 (예정)
      </button>
    </div>
  );
}

