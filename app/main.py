from flask import Flask, render_template, request, session, redirect, url_for
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json, uuid

app = Flask(__name__)
app.secret_key = 'sunrin-secret-key-2026'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
image_path = os.path.join(BASE_DIR, 'app/database/images')
users_path = os.path.join(BASE_DIR, 'app/database/users')

os.makedirs(users_path, exist_ok=True)
os.makedirs(image_path, exist_ok=True)


def get_user(username):
    filepath = os.path.join(users_path, f"{username}.json")
    if not os.path.exists(filepath):
        return None
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_user(username, password_hash):
    filepath = os.path.join(users_path, f"{username}.json")
    data = {
        'username': username,
        'password': password_hash,
        'created_at': datetime.now().isoformat()
    }
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


@app.route('/')
def root():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()

    if not username or not password:
        return render_template('register.html', error='아이디와 비밀번호를 입력해주세요.')

    if get_user(username):
        return render_template('register.html', error='이미 존재하는 아이디입니다.')

    save_user(username, generate_password_hash(password))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()

    user = get_user(username)
    if not user or not check_password_hash(user['password'], password):
        return render_template('login.html', error='아이디 또는 비밀번호가 올바르지 않습니다.')

    session['user_id'] = username
    return redirect(url_for('root'))


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('root'))


@app.route("/upload", methods=['GET', 'POST'])
def upload():
    try:
        if request.method == 'GET':
            return render_template('upload.html')
        if request.method == 'POST':
            # request.files.getlist() : HTML input[multiple]로 선택된 파일들을 리스트로 반환
            # request.files['key'] 는 단일 파일만 반환하므로 다중 파일엔 getlist() 사용
            files = request.files.getlist('fileImage')
            client_id = session.get('user_id')

            if not client_id:
                return "로그인이 필요합니다.", 401

            for obj_file in files:
                # rsplit('.', 1) : 오른쪽에서 1번만 '.'으로 분리 → ['파일명', '확장자']
                # 예) 'photo.test.jpg' → ['photo.test', 'jpg']
                ext = obj_file.filename.rsplit('.', 1)[-1]

                # UUID(Universally Unique Identifier) : 전 세계적으로 고유함이 보장되는 128bit 식별자
                # uuid4() : 완전 랜덤 기반 UUID 생성 (가장 일반적으로 사용)
                # .hex : UUID를 하이픈 없는 32자리 16진수 문자열로 반환
                # 예) 'a3f2c1d4e5b6...' (32자)
                # 인덱스(_0, _1) 대신 UUID를 쓰는 이유:
                #   - 동시 요청 시 인덱스는 충돌 가능, UUID는 충돌 확률이 사실상 0
                #   - 업로드 순서나 총 개수를 외부에서 추측할 수 없어 보안에 유리
                save_name = f"{client_id}_{uuid.uuid4().hex}.{ext}"
                obj_file.save(os.path.join(image_path, save_name))

            return render_template('upload.html')

    except Exception as e:
        print('Exception : ', e)


if __name__ == '__main__':
    app.run(debug=True)
