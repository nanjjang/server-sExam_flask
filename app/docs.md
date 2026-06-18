https://mainia.tistory.com/7199 -> 서버에 이미지 올리기

---

학번  20613

이름  윤준서

프로젝트명  :  photoArchive

---

## 1. 프로젝트 개요

**(1) 주제** : 개인의 사진을 보관 및 공유 할 수 있는 아카이브 서비스

**(2) 목적 (서비스 대상 및 기대 효과)**: 갤러리 혹은 디스크에 사진들을 저장하면 많은 용량이 소모 된다.
icloud 혹은 googleOne 과 같은 온라인 저장소를 구독해서 사용하게되면 한달에 10만원 정도씩 까일수있습니다.
이를 조금이나마 해결하고자 무료 사진 아카이브를 개발하여 다양한 사람들이 자신들의 사진을 공유 및 보관 할 수 있도록 하고자 합니다.

---

## 2. 데이터 설계

사용자 데이터는 JSON 파일로 관리한다. (`database/users/{username}.json`)

| 필드명 | 타입 | 설명 |
|---|---|---|
| username | String | 사용자 아이디 (고유 식별자, 파일명과 동일) |
| password | String | 해시된 비밀번호 (werkzeug scrypt) |
| created_at | String | 계정 생성 일시 (ISO 8601) |

이미지 파일은 `database/images/` 에 저장한다. 파일명 규칙: `{username}_{uuid4}.{ext}`

- uuid4 를 사용하는 이유: 동시 업로드 시 충돌 방지, 업로드 순서 추측 불가로 보안 강화

---

## 3. 디렉토리 구조

```
app/
├── main.py                  # Flask 라우터 및 비즈니스 로직
├── docs.md                  # 설계 문서
├── css/
│   └── index.css
├── templates/
│   ├── base.html            # 공통 레이아웃 (nav, footer)
│   ├── index.html           # 홈 페이지
│   ├── login.html           # 로그인 페이지
│   ├── register.html        # 회원가입 페이지
│   └── upload.html          # 사진 업로드 페이지
└── database/
    ├── users/               # 사용자 JSON 파일
    └── images/              # 업로드된 이미지 파일
```

---

## 4. URL 설계

| URL | 메서드 | 기능 | 로그인 필요 |
|---|---|---|---|
| / | GET | 메인 페이지 출력 | X |
| /register | GET | 회원가입 폼 출력 | X |
| /register | POST | 회원가입 처리 (중복 검사 → 저장 → 로그인 이동) | X |
| /login | GET | 로그인 폼 출력 | X |
| /login | POST | 로그인 처리 (비밀번호 검증 → 세션 저장 → 홈 이동) | X |
| /logout | GET | 로그아웃 (세션 삭제 → 홈 이동) | O |
| /upload | GET | 사진 업로드 폼 출력 | O |
| /upload | POST | 사진 업로드 처리 (다중 파일 저장) | O |

---

## 5. HTML 페이지 설계

**(1) base.html** — 모든 페이지가 상속하는 공통 레이아웃

- 로그인 상태에 따라 nav 메뉴 조건부 출력 (`session.get('user_id')`)
- 로그인 시: 사용자명 환영 문구 / 사진 업로드 / 로그아웃
- 비로그인 시: 로그인 / 회원가입

**(2) index.html** — 홈 페이지, 서비스 소개 문구 출력

**(3) register.html** — 회원가입 폼

- 입력: username (text), password (password)
- 오류 시 `{{ error }}` 로 빨간 메시지 출력

**(4) login.html** — 로그인 폼

- 입력: username (text), password (password)
- 오류 시 `{{ error }}` 로 빨간 메시지 출력

**(5) upload.html** — 사진 업로드

- `<input type="file" name="fileImage" multiple>` 로 다중 파일 선택
- `enctype="multipart/form-data"` 필수

---

## 6. 기능 흐름 설계

**회원가입**
1. GET /register → 폼 출력
2. POST /register → 빈값 검사 → 중복 아이디 검사 → 비밀번호 해시 → JSON 저장 → /login 이동

**로그인**
1. GET /login → 폼 출력
2. POST /login → 사용자 파일 조회 → 비밀번호 검증 → session['user_id'] 저장 → / 이동

**사진 업로드**
1. GET /upload → 폼 출력
2. POST /upload → 로그인 여부 확인 (미인증 시 401) → 파일 목록 수신 → 확장자 추출 → UUID 파일명 생성 → 저장

---

## 7. 보안 설계

| 항목 | 적용 방법 |
|---|---|
| 비밀번호 해시 | werkzeug `generate_password_hash()` — scrypt 알고리즘 |
| 비밀번호 검증 | werkzeug `check_password_hash()` — 원문 저장 없이 해시 비교 |
| 세션 관리 | Flask session + secret_key 로 서버 측 서명 쿠키 |
| 파일명 충돌 방지 | UUID v4 (128bit 랜덤) — 충돌 확률 사실상 0 |
| 업로드 인증 | POST /upload 에서 session 확인, 미인증 시 401 반환 |

