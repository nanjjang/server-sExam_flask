import os
import uuid
from flask import Blueprint, redirect, render_template, request, session, url_for
from config import IMAGE_PATH

upload_bp = Blueprint('upload', __name__)


@upload_bp.route('', methods=['GET', 'POST'])
@upload_bp.route('/', methods=['GET', 'POST'])
def upload():
    try:
        if request.method == 'GET':
            return render_template('upload.html', body_class='page-upload')

        files = request.files.getlist('fileImage')
        client_id = session.get('user_id')

        if not client_id:
            return redirect(url_for('auth.login'))

        for obj_file in files:
            if not obj_file.filename:
                continue
            ext = obj_file.filename.rsplit('.', 1)[-1]
            save_name = f"{client_id}_{uuid.uuid4().hex}.{ext}"
            obj_file.save(os.path.join(IMAGE_PATH, save_name))

        return redirect(url_for('root.gallery'))

    except Exception as e:
        print('Exception : ', e)
