// src/app/topics/page.tsx
// src/app/topics/page.tsx
"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE ?? "http://127.0.0.1:8000";

// 로그인 때 쓰는 토큰 키랑 꼭 맞춰줘!
const ACCESS_TOKEN_KEY = "sentencify_access_token";

// 카테고리 선택 값을 보관하는 키
const CATEGORY_STORAGE_KEY = "bookend:selectedCategory";

type Topic = {
  id: string;
  title: string;
  description: string;
  category_id: number;
  source_type: string;
  score: number | null;
  trend_score: number | null;
};

type ResourceBook = {
  title: string;
  author?: string | null;
  thumbnail_url?: string | null;
  external_url?: string | null;
  source?: string | null;
};

type ResourceContent = {
  title: string;
  platform?: string | null;
  thumbnail_url?: string | null;
  external_url?: string | null;
  source?: string | null;
};

type ResourcePost = {
  title: string;
  external_url?: string | null;
  source?: string | null;
};

type Resources = {
  books: ResourceBook[];
  contents: ResourceContent[];
  posts: ResourcePost[];
};

type SelectedCategoryPayload = {
  ids: { main?: number | null; middle?: number | null; sub?: number | null };
  names: { main?: string; middle?: string; sub?: string };
};

// 카테고리 선택 안 한 경우 기본값 (지금 쓰고 있는 3개)
const DEFAULT_SELECTED_CATEGORY: SelectedCategoryPayload = {
  ids: { main: 1, middle: 2, sub: 3 },
  names: {
    main: "기술과학 / 공학·의학·IT",
    middle: "정보통신 / IT·AI",
    sub: "데이터사이언스·인공지능·추천시스템",
  },
};

function loadSelectedCategory(): SelectedCategoryPayload {
  if (typeof window === "undefined") return DEFAULT_SELECTED_CATEGORY;

  try {
    const raw = window.localStorage.getItem(CATEGORY_STORAGE_KEY);
    if (!raw) return DEFAULT_SELECTED_CATEGORY;

    const parsed = JSON.parse(raw);
    if (!parsed || typeof parsed !== "object") {
      return DEFAULT_SELECTED_CATEGORY;
    }

    return {
      ids: parsed.ids ?? DEFAULT_SELECTED_CATEGORY.ids,
      names: parsed.names ?? DEFAULT_SELECTED_CATEGORY.names,
    };
  } catch {
    return DEFAULT_SELECTED_CATEGORY;
  }
}

export default function TopicsPage() {
  const router = useRouter();

  const [selectedCategory, setSelectedCategory] =
    useState<SelectedCategoryPayload>(DEFAULT_SELECTED_CATEGORY);
  const [inputKeyword, setInputKeyword] = useState("");
  const [trendWeight, setTrendWeight] = useState(0); // 0~100 (0=미반영)
  const [topics, setTopics] = useState<Topic[]>([]);
  const [resources, setResources] = useState<Resources | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 로컬스토리지에서 카테고리 불러오기
  useEffect(() => {
    const loaded = loadSelectedCategory();
    setSelectedCategory(loaded);
  }, []);

  const handleRechooseCategories = () => {
    router.push("/topics/categories");
  };

  const handleGenerateTopics = async () => {
    const pathIds: number[] = [];
    if (selectedCategory.ids.main) pathIds.push(selectedCategory.ids.main);
    if (selectedCategory.ids.middle) pathIds.push(selectedCategory.ids.middle);
    if (selectedCategory.ids.sub) pathIds.push(selectedCategory.ids.sub);

    if (pathIds.length === 0) {
      alert("먼저 관심 카테고리를 선택해 주세요.");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const token =
        typeof window !== "undefined"
          ? window.localStorage.getItem(ACCESS_TOKEN_KEY)
          : null;

      const resp = await fetch(`${API_BASE}/topics/recommend`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({
          category_ids: pathIds,
          input_keyword: inputKeyword.trim() || undefined,
          use_trend: true,
          trend_weight: trendWeight, // 0~100 그대로 넘김
          limit: 3,
        }),
      });

      if (!resp.ok) {
        throw new Error(`API 오류: ${resp.status}`);
      }

      const data = await resp.json();
      setTopics(data.topics ?? []);
      setResources({
        books: data.resources?.books ?? [],
        contents: data.resources?.contents ?? [],
        posts: data.resources?.posts ?? [],
      });
    } catch (err: any) {
      console.error(err);
      setError(err?.message ?? "주제 생성 중 오류가 발생했습니다.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-slate-100 flex justify-center px-4 py-8">
      <div className="w-full max-w-6xl">
        {/* 상단 헤더 */}
        <div className="mb-4 flex items-center justify-between gap-4">
          <h1 className="text-sm md:text-base font-medium text-slate-700">
            선택한 관심사 카테고리 기반 주제 추천
          </h1>

          <button
            type="button"
            onClick={handleRechooseCategories}
            className="inline-flex items-center gap-1 rounded-full border border-slate-300 bg-white px-3 py-1 text-xs md:text-sm text-slate-600 hover:border-purple-400 hover:text-purple-500 transition"
          >
            <span aria-hidden>⟲</span>
            카테고리 다시 설정
          </button>
        </div>

        <div className="grid gap-6 lg:grid-cols-[minmax(0,2.1fr)_minmax(0,1fr)]">
          {/* 왼쪽: 입력 + 주제 리스트 */}
          <section className="rounded-3xl bg-white shadow-sm p-4 md:p-6">
            {/* 선택된 카테고리 pill */}
            <div className="mb-3 flex flex-wrap gap-2 text-xs md:text-sm">
              {["main", "middle", "sub"].map((level) => {
                const label =
                  (selectedCategory.names as any)[level] ??
                  (level === "main"
                    ? "대분류"
                    : level === "middle"
                    ? "중분류"
                    : "소분류");

                return (
                  <span
                    key={level}
                    className="inline-flex items-center rounded-full bg-purple-600 px-4 py-1 text-[11px] md:text-xs font-medium text-white"
                  >
                    {label}
                  </span>
                );
              })}
            </div>

            {/* 사용자 입력 영역 */}
            <div className="mb-4">
              <textarea
                value={inputKeyword}
                onChange={(e) => setInputKeyword(e.target.value)}
                placeholder="생각 나는 것들을 적어주세요."
                className="w-full min-h-[120px] rounded-2xl border border-slate-200 bg-slate-50/70 px-3 py-2 text-sm text-slate-800 outline-none resize-none focus:border-purple-400 focus:ring-2 focus:ring-purple-100"
              />
            </div>

            {/* 트렌드 슬라이더 */}
            <div className="mb-4 space-y-1">
              <div className="flex items-center justify-between text-[11px] md:text-xs text-slate-500">
                <span>트렌드 비중</span>
                <span>{trendWeight}</span>
              </div>
              <input
                type="range"
                min={0}
                max={100}
                value={trendWeight}
                onChange={(e) => setTrendWeight(Number(e.target.value))}
                className="w-full accent-purple-500"
              />
              <div className="flex justify-between text-[10px] md:text-[11px] text-slate-400">
                <span>0 (트렌드 미반영)</span>
                <span>100 (트렌드 최대 반영)</span>
              </div>
            </div>

            {/* 생성하기 버튼 */}
            <button
              type="button"
              onClick={handleGenerateTopics}
              disabled={loading}
              className="mb-4 w-full rounded-full bg-purple-600 py-3 text-sm md:text-base font-semibold text-white shadow-sm hover:bg-purple-700 disabled:cursor-not-allowed disabled:opacity-70 transition"
            >
              {loading ? "생성 중..." : "생성하기"}
            </button>

            {/* 오류 메시지 */}
            {error && (
              <p className="mb-2 text-xs text-red-500">{error}</p>
            )}

            {/* 주제 리스트 */}
            <div className="space-y-3">
              {topics.map((topic, index) => (
                <article
                  key={topic.id ?? index}
                  className="rounded-2xl border border-slate-100 bg-slate-50/60 px-4 py-3"
                >
                  <div className="mb-1 flex items-center justify-between gap-2">
                    <span className="text-[11px] text-slate-400">
                      주제 {index + 1}
                    </span>
                    <span className="inline-flex items-center gap-1 rounded-full bg-slate-900/80 px-2 py-[2px] text-[10px] font-medium text-white">
                      LLM
                      {typeof topic.score === "number" && (
                        <span className="ml-1 text-[10px] font-normal opacity-80">
                          score: {topic.score.toFixed(2)}
                        </span>
                      )}
                    </span>
                  </div>
                  <h2 className="mb-1 text-sm md:text-base font-semibold text-slate-900">
                    {topic.title}
                  </h2>
                  <p className="text-[11px] md:text-sm leading-relaxed text-slate-600">
                    {topic.description}
                  </p>
                </article>
              ))}

              {!loading && topics.length === 0 && (
                <p className="text-xs md:text-sm text-slate-400">
                  상단에서 글감을 입력하고 &quot;생성하기&quot;를 눌러
                  주제를 받아보세요.
                </p>
              )}
            </div>
          </section>

          {/* 오른쪽: 추천 리소스 (도서 / 콘텐츠 / 포스트) */}
          <aside className="space-y-4">
            {/* 추천 도서 */}
            <div className="rounded-3xl bg-white shadow-sm p-4 md:p-5">
              <h3 className="mb-3 text-xs md:text-sm font-semibold text-slate-700">
                추천 도서
              </h3>
              <div className="flex flex-col gap-3">
                {(resources?.books ?? []).length === 0 && (
                  <p className="text-[11px] md:text-xs text-slate-400">
                    북엔드에서 곧 추천 도서를 보여줄 예정이에요.
                  </p>
                )}
                {(resources?.books ?? []).map((book, idx) => (
                  <div
                    key={`${book.title}-${idx}`}
                    className="flex items-center gap-3 rounded-2xl bg-slate-50 px-3 py-2"
                  >
                    <div className="h-14 w-10 flex-shrink-0 rounded-lg bg-slate-200" />
                    <div className="min-w-0">
                      <p className="truncate text-xs font-semibold text-slate-800">
                        {book.title}
                      </p>
                      {book.author && (
                        <p className="truncate text-[10px] text-slate-500">
                          {book.author}
                        </p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* 추천 콘텐츠 */}
            <div className="rounded-3xl bg-white shadow-sm p-4 md:p-5">
              <h3 className="mb-3 text-xs md:text-sm font-semibold text-slate-700">
                추천 콘텐츠
              </h3>
              <div className="flex flex-col gap-3">
                {(resources?.contents ?? []).length === 0 && (
                  <p className="text-[11px] md:text-xs text-slate-400">
                    MUNCH에서 추천 영상을 연결할 예정이에요.
                  </p>
                )}
                {(resources?.contents ?? []).map((item, idx) => (
                  <div
                    key={`${item.title}-${idx}`}
                    className="flex items-center gap-3 rounded-2xl bg-slate-50 px-3 py-2"
                  >
                    <div className="h-14 w-20 flex-shrink-0 rounded-lg bg-slate-200" />
                    <div className="min-w-0">
                      <p className="truncate text-xs font-semibold text-slate-800">
                        {item.title}
                      </p>
                      {item.platform && (
                        <p className="truncate text-[10px] text-slate-500">
                          {item.platform}
                        </p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* 관련 포스트 */}
            <div className="rounded-3xl bg-white shadow-sm p-4 md:p-5">
              <h3 className="mb-3 text-xs md:text-sm font-semibold text-slate-700">
                관련 포스트
              </h3>
              <div className="flex flex-col gap-2">
                {(resources?.posts ?? []).length === 0 && (
                  <p className="text-[11px] md:text-xs text-slate-400">
                    나중에 북엔드 내부 글이나 블로그 글을 연결할 수 있어요.
                  </p>
                )}
                {(resources?.posts ?? []).map((post, idx) => (
                  <div
                    key={`${post.title}-${idx}`}
                    className="rounded-2xl bg-slate-50 px-3 py-2 text-xs text-slate-700"
                  >
                    {post.title}
                  </div>
                ))}
              </div>
            </div>
          </aside>
        </div>
      </div>
    </main>
  );
}

