# photoArchive 프로젝트 완전 분석

---

## 전체 구조 한눈에 보기

```
요청(브라우저) → wsgi.py → app.py → routes/ → templates/
                                              → models/
                                              → database/
```

파일별 역할:
```
app.py          Flask 앱 생성, 설정, 라우트 등록
wsgi.py         배포용 진입점
config.py       경로 설정, 환경변수 로드
routes/
  __init__.py   Blueprint 등록 (라우트 묶음 연결)
  root.py       메인 페이지, 갤러리, 블로그 등 일반 라우트
  upload.py     사진 업로드 라우트
  auth.py       로그인, 회원가입, 로그아웃 라우트
models/
  user.py       유저 데이터 읽기/저장 함수
database/
  images/       업로드된 원본 이미지 저장 폴더
  thumbs/       썸네일 이미지 저장 폴더
  users/        유저 정보 JSON 파일 저장 폴더
  image_meta.json  모든 사진의 제목, 날짜, 업로더 정보
```

---

## HTTP 메서드 기본 개념 (GET vs POST)

**GET** — 데이터를 가져올 때
- URL에 정보가 담김 (`/gallery?q=서울`)
- 브라우저 주소창에 보임
- 북마크 가능, 뒤로가기 가능
- 서버 데이터를 바꾸지 않음

**POST** — 데이터를 보낼 때
- URL에 정보가 안 담김 (body에 숨겨서 전송)
- 파일, 비밀번호 등 민감하거나 큰 데이터 전송
- 서버 데이터를 바꾸는 행위 (저장, 로그인 등)

---

## wsgi.py

```python
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app import app as application
```

**역할:** 배포용 진입점

**왜 필요한가?**
`python app.py`는 개발용 Flask 내장 서버를 쓴다.
실제 서버에선 gunicorn 같은 전문 WSGI 서버가 앱을 실행하는데,
gunicorn은 `application`이라는 이름의 객체를 찾는다.
그래서 `app`을 `application`이라는 이름으로 export하는 파일이 필요하다.

**sys.path.insert(0, ...)는 왜?**
파이썬이 `import app` 할 때 어느 폴더에서 찾아야 할지 알려주는 것.
`os.path.abspath(__file__)`로 이 파일의 절대 경로를 구하고,
`os.path.dirname()`으로 폴더 경로만 추출해서 검색 경로에 추가.

**실행 방법:**
- 개발: `python app.py`
- 배포: `gunicorn wsgi:application`

---

## config.py

```python
import os
from dotenv import load_dotenv
load_dotenv()

secret_key = os.getenv("SECRET_KEY")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_PATH = os.path.join(BASE_DIR, 'database/images')
THUMB_PATH = os.path.join(BASE_DIR, 'database/thumbs')
USERS_PATH = os.path.join(BASE_DIR, 'database/users')
IMAGE_META_PATH = os.path.join(BASE_DIR, 'database/image_meta.json')

os.makedirs(USERS_PATH, exist_ok=True)
os.makedirs(IMAGE_PATH, exist_ok=True)
os.makedirs(THUMB_PATH, exist_ok=True)
```

**역할:** 프로젝트 전역 설정값 정의

**load_dotenv():**
`.env` 파일을 읽어서 환경변수로 등록한다.
`.env` 파일 안에 `SECRET_KEY=abc123` 이런 식으로 써놓으면
`os.getenv("SECRET_KEY")`로 가져올 수 있다.
`.env` 파일은 git에 올리지 않아야 한다 — 비밀키가 노출되면 세션 위조가 가능하기 때문.

**BASE_DIR과 경로 설정:**
`__file__`은 현재 파이썬 파일의 경로다.
`os.path.abspath()`로 절대경로로 바꾸고,
`os.path.dirname()`으로 파일명을 뺀 폴더 경로만 남긴다.
예: config.py가 `/home/user/app/config.py`에 있으면
BASE_DIR = `/home/user/app`

이렇게 하면 어느 폴더에서 실행하든 항상 올바른 경로가 된다.
`'./database/images'` 같은 상대경로는 실행 위치에 따라 달라지기 때문에 위험하다.

**os.makedirs(..., exist_ok=True):**
폴더가 없으면 만들고, 이미 있으면 에러 없이 넘어간다.
서버를 처음 실행할 때 database 폴더들이 자동 생성된다.

---

## app.py

```python
from flask import Flask
from config import secret_key
from routes import register_routes

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.secret_key = secret_key

register_routes(app)

if __name__ == '__main__':
    app.run(debug=True)
```

**역할:** Flask 앱 객체 생성 및 초기화

**Flask(__name__, ...):**
`__name__`은 현재 파일의 모듈 이름이다.
Flask가 템플릿, 정적파일 등의 위치를 찾을 때 이 값을 기준으로 삼는다.
`static_folder='static'` → CSS, JS, 이미지 등 정적 파일의 폴더 이름
`static_url_path='/static'` → 브라우저에서 `/static/css/style.css`로 접근 가능

**app.secret_key:**
세션(session)을 암호화할 때 쓰는 키.
Flask 세션은 쿠키에 저장되는데, 이 키로 서명해서 위변조를 막는다.
이 키가 노출되면 누구나 세션을 조작해서 로그인 상태를 만들 수 있다.

**register_routes(app):**
routes/__init__.py의 함수를 호출해서 모든 Blueprint를 등록한다.

**if __name__ == '__main__':**
`python app.py`로 직접 실행할 때만 동작한다.
`import app`으로 불러올 때는 실행되지 않는다.
`debug=True`는 개발 중에 코드 수정 시 자동 재시작, 에러 페이지 상세 출력.
배포 시엔 절대 debug=True 하면 안 된다 (소스코드가 브라우저에 노출될 수 있음).

---

## routes/__init__.py

```python
from flask import Flask
from .auth import auth_bp
from .upload import upload_bp
from .root import root_bp

def register_routes(app: Flask):
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(upload_bp, url_prefix='/upload')
    app.register_blueprint(root_bp, url_prefix='/')
```

**역할:** 모든 Blueprint를 앱에 등록

**Blueprint란?**
라우트를 기능별로 묶어서 관리하는 단위다.
모든 라우트를 app.py 하나에 넣으면 파일이 너무 커진다.
Blueprint로 나눠서 auth(인증), upload(업로드), root(나머지)로 분리했다.

**url_prefix:**
- `auth_bp`에 `/auth` → 모든 auth 라우트 앞에 `/auth`가 붙음
  - `/register` → 실제 URL은 `/auth/register`
  - `/login` → 실제 URL은 `/auth/login`
- `upload_bp`에 `/upload` → `/upload/`
- `root_bp`에 `/` → 그대로 (`/gallery`, `/blog` 등)

**`.auth`에서 점(.)의 의미:**
같은 패키지(routes 폴더) 안에 있는 파일을 가져오는 상대 import.
`from routes.auth import auth_bp`와 동일하다.

---

## routes/auth.py

### Blueprint 선언

```python
auth_bp = Blueprint('auth', __name__)
```

`'auth'`는 이 Blueprint의 이름이다.
`url_for('auth.login')` 처럼 이름으로 URL을 역으로 찾을 때 사용한다.

---

### register() — 회원가입

```python
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html', body_class='auth')

    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()

    if not username or not password:
        return render_template('register.html', error='아이디와 비밀번호를 입력해주세요.', body_class='auth')

    if get_user(username):
        return render_template('register.html', error='이미 존재하는 아이디입니다.', body_class='auth')

    save_user(username, generate_password_hash(password))
    return redirect(url_for('auth.login'))
```

**실제 URL:** `/auth/register`

**왜 GET과 POST 둘 다?**
같은 URL에서 두 가지 역할을 한다.
- GET: 회원가입 폼 화면을 보여준다
- POST: 폼을 제출했을 때 처리한다

하나의 라우트로 두 역할을 처리하는 패턴 — 폼 URL과 처리 URL이 같아서 관리가 편하다.

**흐름:**
1. 브라우저가 `/auth/register`에 GET 요청 → 폼 HTML 반환
2. 사용자가 폼 작성 후 제출 → POST 요청
3. username, password를 form에서 꺼냄
4. `.strip()`으로 앞뒤 공백 제거 (실수로 스페이스 입력한 경우 처리)
5. 빈 값이면 에러 메시지와 함께 폼 다시 보여줌
6. `get_user(username)`으로 이미 있는 아이디인지 확인
7. 없으면 `generate_password_hash(password)`로 비밀번호 암호화 후 저장
8. 성공하면 로그인 페이지로 redirect

**generate_password_hash():**
비밀번호를 그대로 저장하면 DB가 털렸을 때 모든 비밀번호가 노출된다.
해시 함수로 변환하면 원래 값을 복원할 수 없다.
예: `"1234"` → `"pbkdf2:sha256:260000$abc...xyz"`

---

### login() — 로그인

```python
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html', body_class='auth')

    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()

    user = get_user(username)
    if not user or not check_password_hash(user['password'], password):
        return render_template('login.html', error='아이디 또는 비밀번호가 올바르지 않습니다.', body_class='auth')

    session['user_id'] = username
    return redirect(url_for('root.root'))
```

**실제 URL:** `/auth/login`

**흐름:**
1. GET → 로그인 폼 보여줌
2. POST → username, password 꺼냄
3. `get_user(username)`으로 해당 유저의 저장된 데이터 조회
4. 유저가 없거나 비밀번호가 틀리면 에러
5. `check_password_hash(저장된해시, 입력한비밀번호)` → 해시와 비교
6. 성공하면 `session['user_id'] = username`으로 세션에 저장
7. 홈으로 redirect

**왜 에러 메시지를 "아이디 또는 비밀번호"로 합쳐서 쓰나?**
"아이디가 없습니다"라고 따로 알려주면 공격자가 존재하는 아이디를 골라낼 수 있다.
합쳐서 알려주면 아이디가 없는 건지 비밀번호가 틀린 건지 모른다.

**session이란?**
로그인 상태를 유지하는 방법이다.
Flask는 세션 데이터를 서명된 쿠키로 브라우저에 저장한다.
이후 모든 요청에서 `session['user_id']`를 확인해서 로그인 여부를 판단한다.

---

### logout() — 로그아웃

```python
@auth_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('root.root'))
```

**실제 URL:** `/auth/logout`

**왜 GET만?**
로그아웃은 데이터를 보내지 않고 그냥 링크 클릭으로 처리한다.
보안상 POST가 맞지만 이 프로젝트 수준에선 GET으로도 무방하다.

**session.pop('user_id', None):**
세션에서 user_id를 삭제한다.
두 번째 인자 `None`은 user_id가 없을 때 에러 대신 None을 반환하라는 의미.
이후 요청에서 `session.get('user_id')`는 None을 반환 → 로그인 안 된 상태.

---

## models/user.py

```python
def get_user(username):
    filepath = os.path.join(USERS_PATH, f"{username}.json")
    if not os.path.exists(filepath):
        return None
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_user(username, password_hash):
    filepath = os.path.join(USERS_PATH, f"{username}.json")
    data = {
        'username': username,
        'password': password_hash,
        'created_at': datetime.now().isoformat()
    }
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
```

**역할:** 유저 데이터를 JSON 파일로 저장/조회

**왜 DB 대신 JSON 파일?**
이 프로젝트는 DB 없이 파일 시스템만 사용한다.
유저 1명당 파일 1개 (`database/users/asdf.json` 같은 형태).

**get_user(username):**
`username.json` 파일이 있으면 읽어서 딕셔너리로 반환.
없으면 None 반환 → auth.py에서 "없는 유저"로 처리.

**save_user(username, password_hash):**
유저 정보를 JSON으로 저장.
`password_hash`는 이미 암호화된 값 — 원본 비밀번호는 저장하지 않는다.
`ensure_ascii=False` → 한글이 깨지지 않게.
`indent=2` → 파일을 사람이 읽기 좋게 들여쓰기.

---

## routes/upload.py

### upload() — 사진 업로드

```python
@upload_bp.route('', methods=['GET', 'POST'])
@upload_bp.route('/', methods=['GET', 'POST'])
def upload():
    try:
        if request.method == 'GET':
            return render_template('upload.html', photo_tags=PHOTO_TAGS, body_class='upload')

        files = request.files.getlist('fileImage')
        client_id = session.get('user_id')
        photo_title = request.form.get('photoTitle', '').strip()
        photo_tag = request.form.get('photoTag', 'jitter').strip()

        if not client_id:
            return redirect(url_for('auth.login'))

        if photo_tag not in PHOTO_TAGS:
            photo_tag = 'jitter'

        meta = load_image_meta()
        saved_count = 0

        for index, obj_file in enumerate(files):
            if not obj_file.filename:
                continue
            ext = obj_file.filename.rsplit('.', 1)[-1]
            save_name = f"{client_id}_{uuid.uuid4().hex}.{ext}"
            obj_file.save(os.path.join(IMAGE_PATH, save_name))
            saved_count += 1
            ...

        if saved_count:
            save_image_meta(meta)

        return redirect(url_for('root.gallery'))
    except Exception as e:
        print('Exception : ', e)
        return redirect(url_for('upload.upload'))
```

**실제 URL:** `/upload` 또는 `/upload/`

**왜 라우트가 두 개 (`''`와 `'/'`)?**
`/upload`와 `/upload/` 둘 다 같은 함수로 처리하기 위해서.
URL 끝에 슬래시가 있든 없든 동일하게 동작한다.

**왜 POST를 써야 하나?**
파일 업로드는 반드시 POST여야 한다.
GET은 URL에 데이터를 담는데, 파일을 URL에 담을 수 없다.
또한 HTML form에서 `enctype="multipart/form-data"`와 함께 POST를 써야 파일이 전송된다.

**request.files.getlist('fileImage'):**
`<input type="file" name="fileImage" multiple>`에서 올라온 파일들.
`getlist`로 여러 파일을 한꺼번에 받는다.

**왜 로그인 체크를 POST에서만 하나?**
GET(화면 보여주기)은 로그인 없이도 폼을 볼 수 있게 했다.
실제 업로드(POST) 시점에 로그인 여부를 확인한다.
로그인 안 됐으면 로그인 페이지로 보낸다.

**파일명을 왜 uuid로 바꾸나?**
사용자가 올린 파일명 그대로 저장하면 문제가 생긴다.
- 두 사람이 같은 이름의 파일을 올리면 덮어씌워진다
- 한글 파일명, 특수문자 등으로 오류 날 수 있다
- `{client_id}_{uuid}.jpg` 형식으로 저장하면 절대 충돌 없음
- 파일명 앞부분이 곧 업로더 아이디가 됨 → 내 갤러리 필터링에 활용

**uuid.uuid4().hex:**
랜덤한 고유 문자열 생성. 예: `6250f517b0494cc68ac270d78254fdfd`
`.hex`를 붙이면 숫자와 소문자만 나온다 (하이픈 없음).

**메타데이터를 왜 따로 JSON에 저장하나?**
이미지 파일 자체에는 제목, 날짜, 카테고리 같은 정보를 저장할 수 없다.
별도 `image_meta.json`에 파일명을 키로 해서 정보를 저장한다.

```json
{
  "asdf_abc123.jpg": {
    "title": "서울 노을",
    "collection": "jitter",
    "uploaded_by": "asdf",
    "uploaded_at": "2026.06.22"
  }
}
```

**try/except:**
파일 저장 도중 어떤 에러가 나도 서버가 죽지 않고 업로드 페이지로 돌아간다.

---

### load_image_meta() / save_image_meta()

```python
def load_image_meta():
    if not os.path.exists(IMAGE_META_PATH):
        return {}
    try:
        with open(IMAGE_META_PATH, 'r', encoding='utf-8') as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        return {}

def save_image_meta(meta):
    with open(IMAGE_META_PATH, 'w', encoding='utf-8') as file:
        json.dump(meta, file, ensure_ascii=False, indent=2)
```

**load_image_meta():**
JSON 파일이 없으면 빈 딕셔너리 반환.
파일이 깨졌거나 읽기 실패해도 에러 없이 빈 딕셔너리 반환.
여기에 새 파일 정보를 추가한 뒤 다시 저장하는 흐름.

**왜 읽고 → 추가하고 → 다시 쓰나?**
JSON 파일에 한 줄 추가하는 기능이 없다.
통째로 읽어서 딕셔너리에 키를 추가하고, 통째로 다시 쓴다.

---

## routes/root.py

### load_image_meta()

upload.py에도 동일한 함수가 있다. (코드 중복)
root.py에서는 읽기 전용으로만 사용하고, upload.py에서는 읽고 쓴다.

---

### get_gallery_photos(owner=None, limit=None)

```python
def get_gallery_photos(owner=None, limit=None):
    allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
    meta = load_image_meta()
    photos = []

    filenames = []
    if os.path.exists(IMAGE_PATH):
        for filename in os.listdir(IMAGE_PATH):
            _, ext = os.path.splitext(filename)
            if ext.lower() in allowed_extensions:
                filenames.append(filename)

    filenames.sort(key=lambda f: os.path.getmtime(os.path.join(IMAGE_PATH, f)), reverse=True)

    for filename in filenames:
        stem, _ = os.path.splitext(filename)
        file_owner = stem.split('_', 1)[0]

        if owner and file_owner != owner:
            continue

        image_url = url_for('root.media', filename=filename)
        thumb_path = os.path.join(THUMB_PATH, filename)
        if os.path.exists(thumb_path):
            image_url = url_for('root.thumbnail', filename=filename)

        photo_meta = meta.get(filename, {})
        photos.append({...})

    return photos[:limit] if limit else photos
```

**역할:** 갤러리에 표시할 사진 목록을 만드는 핵심 함수

**왜 라우트가 아니고 일반 함수인가?**
여러 라우트(홈, 갤러리, 내 갤러리, 기능소개 등)에서 공통으로 필요하다.
중복을 없애기 위해 함수로 분리했다.

**allowed_extensions:**
이미지 파일만 필터링. txt, zip 같은 파일이 섞여 있어도 무시.

**os.listdir():**
폴더 안의 파일 이름 목록을 가져온다. 순서는 보장 안 됨.

**filenames.sort(key=lambda f: os.path.getmtime(...), reverse=True):**
파일의 수정 시간(mtime) 기준으로 최신순 정렬.
`reverse=True` → 최신이 앞으로.
`lambda f: ...` → 각 파일명으로 수정 시간을 구하는 함수.

**stem.split('_', 1)[0]:**
파일명이 `asdf_uuid.jpg`일 때 `_`를 기준으로 1번만 자름.
`['asdf', 'uuid']` → `[0]` → `'asdf'` = 업로더 아이디.

**owner 파라미터:**
`owner=None`이면 전체 사진.
`owner='asdf'`면 asdf가 올린 사진만. (내 갤러리에서 사용)

**limit 파라미터:**
`limit=8`이면 최대 8장만 반환.

**url_for('root.media', filename=filename):**
`/media/파일명.jpg` URL을 생성한다.
썸네일이 있으면 `/thumb/파일명.jpg` URL로 대신 사용.

---

### get_news_posts()

```python
def get_news_posts():
    photos = get_gallery_photos()
    posts = []
    for index, post in enumerate(NEWS_POSTS):
        photo = photos[index % len(photos)] if photos else None
        posts.append({
            **post,
            'image_url': photo['url'] if photo else '',
            'image_alt': photo['title'] if photo else post['title'],
        })
    return posts
```

**역할:** 블로그 게시글 목록에 이미지를 붙여서 반환

**왜 사진 갤러리 이미지를 블로그에 붙이나?**
블로그 글에 별도 이미지가 없기 때문에 갤러리에 올라온 사진을 재활용한다.
`index % len(photos)` → 사진이 10장이고 글이 10개면 각각 1장씩.
사진보다 글이 많으면 처음 사진부터 다시 순환.

**`**post`:**
딕셔너리를 펼쳐서 모든 키-값을 복사한다.
`{**post, 'image_url': ...}` → post의 내용 + image_url 추가.

---

### split_news_index_posts(posts)

```python
def split_news_index_posts(posts):
    recent_posts = list(enumerate(posts[:6]))
    if not recent_posts:
        return None, []
    hero_index, hero_post = max(
        recent_posts,
        key=lambda item: (POPULAR_NEWS_SCORES.get(item[1]['slug'], 0), -item[0]),
    )
    remaining_posts = [post for index, post in enumerate(posts) if index != hero_index]
    return hero_post, remaining_posts
```

**역할:** 블로그 목록에서 상단에 크게 표시할 대표 글(hero)과 나머지를 분리

**enumerate(posts[:6]):**
앞 6개만 보고 그 중에서 대표 글을 고른다.

**max(..., key=...):**
가장 점수가 높은 글을 고른다.
`POPULAR_NEWS_SCORES`에 slug별 점수가 있고, 점수가 같으면 순서가 빠른 것 우선 (`-item[0]`).

**remaining_posts:**
hero로 뽑힌 글을 제외한 나머지 전체 (6개 이후 글 포함).

---

### blog() — 블로그 페이지

```python
@root_bp.route('/blog')
def blog():
    posts = get_news_posts()
    hero_post, grid_posts = split_news_index_posts(posts)
    return render_template('blog.html', hero_post=hero_post, posts=grid_posts, body_class='news')
```

**왜 GET만?**
데이터를 읽어서 보여주기만 한다. 서버 데이터를 바꾸지 않는다.

---

### root() — 홈 페이지

```python
@root_bp.route('/')
def root():
    photos = get_gallery_photos()
    products = [
        {'slug': p['slug'], 'title': p['title'], 'image_url': p['url'], ...}
        for p in photos
    ]
    return render_template('home.html', products=products, body_class='home')
```

**왜 GET만?**
홈 화면은 보여주기만 한다.

**products로 변수명 바꾸는 이유:**
원래 쇼핑몰 템플릿을 기반으로 만들었기 때문에 템플릿이 `product`라는 변수를 기대한다.

---

### gallery() — 전체 갤러리

```python
@root_bp.route('/gallery')
def gallery():
    query = request.args.get('q', '').strip()
    photos = get_gallery_photos()
    if query:
        lowered = query.lower()
        photos = [p for p in photos if lowered in p['title'].lower() or lowered in p['owner'].lower()]
    return render_template('gallery.html', photos=photos, query=query, body_class='gallery')
```

**왜 GET만?**
검색도 데이터를 읽는 행위다. 서버를 바꾸지 않는다.

**request.args.get('q', ''):**
URL의 쿼리스트링을 읽는다.
`/gallery?q=서울` → `query = '서울'`
기본값 `''`으로 q가 없으면 빈 문자열.

**왜 검색에 POST 안 쓰나?**
GET을 쓰면 검색 결과 URL을 북마크하거나 공유할 수 있다.
`/gallery?q=서울`을 친구에게 보내면 친구도 같은 검색 결과를 볼 수 있다.
POST는 URL에 검색어가 남지 않아서 공유가 안 된다.

**lowered = query.lower():**
대소문자 구분 없이 검색하기 위해 모두 소문자로 통일.
`'Seoul'`과 `'seoul'` 둘 다 매칭되게.

---

### my_gallery() — 내 갤러리

```python
@root_bp.route('/my-gallery')
def my_gallery():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login'))
    photos = get_gallery_photos(owner=user_id)
    return render_template('my_gallery.html', photos=photos, body_class='gallery')
```

**왜 GET만?**
보여주기만 한다.

**왜 로그인 체크를 하나?**
내 갤러리는 로그인한 사람만 볼 수 있어야 한다.
`session.get('user_id')`가 None이면 로그인 안 된 상태 → 로그인 페이지로.

**get_gallery_photos(owner=user_id):**
전체 사진 중 내가 올린 것만 필터링.

---

### product(slug) — 개별 사진 상세

```python
@root_bp.route('/products/<slug>')
def product(slug):
    return redirect(url_for('root.gallery'))
```

갤러리로 redirect만 한다. (상세 페이지 없음)
홈 화면 카드 클릭 시 이 URL로 오는데, 상세 페이지 대신 갤러리로 보낸다.

---

### media(filename) / thumbnail(filename) — 이미지 파일 서빙

```python
@root_bp.route('/media/<path:filename>')
def media(filename):
    return send_from_directory(IMAGE_PATH, filename)

@root_bp.route('/thumb/<path:filename>')
def thumbnail(filename):
    return send_from_directory(THUMB_PATH, filename)
```

**왜 GET만?**
파일을 읽어서 전달하는 행위다.

**왜 라우트로 만들었나?**
`database/images/`는 Flask의 `static/` 폴더 밖에 있다.
Flask는 `static/` 폴더만 자동으로 서빙하기 때문에,
다른 폴더의 파일은 이렇게 라우트로 직접 서빙해야 한다.

**send_from_directory(폴더, 파일명):**
지정한 폴더에서 파일을 찾아 HTTP 응답으로 반환.
파일 확장자에 맞는 Content-Type 헤더 자동 설정.
경로 탈출 공격(`../../etc/passwd`) 자동 차단.

**`<path:filename>`:**
`<string:filename>`은 `/`를 포함할 수 없다.
`<path:filename>`은 `/`포함 중첩 경로도 받을 수 있다.

---

## 전체 요청 흐름 예시

### 사진 업로드 전체 흐름

```
1. 사용자가 /upload 접속 (GET)
   → upload() 실행
   → upload.html 반환 (폼 화면)

2. 사용자가 사진 선택 후 제출 (POST)
   → upload() 실행
   → session에서 user_id 확인
   → 로그인 안 됐으면 /auth/login으로 redirect
   → 파일마다 uuid 파일명 생성
   → database/images/에 저장
   → image_meta.json에 정보 추가
   → /gallery로 redirect

3. 사용자가 /gallery 접속 (GET)
   → gallery() 실행
   → get_gallery_photos() → images 폴더 스캔
   → gallery.html에 photos 전달 → 화면 렌더링

4. 브라우저가 <img src="/media/파일명.jpg"> 렌더링
   → GET /media/파일명.jpg
   → media() 실행
   → send_from_directory로 이미지 파일 반환
```

### 로그인 전체 흐름

```
1. /auth/login (GET) → 로그인 폼 표시
2. 폼 제출 (POST)
   → DB(JSON)에서 유저 조회
   → 비밀번호 해시 비교
   → 성공: session['user_id'] = username → 홈으로
   → 실패: 에러 메시지와 함께 폼 다시 표시
3. 이후 모든 요청에서 session['user_id']로 로그인 상태 유지
4. /auth/logout → session에서 user_id 삭제 → 홈으로
```

---

## 자주 나올 수 있는 질문 정리

**Q. GET과 POST의 차이는?**
GET은 데이터를 가져오는 것, POST는 데이터를 보내는 것.
GET은 URL에 데이터가 보이고, POST는 숨겨진다.
파일 업로드, 로그인은 반드시 POST.

**Q. Blueprint를 왜 쓰나?**
라우트를 기능별로 파일을 분리해서 관리하기 위해.
모든 라우트가 하나의 파일에 있으면 유지보수가 어렵다.

**Q. 세션은 어디에 저장되나?**
Flask 기본 세션은 브라우저 쿠키에 저장된다.
secret_key로 서명해서 위변조를 막는다.
서버엔 저장 안 됨 → 서버 재시작해도 세션 유지.

**Q. 비밀번호를 왜 해시로 저장하나?**
원본을 저장하면 파일이 털렸을 때 모든 비밀번호 노출.
해시는 원본 복원 불가. 로그인 시 같은 해시가 나오는지 비교.

**Q. uuid를 왜 파일명에 쓰나?**
중복 방지. 두 사람이 같은 이름의 파일을 올려도 절대 충돌 안 남.

**Q. image_meta.json을 왜 쓰나?**
이미지 파일엔 제목, 날짜 같은 메타정보를 저장할 수 없음.
별도 JSON 파일에 파일명을 키로 해서 정보를 관리.

**Q. render_template과 redirect의 차이는?**
`render_template` → HTML을 만들어서 바로 응답.
`redirect` → "이 URL로 다시 요청하세요"라고 브라우저에 알림 (302 응답).
폼 제출 후 redirect를 쓰는 이유: 새로고침하면 폼이 다시 제출되는 문제 방지.

**Q. url_for를 왜 쓰나?**
URL을 하드코딩하면 나중에 경로가 바뀔 때 전부 수정해야 한다.
`url_for('auth.login')`은 login 함수의 URL을 자동으로 찾아준다.
