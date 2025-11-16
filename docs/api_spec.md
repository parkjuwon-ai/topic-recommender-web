# API & Data Model Spec (v1)

## 기능 범위

- 로그인 (Google)
- 관심 카테고리 선택 (대/중/소)
- 선택한 관심사 기반 주제 추천 + 리소스 추천
- 주제 선택 기록

---

## 1. ERD (Mermaid)

```mermaid
erDiagram
    USERS ||--o{ USER_INTERESTS : has
    INTEREST_CATEGORIES ||--o{ USER_INTERESTS : has

    USERS ||--o{ USER_TOPIC_SESSIONS : starts
    TOPIC_CANDIDATES ||--o{ USER_TOPIC_SESSIONS : selected

    USERS {
        uuid   id PK
        string email
        string name
        string avatar_url
        string auth_provider        // 'google'
        string provider_user_id     // Google sub
        timestamp created_at
        timestamp updated_at
        timestamp last_login_at
    }

    INTEREST_CATEGORIES {
        int       id PK
        string    name
        int       parent_id FK      // self reference
        smallint  level             // 1:대, 2:중, 3:소
        timestamp created_at
    }

    USER_INTERESTS {
        uuid   id PK
        uuid   user_id FK
        int    category_id FK       // 보통 소분류 id
        float  weight               // 기본 1.0
        timestamp created_at
    }

    TOPIC_CANDIDATES {
        uuid     id PK
        string   title
        string   description
        int      category_id FK
        string   source_type        // trend | bookend | munch | manual
        json     source_meta
        timestamp created_at
        timestamp updated_at
    }

    USER_TOPIC_SESSIONS {
        uuid     id PK
        uuid     user_id FK
        uuid     topic_id FK
        string   input_keyword
        boolean  use_trend
        string   selected_format    // blog | newsletter | ...
        timestamp created_at
    }
```
## 2. 주요 플로우

### 2.1 로그인 플로우

1. 클라이언트에서 Google 로그인 → `id_token` 획득  
2. 서버 `/auth/login`에 `id_token` 전송  
3. 성공 시:
   - **신규 사용자**면 회원가입 + JWT 발급  
   - **기존 사용자**면 `last_login_at` 갱신 + JWT 발급  
4. 프론트는 JWT를 저장하고 이후 요청에 `Authorization` 헤더로 전송  

---

### 2.2 라우팅 규칙 (초기 진입)

1. 클라이언트 진입 시 `GET /me` 호출  
2. 응답의 `interests` 기준으로 분기:
   - `interests` 비어 있음 → **관심 카테고리 선택 화면**으로 이동  
   - `interests` 존재 → **주제 추천 화면**으로 이동  

---

### 2.3 관심 카테고리 선택 화면

1. `GET /interest-categories/tree` 호출 → 전체 카테고리 트리 조회  
2. `GET /me`로 현재 선택된 카테고리 목록 조회 → UI 상에서 하이라이트  
3. 사용자가 대/중/소 카테고리를 선택  
4. 하단 💜 버튼 클릭 시:
   - `PUT /me/interests` 호출로 저장  
   - 성공 후 `/topics` (주제 추천 화면)으로 이동  

---

### 2.4 주제 추천 화면

**레이아웃(예상)**

- 왼쪽: 카테고리 칩, 입력 박스, 트렌드 ON/OFF 토글, “실행하기” 버튼  
- 오른쪽: 추천 주제 카드(1~3개), 추천 리소스 영역  

**플로우**

1. 사용자가 카테고리 선택, 입력 키워드 작성, 트렌드 ON/OFF 설정  
2. “실행하기” 버튼 클릭 → `POST /topics/recommend` 호출  
3. 응답 매핑:
   - `topics` → “주제 1~3” 카드  
   - `resources` → 추천 도서/콘텐츠/포스트/트렌드 영역  

---

### 2.5 주제 선택 플로우

1. 사용자가 특정 주제 카드를 클릭  
2. 글 형식 선택 (예: `blog`, `newsletter` 등)  
3. `POST /sessions` 호출로 선택 기록 저장  
4. 이후 Draft 화면 등으로 라우팅 (추후 확장)  

---

## 3. Auth

### 3.1 POST /auth/login

**설명**  
Google `id_token`으로 로그인/회원가입 후 JWT 발급.

- 회원이 존재하지 않으면 `USERS`에 생성  
- 항상 `user` 정보 + `token` 반환  

**Request**

```json
{
  "id_token": "google-id-token-string"
}
```

### Response 200 OK

```json
{
  "user": {
    "id": "8e8f3c9a-1a2b-4c3d-9e0f-123456789abc",
    "email": "user@example.com",
    "name": "홍길동",
    "avatar_url": "https://lh3.googleusercontent.com/...",
    "created_at": "2025-11-15T09:00:00Z"
  },
  "token": "jwt-token-string"
}
```

## 4. Me & Interests

### 4.1 GET /me

**설명**  
현재 로그인된 사용자 정보 + 관심사 목록 조회.

**Response 200 OK**

```json
{
  "id": "8e8f3c9a-1a2b-4c3d-9e0f-123456789abc",
  "email": "user@example.com",
  "name": "홍길동",
  "avatar_url": "https://lh3.googleusercontent.com/...",
  "interests": [
    { "category_id": 101, "name": "정보통신·IT·AI", "level": 2 },
    { "category_id": 203, "name": "데이터사이언스·인공지능·추천시스템", "level": 3 }
  ]
}
```

### 4.2 PUT /me/interests

**설명**  
사용자의 관심 카테고리 저장/갱신.  
관심 선택 화면에서 하단 💜 버튼 클릭 시 호출.

- 기존 `USER_INTERESTS`는 삭제 후 재생성 또는 upsert 정책 사용  
- `weight`는 기본 1.0, 필요 시 가중치 조정 가능  

**Request**

```json
{
  "interests": [
    { "category_id": 203, "weight": 1.0 },
    { "category_id": 187, "weight": 1.0 },
    { "category_id": 45,  "weight": 0.8 }
  ]
}
```

**Response 200 OK**

```json
{
  "interests": [
    {
      "category_id": 203,
      "name": "데이터사이언스·인공지능·추천시스템",
      "level": 3,
      "weight": 1.0
    },
    {
      "category_id": 187,
      "name": "정보통신·IT·AI",
      "level": 2,
      "weight": 1.0
    },
    {
      "category_id": 45,
      "name": "일반·자기계발",
      "level": 1,
      "weight": 0.8
    }
  ]
}
```

## 5. 관심 카테고리

### 5.1 GET /interest-categories/tree

**설명**  
대/중/소 전체 카테고리 트리를 반환.  
프론트에서는 이를 기반으로 트리형 선택 UI 구성.

**Response 200 OK (예시)**

```json
{
  "items": [
    {
      "id": 1,
      "name": "일반·자기계발",
      "children": [
        {
          "id": 2,
          "name": "지식·정보·미디어",
          "children": [
            { "id": 3, "name": "백과/상식/퀴즈" },
            { "id": 4, "name": "시사/뉴스 읽기" },
            { "id": 5, "name": "도서관·아카이브/자료조직" }
          ]
        },
        {
          "id": 6,
          "name": "자기계발·습관·생산성",
          "children": [
            { "id": 7, "name": "목표 설정/OKR/버킷리스트" },
            { "id": 8, "name": "시간관리/루틴/플래너" },
            { "id": 9, "name": "집중력/몰입/딥워크" }
          ]
        }
        // ...
      ]
    }
    // 나머지 대분류들...
  ]
}
```

## 6. 주제 + 리소스 추천

### 6.1 POST /topics/recommend

**설명**  
관심사 + 입력 키워드 + 트렌드 ON/OFF 정보를 기반으로  
주제 3개와 관련 리소스를 추천.

- `category_ids` 생략 시 → 서버에서 `USER_INTERESTS` 기반 대표 카테고리 자동 선택  
- `use_trend = true` → Google Trends 기반 연관 트렌드 반영  

**Request**

```json
{
  "category_ids": [203, 187],
  "input_keyword": "추천 시스템 수업 복습 에세이 쓰기",
  "use_trend": true,
  "limit": 3
}
```

**Response 200 OK (요약 예시)**

```json
{
  "topics": [
    {
      "id": "7b2f9f40-5d4c-4a2b-8f61-2a4efc3c1111",
      "title": "내 첫 추천 시스템 프로젝트 회고록",
      "description": "수업에서 만든 추천 시스템을 실제 서비스 관점에서 돌아보는 에세이.",
      "category": {
        "id": 203,
        "name": "데이터사이언스·인공지능·추천시스템"
      },
      "source_type": "trend",
      "source_meta": {
        "trend_used": true,
        "trend_score": 78
      }
    },
    {
      "...": "..."
    },
    {
      "...": "..."
    }
  ],
  "resources": {
    "books": [
      {
        "title": "Easy! 추천 시스템 입문",
        "author": "홍길동",
        "thumbnail_url": "https://book-end.tech/book1.jpg",
        "external_url": "https://book-end.tech/books/123",
        "source": "bookend"
      }
    ],
    "contents": [
      {
        "title": "추천 시스템 개념 한 번에 정리",
        "platform": "munch",
        "thumbnail_url": "https://munch.press/thumb/abc.jpg",
        "external_url": "https://munch.press/videos/abc",
        "source": "munch"
      }
    ],
    "posts": [],
    "trends": [
      "#추천시스템",
      "#데이터사이언스",
      "#AI에세이"
    ]
  }
}
```
### 7. 세션 (주제 선택 기록)

#### 7.1 POST /sessions

**설명**  
사용자가 주제 카드를 선택하고 글 형식을 고를 때 호출.  
선택된 주제/입력/트렌드 사용 여부/형식을 기록.

**Request**

```json
{
  "topic_id": "7b2f9f40-5d4c-4a2b-8f61-2a4efc3c1111",
  "input_keyword": "추천 시스템 수업 복습 에세이 쓰기",
  "use_trend": true,
  "selected_format": "blog"
}
```

**Response 200 OK (요약 예시)**
```json
{
  "id": "c7a1e0cb-8f5f-4c77-9c69-c1c4d6af9999",
  "user_id": "8e8f3c9a-1a2b-4c3d-9e0f-123456789abc",
  "topic_id": "7b2f9f40-5d4c-4a2b-8f61-2a4efc3c1111",
  "selected_format": "blog",
  "created_at": "2025-11-15T09:10:00Z"
}
```

#### 7.2 GET /sessions/me (요약)

**설명**  
내가 선택했던 주제 세션들을 요약 리스트로 조회.

**Response 200 OK**

```json
{
  "items": [
    {
      "id": "c7a1e0cb-8f5f-4c77-9c69-c1c4d6af9999",
      "topic": {
        "id": "7b2f9f40-5d4c-4a2b-8f61-2a4efc3c1111",
        "title": "내 첫 추천 시스템 프로젝트 회고록"
      },
      "selected_format": "blog",
      "created_at": "2025-11-15T09:10:00Z"
    }
  ]
}
```


