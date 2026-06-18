import os
import uuid
from flask import Blueprint, render_template, request, session
from config import IMAGE_PATH

upload_bp = Blueprint('upload', __name__)


@upload_bp.route('/upload', methods=['GET', 'POST'])
def upload():
    try:
        if request.method == 'GET':
            return render_template('upload.html')

        files = request.files.getlist('fileImage')
        client_id = session.get('user_id')

        if not client_id:
            return "로그인이 필요합니다.", 401

        for obj_file in files:
            ext = obj_file.filename.rsplit('.', 1)[-1]
            save_name = f"{client_id}_{uuid.uuid4().hex}.{ext}"
            obj_file.save(os.path.join(IMAGE_PATH, save_name))

        return render_template('upload.html')

    except Exception as e:
        print('Exception : ', e)
