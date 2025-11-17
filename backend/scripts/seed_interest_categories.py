# scripts/seed_interest_categories.py
from app.db.session import SessionLocal
from app.models.interest_category import InterestCategory


CATEGORY_TREE = [
    {
        "name": "일반·자기계발",
        "children": [
            {
                "name": "지식·정보·미디어",
                "children": [
                    {"name": "백과/상식/퀴즈"},
                    {"name": "시사/뉴스 읽기"},
                    {"name": "도서관·아카이브/자료조직"},
                ],
            },
            {
                "name": "자기계발·습관·생산성",
                "children": [
                    {"name": "목표 설정/OKR/버킷리스트"},
                    {"name": "시간관리/루틴/플래너"},
                    {"name": "집중력/몰입/딥워크"},
                ],
            },
            {
                "name": "트렌드·메가이슈",
                "children": [
                    {"name": "세대/라이프스타일 트렌드"},
                    {"name": "디지털 전환/미래 일자리"},
                    {"name": "메가트렌드/미래예측"},
                ],
            },
        ],
    },
    {
        "name": "심리·가치관",
        "children": [
            {
                "name": "철학·사상",
                "children": [
                    {"name": "서양철학(고대~현대)"},
                    {"name": "동양·한국철학"},
                    {"name": "정치철학·사회사상"},
                ],
            },
            {
                "name": "사고법·논리·비판적 사고",
                "children": [
                    {"name": "논리학·논증·토론"},
                    {"name": "과학철학/지식론"},
                    {"name": "인지편향·생각의 오류"},
                ],
            },
            {
                "name": "심리·인간 이해",
                "children": [
                    {"name": "성격·기질 이론"},
                    {"name": "감정·욕구·동기"},
                    {"name": "대인관계 심리/애착"},
                ],
            },
            {
                "name": "윤리·가치관",
                "children": [
                    {"name": "개인윤리/삶의 태도"},
                    {"name": "직업윤리/AI 윤리"},
                    {"name": "생명윤리/기술윤리"},
                ],
            },
        ],
    },
    {
        "name": "종교 / 영성",
        "children": [
            {
                "name": "세계 종교",
                "children": [
                    {"name": "불교"},
                    {"name": "기독교·가톨릭"},
                    {"name": "이슬람/힌두교/기타 세계종교"},
                ],
            },
            {
                "name": "한국 종교·민속 신앙",
                "children": [
                    {"name": "유교/도교/천도교"},
                    {"name": "무속·민간신앙"},
                    {"name": "신흥종교·종교문화"},
                ],
            },
            {
                "name": "영성·명상·수행",
                "children": [
                    {"name": "명상/마음챙김"},
                    {"name": "수행·영적 성장"},
                    {"name": "종교와 사회/종교사회학"},
                ],
            },
        ],
    },
    {
        "name": "사회과학 / 사회·정치·경제·법",
        "children": [
            {
                "name": "사회·문화·일상",
                "children": [
                    {"name": "가족·인구·세대(청년, MZ, 고령화 등)"},
                    {"name": "젠더·다양성·차별"},
                    {"name": "도시·지역사회·지방소멸"},
                ],
            },
            {
                "name": "정치·행정·국제",
                "children": [
                    {"name": "선거·정당·정치참여"},
                    {"name": "정부·정책·행정"},
                    {"name": "국제정세·외교·지정학"},
                ],
            },
            {
                "name": "경제·경영·노동",
                "children": [
                    {"name": "거시경제·산업구조"},
                    {"name": "노동시장·노동환경·플랫폼 노동"},
                    {"name": "스타트업·기업가정신·경영전략"},
                ],
            },
            {
                "name": "법·권리·제도",
                "children": [
                    {"name": "인권·헌법·시민권"},
                    {"name": "소비자 보호·약관·개인정보"},
                    {"name": "노동·복지·사회보장 제도"},
                ],
            },
            {
                "name": "교육·복지·사회문제",
                "children": [
                    {"name": "교육제도·입시·평생교육"},
                    {"name": "복지/돌봄/사회안전망"},
                    {"name": "범죄·안전·군사·치안"},
                ],
            },
        ],
    },
    {
        "name": "자연과학",
        "children": [
            {
                "name": "수학·통계",
                "children": [
                    {"name": "일상 속 수학/수리적 사고"},
                    {"name": "확률·통계·데이터 읽기"},
                    {"name": "암호·알고리즘 이론(개념 소개)"},
                ],
            },
            {
                "name": "물리·천문",
                "children": [
                    {"name": "고전 물리(힘, 운동, 에너지)"},
                    {"name": "현대 물리(양자, 상대성)"},
                    {"name": "우주·천문·우주탐사"},
                ],
            },
            {
                "name": "화학·재료",
                "children": [
                    {"name": "생활 화학(세제, 플라스틱 등)"},
                    {"name": "신소재·배터리·에너지"},
                    {"name": "환경 화학·오염·기후"},
                ],
            },
            {
                "name": "생명과학·환경",
                "children": [
                    {"name": "유전·진화·생명 탄생"},
                    {"name": "뇌과학·인지과학"},
                    {"name": "생태계·기후변화·환경위기"},
                ],
            },
        ],
    },
    {
        "name": "기술과학 / 공학·의학·IT",
        "children": [
            {
                "name": "의학·건강과학",
                "children": [
                    {"name": "질병·의료·보건 정책"},
                    {"name": "운동·영양·생활습관"},
                    {"name": "정신건강·우울·불안·치유"},
                ],
            },
            {
                "name": "공학·인프라·산업기술",
                "children": [
                    {"name": "기계·로봇·제조자동화"},
                    {"name": "전기·전자·반도체"},
                    {"name": "건축·토목·도시 인프라"},
                ],
            },
            {
                "name": "농업·식품·생활과학",
                "children": [
                    {"name": "농업·농촌·식량 문제"},
                    {"name": "식품공학·푸드테크"},
                    {"name": "주거·정리·가사·생활기술"},
                ],
            },
            {
                "name": "정보통신·IT·AI",
                "children": [
                    {"name": "컴퓨터·소프트웨어·프로그래밍"},
                    {"name": "인터넷·플랫폼·모바일 서비스"},
                    {"name": "데이터사이언스·인공지능·추천시스템"},
                ],
            },
        ],
    },
    {
        "name": "예술 / 디자인·대중문화",
        "children": [
            {
                "name": "시각예술·디자인",
                "children": [
                    {"name": "회화·일러스트·드로잉"},
                    {"name": "사진·영상아트"},
                    {"name": "그래픽·브랜딩·UX/UI"},
                ],
            },
            {
                "name": "건축·공예",
                "children": [
                    {"name": "건축·인테리어·도시 디자인"},
                    {"name": "조각·도자·목공·금속공예"},
                    {"name": "전통공예·수작업·핸드메이드"},
                ],
            },
            {
                "name": "음악·공연예술",
                "children": [
                    {"name": "클래식·재즈·국악"},
                    {"name": "K-POP·대중음악"},
                    {"name": "연극·뮤지컬·무용"},
                ],
            },
            {
                "name": "대중문화·엔터테인먼트",
                "children": [
                    {"name": "영화·드라마·OTT"},
                    {"name": "애니메이션·웹툰·게임"},
                    {"name": "아이돌·팬덤·굿즈 문화"},
                ],
            },
        ],
    },
    {
        "name": "언어 / 한국어·외국어·번역",
        "children": [
            {
                "name": "한국어·국어",
                "children": [
                    {"name": "맞춤법·문법·표기"},
                    {"name": "말하기·글쓰기 표현"},
                    {"name": "한글·순우리말·방언"},
                ],
            },
            {
                "name": "외국어 학습",
                "children": [
                    {"name": "영어(회화, 시험, 비즈니스)"},
                    {"name": "일본어·중국어"},
                    {"name": "기타 언어(독어, 불어 등)"},
                ],
            },
            {
                "name": "언어학·번역",
                "children": [
                    {"name": "언어학·의미론·담화"},
                    {"name": "번역/통역 실무·노하우"},
                    {"name": "기계번역·LLM·언어기술"},
                ],
            },
        ],
    },
    {
        "name": "문학 / 소설·에세이",
        "children": [
            {
                "name": "한국문학",
                "children": [
                    {"name": "한국 소설"},
                    {"name": "시·시집"},
                    {"name": "수필·에세이"},
                ],
            },
            {
                "name": "세계문학",
                "children": [
                    {"name": "영미문학"},
                    {"name": "유럽문학"},
                    {"name": "기타 지역문학(라틴, 중동 등)"},
                ],
            },
            {
                "name": "장르문학·웹소설",
                "children": [
                    {"name": "미스터리·스릴러"},
                    {"name": "SF·판타지"},
                    {"name": "로맨스·로맨스판타지·웹소설"},
                ],
            },
            {
                "name": "논픽션·인문에세이",
                "children": [
                    {"name": "인문·사상 에세이"},
                    {"name": "여행기·기행문"},
                    {"name": "자전적 글쓰기·회고록"},
                ],
            },
        ],
    },
    {
        "name": "역사 / 지리·문화유산",
        "children": [
            {
                "name": "한국사",
                "children": [
                    {"name": "선사·고대(선사, 부여·삼한, 삼국, 남북국)"},
                    {"name": "고려"},
                    {"name": "조선"},
                    {"name": "근현대사(개항기~오늘)"},
                ],
            },
            {
                "name": "동아시아·세계사",
                "children": [
                    {"name": "중국사"},
                    {"name": "일본사·동아시아사"},
                    {"name": "유럽·미국·기타 지역사"},
                ],
            },
            {
                "name": "주제별 역사",
                "children": [
                    {"name": "전쟁·외교·제국사"},
                    {"name": "일상사·생활사·민속"},
                    {"name": "과학·기술·경제·사상사"},
                ],
            },
            {
                "name": "문화유산·박물관",
                "children": [
                    {"name": "유물·고고학·발굴"},
                    {"name": "건축·사찰·고적"},
                    {"name": "종교·의례용품/미술사/전시콘텐츠"},
                ],
            },
        ],
    },
]


def insert_categories(db, nodes, parent=None, level: int = 1):
    for node in nodes:
        cat = InterestCategory(
            name=node["name"],
            parent_id=parent.id if parent else None,
            level=level,
        )
        db.add(cat)
        db.flush()  # cat.id 채우기

        children = node.get("children") or []
        if children:
            insert_categories(db, children, parent=cat, level=level + 1)


def main():
    db = SessionLocal()
    try:
        # 기존 데이터 있으면 지우고 다시 넣고 싶으면 아래 주석 해제
        # db.query(InterestCategory).delete()
        # db.commit()

        insert_categories(db, CATEGORY_TREE)
        db.commit()
        print("✅ interest_categories seeding 완료")
    finally:
        db.close()


if __name__ == "__main__":
    # 실행: PYTHONPATH=. python scripts/seed_interest_categories.py
    main()

