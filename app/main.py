from flask import Flask, render_template, request, session
from datetime import datetime
import os

app = Flask(__name__)
image_path = 'app/static/images/'

@app.route('/')
def root():
    return render_template('index.html')

@app.route("/upload", methods=['GET', 'POST'])
def upload():
    try:
        if request.method == 'GET':
            return render_template('upload.html')
        if request.method == 'POST':
            # 이미지 업로드
            obj_file = request.files['fileImage']
            # 현재 로그인한 사용자 ID
            client_id = session.get('user_id')

            if not client_id:
                return "로그인이 필요합니다.", 401

            today = datetime.now().strftime("%Y%m%d")
            # ext = os.path.splitext(obj_file.filename)[1]
            # save_name = f"{client_id}_{today}{ext}"
            save_name = f"{client_id}_{today}.jpg"
            obj_file.save(os.path.join(image_path, save_name))

            return render_template('upload.html')

    except Exception as e:
        # 모든 예외 처리, Exception을 사용
        print('Exception : ', e)

if __name__ == '__main__':
    app.run(debug=True)