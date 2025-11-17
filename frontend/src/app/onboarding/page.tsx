// src/app/onboarding/page.tsx
"use client";

import { useState } from "react";

export default function OnboardingPage() {
  const [trendWeight, setTrendWeight] = useState(50);

  return (
    <div className="body-card w-full space-y-5">
      <h1 className="text-lg font-semibold">온보딩 (임시)</h1>
      <p className="text-sm text-slate-300">
        관심사를 선택하고, 트렌드를 얼마나 반영할지 슬라이더로 정하는 화면입니다.
        지금은 레이아웃만 잡아두는 단계예요.
      </p>

      <div className="space-y-2">
        <div className="flex items-center justify-between text-xs text-slate-300">
          <span>트렌드 비중</span>
          <span className="font-mono text-sky-400">{trendWeight}%</span>
        </div>
        <input
          type="range"
          min={0}
          max={100}
          value={trendWeight}
          onChange={(e) => setTrendWeight(Number(e.target.value))}
          className="w-full"
        />
      </div>

      <p className="text-xs text-slate-400">
        * 나중에 이 값이 백엔드의 <code>trend_weight</code> 필드로 전달됩니다.
      </p>
    </div>
  );
}

