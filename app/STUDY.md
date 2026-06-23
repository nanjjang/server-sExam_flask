# photoArchive — 발표 준비 완전 정리

---

## 목차

1. [프로젝트 전체 구조](#1-프로젝트-전체-구조)
2. [Flask 앱이 켜지는 흐름](#2-flask-앱이-켜지는-흐름)
3. [Blueprint — 라우트를 나누는 방법](#3-blueprint--라우트를-나누는-방법)
4. [회원가입 / 로그인 / 로그아웃 흐름](#4-회원가입--로그인--로그아웃-흐름)
5. [사진 업로드 흐름](#5-사진-업로드-흐름)
6. [갤러리 / 내 갤러리 흐름](#6-갤러리--내-갤러리-흐름)
7. [검색 흐름](#7-검색-흐름)
8. [데이터 저장 구조 (DB 없이 JSON과 파일로)](#8-데이터-저장-구조-db-없이-json과-파일로)
9. [Jinja2 템플릿 — 파이썬 데이터를 HTML에 넣는 법](#9-jinja2-템플릿--파이썬-데이터를-html에-넣는-법)
10. [세션 — 로그인 상태를 기억하는 법](#10-세션--로그인-상태를-기억하는-법)
11. [정적 파일 (CSS, 이미지) 서빙 구조](#11-정적-파일-css-이미지-서빙-구조)
12. [자주 물어볼 만한 것들 Q&A](#12-자주-물어볼-만한-것들-qa)

---

## 1. 프로젝트 전체 구조

```
app/
├── app.py                  ← Flask 앱 생성, 실행 진입점
├── config.py               ← 경로 상수, 환경변수
├── routes/
│   ├── __init__.py         ← Blueprint 등록
│   ├── root.py             ← 화면 라우트 (홈, 갤러리, 피처 등)
│   ├── upload.py           ← 사진 업로드 라우트
│   └── auth.py             ← 회원가입, 로그인, 로그아웃 라우트
├── models/
│   └── user.py             ← 유저 데이터 읽기/쓰기 함수
├── templates/
│   ├── base.html           ← 공통 네비게이션, 푸터 (모든 페이지가 extends)
│   ├── home.html
│   ├── gallery.html
│   ├── my_gallery.html
│   ├── upload.html
│   ├── feature.html
│   ├── reviews.html
│   ├── whats_new.html
│   ├── news_detail.html
│   ├── page.html
│   ├── login.html
│   └── register.html
├── static/
│   ├── css/
│   │   ├── index.css       ← 나머지 CSS를 @import로 묶는 진입점
│   │   ├── base.css        ← 공통 스타일
│   │   ├── home.css        ← 홈/피처/리뷰 마케팅 페이지 스타일
│   │   ├── marketplace.css
│   │   ├── news.css
│   │   ├── reviews.css
│   │   └── pages.css       ← 피처 페이지 섹션들 스타일
│   └── images/             ← UI 스크린샷 이미지들
└── database/
    ├── image_meta.json     ← 사진 메타데이터 (제목, 분류, 업로더, 날짜)
    ├── images/             ← 업로드된 사진 원본
    ├── thumbs/             ← 썸네일 (있을 경우)
    └── users/              ← 유저별 JSON 파일 ({username}.json)
```

---

## 2. Flask 앱이 켜지는 흐름

```python
# app.py
app = Flask(__name__, static_folder='static', static_url_path='/static')
app.secret_key = secret_key
register_routes(app)
```

1. `Flask(__name__)` — 현재 파일 위치를 기준으로 Flask 앱 객체를 만든다.
2. `static_folder='static'` — `/static/` URL로 요청이 오면 `app/static/` 폴더에서 파일을 찾는다.
3. `secret_key` — 세션(쿠키) 데이터를 암호화하는 비밀 키. `.env`에서 읽어온다.
4. `register_routes(app)` — Blueprint 세 개를 한 번에 등록한다.

**왜 `__name__`을 쓰는가?**
Flask가 이 파일의 위치를 기준으로 templates/, static/ 폴더를 찾기 때문이다. `__name__`은 Python이 자동으로 현재 모듈 이름을 넣어준다.

---

## 3. Blueprint — 라우트를 나누는 방법

라우트를 한 파일에 다 넣으면 코드가 길어진다. Blueprint는 라우트를 기능별로 파일로 분리하는 Flask 기능이다.

```python
# routes/__init__.py
def register_routes(app):
    app.register_blueprint(auth_bp,   url_prefix='/auth')
    app.register_blueprint(upload_bp, url_prefix='/upload')
    app.register_blueprint(root_bp,   url_prefix='/')
```

| Blueprint | prefix | 담당 |
|-----------|--------|------|
| `auth_bp` | `/auth` | 회원가입(`/auth/register`), 로그인(`/auth/login`), 로그아웃(`/auth/logout`) |
| `upload_bp` | `/upload` | 업로드 페이지(`/upload/`) |
| `root_bp` | `/` | 홈, 갤러리, 피처, 리뷰, 뉴스 등 |

**url_for() 사용법**
템플릿이나 코드에서 URL을 직접 문자열로 쓰지 않는다.
```python
url_for('auth.login')       # → /auth/login
url_for('upload.upload')    # → /upload/
url_for('root.gallery')     # → /gallery
```
`'Blueprint이름.함수이름'` 형태로 쓴다. URL이 바뀌어도 코드를 고칠 필요가 없다.

---

## 4. 회원가입 / 로그인 / 로그아웃 흐름

### 회원가입 (`/auth/register`)

```
GET /auth/register
  → register.html 렌더링 (빈 폼)

POST /auth/register
  → username, password 받음
  → 비어있으면 에러
  → get_user(username) → 이미 있으면 에러
  → save_user(username, generate_password_hash(password))
  → redirect → /auth/login
```

**비밀번호를 그대로 저장하지 않는 이유**
`generate_password_hash()`는 비밀번호를 해시(단방향 암호화)로 변환한다.
파일이 유출되어도 원래 비밀번호를 알 수 없다.
로그인 시 `check_password_hash(저장된해시, 입력된비밀번호)`로 비교한다.

**유저 데이터 저장 위치**
```
database/users/
  dbswnstj.json
  {
    "username": "dbswnstj",
    "password": "pbkdf2:sha256:...",   ← 해시된 비밀번호
    "created_at": "2026-06-20T..."
  }
```
유저마다 JSON 파일 하나. `get_user(username)`은 `users/{username}.json`이 있는지 확인한다.

### 로그인 (`/auth/login`)

```
POST /auth/login
  → username, password 받음
  → get_user(username) → 없으면 에러
  → check_password_hash(user['password'], password) → 다르면 에러
  → session['user_id'] = username   ← 세션에 저장
  → redirect → /
```

### 로그아웃 (`/auth/logout`)

```python
session.pop('user_id', None)   # 세션에서 user_id 제거
redirect → /
```

---

## 5. 사진 업로드 흐름

```
GET /upload/
  → upload.html 렌더링 (PHOTO_TAGS 태그 목록 전달)

POST /upload/
  1. session에서 user_id 확인 → 없으면 로그인 페이지로
  2. request.files.getlist('fileImage') → 업로드된 파일 목록
  3. 파일마다:
     a. 확장자 추출 (e.g. 'jpg')
     b. 파일명 생성: "{user_id}_{uuid}.{ext}"
        예: "dbswnstj_3f80595326864dcb8acbaf55a42b079c.jpg"
     c. app/database/images/ 에 저장
     d. image_meta.json에 메타데이터 기록
  4. image_meta.json 저장
  5. redirect → /gallery
```

**파일명에 UUID를 붙이는 이유**
같은 이름의 파일을 여러 명이 올려도 충돌하지 않는다.
UUID는 거의 겹치지 않는 랜덤 문자열이다 (`uuid.uuid4().hex`).

**파일명 앞에 user_id를 붙이는 이유**
`dbswnstj_3f805953....jpg` → 파일명만 보면 누가 올린 파일인지 알 수 있다.
갤러리에서 `stem.split('_', 1)[0]`으로 owner를 추출할 수 있다.

**메타데이터 구조**
```json
{
  "dbswnstj_3f80595326864dcb8acbaf55a42b079c.JPG": {
    "title": "Seoul blue hour",
    "collection": "figma-templates",
    "uploaded_by": "dbswnstj",
    "uploaded_at": "2026.06.20"
  }
}
```
이미지 파일 자체에는 제목 같은 정보를 저장할 수 없으니 JSON에 별도로 기록한다.

**여러 장 올릴 때 제목 처리**
```python
if len(files) > 1 and photo_title:
    display_title = f"{photo_title} {index + 1:02d}"
    # "Seoul 01", "Seoul 02", ...
```
사진이 여러 장이고 제목이 있으면 뒤에 번호를 붙인다.

---

## 6. 갤러리 / 내 갤러리 흐름

### get_gallery_photos() — 핵심 함수

```python
def get_gallery_photos(owner=None, limit=None):
    # 1. image_meta.json 불러오기
    # 2. database/images/ 폴더의 파일 목록 읽기
    # 3. 수정 시간(mtime) 기준 최신순 정렬
    # 4. 파일명에서 owner 추출 → owner 파라미터와 비교
    # 5. 썸네일 있으면 썸네일 URL, 없으면 원본 URL
    # 6. photo 딕셔너리 반환
```

반환 딕셔너리 구조:
```python
{
    'filename': 'dbswnstj_3f805...jpg',
    'slug': 'dbswnstj_3f805...',   # 확장자 제거
    'owner': 'dbswnstj',
    'title': 'Seoul blue hour',
    'date': '2026.06.20',
    'url': '/media/dbswnstj_3f805...jpg'
}
```

### 전체 갤러리 (`/gallery`)

```python
@root_bp.route('/gallery')
def gallery():
    query = request.args.get('q', '').strip()
    photos = get_gallery_photos()
    if query:
        photos = [p for p in photos
                  if query.lower() in p['title'].lower()
                  or query.lower() in p['owner'].lower()]
    return render_template('gallery.html', photos=photos, query=query)
```

- `request.args.get('q')` — URL의 `?q=검색어` 쿼리스트링을 읽는다.
- 검색어가 있으면 title 또는 owner에 포함된 사진만 남긴다.

### 내 갤러리 (`/my-gallery`)

```python
@root_bp.route('/my-gallery')
def my_gallery():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login'))   # 비로그인 차단
    photos = get_gallery_photos(owner=user_id)   # 내 사진만
    return render_template('my_gallery.html', photos=photos)
```

`get_gallery_photos(owner=user_id)` → 파일명 앞부분이 `user_id`와 같은 사진만 반환.

---

## 7. 검색 흐름

검색은 별도 라우트 없이 갤러리 라우트에서 처리된다.

```
사용자가 검색어 입력 → 폼 submit
→ GET /gallery?q=검색어
→ gallery() 함수에서 request.args.get('q') 로 읽음
→ photos 목록에서 title/owner 필터링
→ gallery.html에 필터링된 photos 전달
```

HTML 폼:
```html
<form method="GET" action="/gallery">
  <input name="q" value="{{ query }}">
  <button>Search</button>
</form>
```

**POST가 아닌 GET을 쓰는 이유**
검색 결과는 URL에 `?q=...`가 포함되어야 공유하거나 북마크할 수 있다.
데이터를 변경하는 게 아니라 조회만 하기 때문에 GET이 적합하다.

---

## 8. 데이터 저장 구조 (DB 없이 JSON과 파일로)

이 프로젝트는 데이터베이스(MySQL, SQLite 등)를 사용하지 않는다.
파일 시스템과 JSON으로 모든 데이터를 관리한다.

| 데이터 | 저장 위치 | 형식 |
|--------|----------|------|
| 업로드 이미지 원본 | `database/images/` | 이미지 파일 |
| 썸네일 | `database/thumbs/` | 이미지 파일 |
| 이미지 메타데이터 | `database/image_meta.json` | JSON |
| 유저 정보 | `database/users/{username}.json` | JSON |

**JSON을 읽고 쓰는 패턴**
```python
# 읽기
with open(IMAGE_META_PATH, 'r', encoding='utf-8') as file:
    meta = json.load(file)

# 쓰기
with open(IMAGE_META_PATH, 'w', encoding='utf-8') as file:
    json.dump(meta, file, ensure_ascii=False, indent=2)
```
`ensure_ascii=False` — 한글 같은 유니코드 문자를 그대로 저장한다. (없으면 `서울` 같은 코드로 저장됨)

**이 방식의 장단점**
- 장점: 설치 없이 바로 사용 가능, 파일 열어서 내용 바로 확인 가능
- 단점: 동시 접속자가 많으면 JSON 덮어쓰기 충돌 가능, 검색/정렬이 느림

---

## 9. Jinja2 템플릿 — 파이썬 데이터를 HTML에 넣는 법

Flask는 Jinja2 템플릿 엔진을 사용한다.

### 기본 문법

```html
{{ 변수 }}              ← 값 출력
{% if 조건 %}...{% endif %}   ← 조건문
{% for item in list %}...{% endfor %}  ← 반복문
{{ url_for('root.gallery') }}  ← URL 생성
```

### 상속 구조 (base.html)

모든 페이지 템플릿은 base.html을 상속한다.

```html
<!-- base.html -->
<header>...</header>
<main>
  {% block content %}{% endblock %}
</main>
<footer>...</footer>

<!-- gallery.html -->
{% extends 'base.html' %}
{% block content %}
  <h1>갤러리</h1>
  ...
{% endblock %}
```

base.html의 nav, footer 코드를 모든 페이지가 공유한다. 네비게이션을 한 곳만 수정하면 전체 적용된다.

### body_class로 페이지 구분

```python
# 라우트에서
return render_template('home.html', body_class='home')
```

```html
<!-- base.html -->
<body class="{{ body_class|default('') }}">
{% set is_marketing = body_class in ['home', 'feature', 'reviews'] %}
```

`body_class`로 어떤 페이지인지 CSS에서 구분한다.
`is_marketing`이 True이면 어두운 마케팅 스타일 네비게이션과 푸터를 보여준다.

### 데이터 전달

```python
# Python (라우트)
return render_template('gallery.html', photos=photos, query=query)

# HTML (템플릿)
{% for photo in photos %}
  <img src="{{ photo.url }}" alt="{{ photo.title }}">
{% endfor %}
```

`render_template()`의 키워드 인자가 템플릿 변수가 된다.

---

## 10. 세션 — 로그인 상태를 기억하는 법

HTTP는 기본적으로 상태가 없다(stateless). 요청마다 서버는 누가 보냈는지 모른다.
세션은 이 문제를 쿠키로 해결한다.

```python
# 로그인 성공 시
session['user_id'] = username
# → 서버가 암호화된 쿠키를 브라우저에 전달

# 이후 요청마다
user_id = session.get('user_id')   # 쿠키를 복호화해서 읽음

# 로그아웃 시
session.pop('user_id', None)       # 쿠키에서 제거
```

`session`은 Flask가 제공하는 딕셔너리처럼 쓸 수 있는 객체다.
`app.secret_key`로 암호화하기 때문에 사용자가 쿠키 내용을 조작할 수 없다.

**템플릿에서 세션 확인**
```html
{% if session.get('user_id') %}
  <a href="/auth/logout">Logout</a>
{% else %}
  <a href="/auth/login">Login</a>
{% endif %}
```

---

## 11. 정적 파일 (CSS, 이미지) 서빙 구조

```python
# app.py
app = Flask(__name__, static_folder='static', static_url_path='/static')
```

`/static/css/index.css` 요청 → `app/static/css/index.css` 파일 전달

**CSS 구조**
```css
/* index.css — 진입점, 나머지를 모두 import */
@import url("./base.css");
@import url("./home.css");
@import url("./marketplace.css");
@import url("./news.css");
@import url("./reviews.css");
@import url("./pages.css");
```

모든 페이지가 `index.css` 하나만 로드하면 전체 스타일이 적용된다.

**업로드 이미지 서빙**
업로드된 이미지는 `static/` 폴더가 아니라 `database/images/`에 있어서 별도 라우트가 필요하다.

```python
@root_bp.route('/media/<path:filename>')
def media(filename):
    return send_from_directory(IMAGE_PATH, filename)

@root_bp.route('/thumb/<path:filename>')
def thumbnail(filename):
    return send_from_directory(THUMB_PATH, filename)
```

`send_from_directory(폴더, 파일명)` — 지정한 폴더에서 파일을 HTTP 응답으로 전달한다.

---

## 12. 자주 물어볼 만한 것들 Q&A

**Q. 데이터베이스를 안 쓴 이유는?**
이 프로젝트의 목적은 Flask의 라우팅, 파일 저장, 템플릿 구조를 이해하는 것이다.
DB를 추가하면 모델 설계, ORM 설정 등 복잡도가 올라가기 때문에 JSON 파일로 단순하게 구현했다.

**Q. 비밀번호를 어떻게 안전하게 저장하는가?**
`werkzeug.security.generate_password_hash()`로 PBKDF2-SHA256 해시를 만든다.
저장된 해시만 보고는 원래 비밀번호를 역추적할 수 없다.
로그인 시 `check_password_hash(hash, 입력값)`으로 비교한다.

**Q. 파일명을 왜 UUID로 만드는가?**
같은 파일명이 존재할 때 덮어쓰이는 것을 방지한다.
`uuid.uuid4().hex`는 128비트 랜덤 값이라 충돌 확률이 사실상 0이다.

**Q. 전체 갤러리와 내 갤러리는 어떻게 구분하는가?**
파일명 맨 앞이 `{user_id}_`로 시작한다.
`get_gallery_photos(owner=user_id)` 호출 시 파일명의 `_` 앞부분이 user_id와 일치하는 것만 필터링한다.

**Q. 검색은 어떻게 구현했는가?**
URL 쿼리스트링 `?q=...`을 `request.args.get('q')`로 읽는다.
메모리에 올라온 photos 리스트를 Python 리스트 컴프리헨션으로 필터링한다.
별도의 검색 인덱스나 DB 쿼리 없이 단순 문자열 포함 여부(`in`)로 비교한다.

**Q. 로그인하지 않은 사용자가 내 갤러리에 접근하면?**
```python
user_id = session.get('user_id')
if not user_id:
    return redirect(url_for('auth.login'))
```
`session.get()`이 None을 반환하면 로그인 페이지로 리다이렉트한다.

**Q. 사진을 여러 장 올리면 어떻게 처리하는가?**
`request.files.getlist('fileImage')`로 파일 리스트 전체를 받는다.
for 루프로 파일마다 저장하고 메타데이터를 기록한다.
제목이 있으면 `제목 01`, `제목 02`처럼 번호를 붙인다.

**Q. Blueprint의 `url_prefix`는 무슨 역할인가?**
```python
app.register_blueprint(auth_bp, url_prefix='/auth')
```
auth_bp 안의 모든 라우트 앞에 `/auth`가 붙는다.
`@auth_bp.route('/login')` → 실제 URL은 `/auth/login`

**Q. `render_template()`에서 데이터는 어떻게 전달하는가?**
```python
return render_template('gallery.html', photos=photos, query=query)
```
키워드 인자로 전달한 값들이 Jinja2 템플릿의 변수로 사용된다.
템플릿에서 `{{ photos }}`, `{{ query }}`로 접근 가능하다.

**Q. `send_from_directory`를 왜 쓰는가?**
업로드 이미지는 `static/` 폴더 밖에 있어서 Flask가 자동으로 서빙하지 않는다.
`send_from_directory(IMAGE_PATH, filename)`으로 지정한 폴더에서 직접 파일을 응답으로 보낸다.

**Q. `config.py`에서 경로를 상수로 만드는 이유는?**
```python
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_PATH = os.path.join(BASE_DIR, 'database/images')
```
하드코딩된 경로(`/Users/.../images`)는 다른 컴퓨터에서 실행하면 깨진다.
`__file__`은 항상 현재 파일의 위치를 가리키므로 어디서 실행해도 올바른 절대경로가 만들어진다.

---

## 핵심 흐름 요약

```
사용자 요청
    ↓
Flask 라우트 매칭 (Blueprint)
    ↓
세션 확인 (로그인 필요 여부)
    ↓
데이터 처리
  - 파일 읽기: os.listdir() + json.load()
  - 파일 쓰기: file.save() + json.dump()
  - 필터링: 리스트 컴프리헨션
    ↓
render_template()으로 HTML 생성 (Jinja2)
    ↓
HTTP 응답 반환
```
