// src/app/topics/categories/page.tsx
"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

const CATEGORY_STORAGE_KEY = "bookend:selectedCategory";

type CategoryOption = {
  id: number;
  label: string;
};

type CategoryTree = {
  main: CategoryOption[];
  middle: Record<number, CategoryOption[]>;
  sub: Record<number, CategoryOption[]>;
};

// ⚠️ 일단은 프론트에서만 쓰는 mock 트리.
// 나중에 DB/백엔드 카테고리랑 맞추고 싶으면 여기 id만 교체하면 돼.
const CATEGORY_TREE: CategoryTree = {
  main: [
    { id: 1, label: "기술과학 / 공학·의학·IT" },
    { id: 2, label: "정보통신 / IT·AI" },
    { id: 3, label: "데이터사이언스·인공지능·추천시스템" },
  ],
  middle: {
    1: [
      { id: 11, label: "지식정보·미디어" },
      { id: 12, label: "자기계발·습관·실천성" },
      { id: 13, label: "트렌드·메가이슈" },
    ],
    2: [
      { id: 21, label: "프로그래밍·코딩" },
      { id: 22, label: "웹·모바일 서비스" },
    ],
    3: [
      { id: 31, label: "추천시스템·AI 응용" },
      { id: 32, label: "데이터 분석·시각화" },
    ],
  },
  sub: {
    11: [
      { id: 101, label: "백과사전/퀴즈" },
      { id: 102, label: "시사·뉴스 읽기" },
      { id: 103, label: "도서관·아카이브·자료조직" },
    ],
    12: [
      { id: 111, label: "루틴·습관 만들기" },
      { id: 112, label: "목표 설정·자기 점검" },
    ],
    13: [
      { id: 121, label: "AI·출판 트렌드" },
      { id: 122, label: "미디어 환경 변화" },
    ],
    21: [
      { id: 201, label: "파이썬" },
      { id: 202, label: "자바스크립트" },
    ],
    31: [
      { id: 301, label: "개인화 추천" },
      { id: 302, label: "콘텐츠 추천" },
    ],
  },
};

type SelectedCategory = {
  mainId: number | null;
  middleId: number | null;
  subId: number | null;
};

function PillsRow({
  options,
  selectedId,
  onClick,
}: {
  options: CategoryOption[];
  selectedId: number | null;
  onClick: (id: number) => void;
}) {
  return (
    <div className="flex flex-wrap gap-2">
      {options.map((opt) => {
        const isActive = opt.id === selectedId;
        return (
          <button
            key={opt.id}
            type="button"
            onClick={() => onClick(opt.id)}
            className={`rounded-full px-4 py-2 text-xs md:text-sm transition ${
              isActive
                ? "bg-purple-600 text-white shadow-sm"
                : "bg-slate-100 text-slate-600 hover:bg-slate-200"
            }`}
          >
            {opt.label}
          </button>
        );
      })}
    </div>
  );
}

export default function CategorySelectPage() {
  const router = useRouter();
  const [selected, setSelected] = useState<SelectedCategory>({
    mainId: null,
    middleId: null,
    subId: null,
  });

  // 최초 진입 시 기본 선택 (각 레벨 첫 번째)
  useEffect(() => {
    const defaultMain = CATEGORY_TREE.main[0]?.id ?? null;
    const middleList =
      (defaultMain && CATEGORY_TREE.middle[defaultMain]) || [];
    const defaultMiddle = middleList[0]?.id ?? null;
    const subList =
      (defaultMiddle && CATEGORY_TREE.sub[defaultMiddle]) || [];
    const defaultSub = subList[0]?.id ?? null;

    setSelected({
      mainId: defaultMain,
      middleId: defaultMiddle,
      subId: defaultSub,
    });
  }, []);

  const handleMainClick = (id: number) => {
    if (id === selected.mainId) return;

    const middleList = CATEGORY_TREE.middle[id] ?? [];
    const newMiddle = middleList[0]?.id ?? null;
    const subList = newMiddle ? CATEGORY_TREE.sub[newMiddle] ?? [] : [];
    const newSub = subList[0]?.id ?? null;

    setSelected({
      mainId: id,
      middleId: newMiddle,
      subId: newSub,
    });
  };

  const handleMiddleClick = (id: number) => {
    if (id === selected.middleId) return;

    const subList = CATEGORY_TREE.sub[id] ?? [];
    const newSub = subList[0]?.id ?? null;

    setSelected((prev) => ({
      ...prev,
      middleId: id,
      subId: newSub,
    }));
  };

  const handleSubClick = (id: number) => {
    setSelected((prev) => ({ ...prev, subId: id }));
  };

  const handleSubmit = () => {
    const { mainId, middleId, subId } = selected;

    if (!mainId || !middleId || !subId) {
      alert("대분류, 중분류, 소분류를 모두 선택해 주세요.");
      return;
    }

    const findLabel = (list: CategoryOption[], id: number | null) =>
      list.find((c) => c.id === id)?.label ?? "";

    const mainLabel = findLabel(CATEGORY_TREE.main, mainId);
    const middleLabel = findLabel(
      CATEGORY_TREE.middle[mainId] ?? [],
      middleId,
    );
    const subLabel = findLabel(
      CATEGORY_TREE.sub[middleId] ?? [],
      subId,
    );

    if (typeof window !== "undefined") {
      window.localStorage.setItem(
        CATEGORY_STORAGE_KEY,
        JSON.stringify({
          ids: { main: mainId, middle: middleId, sub: subId },
          names: { main: mainLabel, middle: middleLabel, sub: subLabel },
        }),
      );
    }

    router.push("/topics");
  };

  const mainOptions = CATEGORY_TREE.main;
  const middleOptions =
    (selected.mainId && CATEGORY_TREE.middle[selected.mainId]) || [];
  const subOptions =
    (selected.middleId && CATEGORY_TREE.sub[selected.middleId]) || [];

  return (
    <main className="min-h-screen bg-slate-100 flex justify-center px-4 py-8">
      <div className="w-full max-w-5xl rounded-3xl bg-white shadow-sm p-6 md:p-10">
        <h1 className="mb-6 text-base md:text-lg font-semibold text-slate-800">
          관심 카테고리 선택
        </h1>

        {/* 대분류 */}
        <section className="mb-8 space-y-2">
          <p className="text-xs md:text-sm font-medium text-slate-700">
            관심 카테고리 - 대분류
          </p>
          <PillsRow
            options={mainOptions}
            selectedId={selected.mainId}
            onClick={handleMainClick}
          />
        </section>

        {/* 중분류 */}
        <section className="mb-8 space-y-2">
          <p className="text-xs md:text-sm font-medium text-slate-700">
            관심 카테고리 - 중분류
          </p>
          {middleOptions.length > 0 ? (
            <PillsRow
              options={middleOptions}
              selectedId={selected.middleId}
              onClick={handleMiddleClick}
            />
          ) : (
            <p className="text-xs text-slate-400">
              이 대분류에 대한 중분류가 아직 준비 중입니다.
            </p>
          )}
        </section>

        {/* 소분류 */}
        <section className="mb-10 space-y-2">
          <p className="text-xs md:text-sm font-medium text-slate-700">
            관심 카테고리 - 소분류
          </p>
          {subOptions.length > 0 ? (
            <PillsRow
              options={subOptions}
              selectedId={selected.subId}
              onClick={handleSubClick}
            />
          ) : (
            <p className="text-xs text-slate-400">
              이 중분류에 대한 소분류가 아직 준비 중입니다.
            </p>
          )}
        </section>

        <div className="flex justify-center">
          <button
            type="button"
            onClick={handleSubmit}
            className="w-full md:w-auto rounded-full bg-purple-600 px-10 py-3 text-sm md:text-base font-semibold text-white shadow-sm hover:bg-purple-700 transition"
          >
            주제 생성하기
          </button>
        </div>
      </div>
    </main>
  );
}

