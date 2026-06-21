import json
import os
import uuid
from datetime import datetime
from flask import Blueprint, redirect, render_template, request, session, url_for
from config import IMAGE_META_PATH, IMAGE_PATH

upload_bp = Blueprint('upload', __name__)

PHOTO_TAGS = {
    'after-effects': 'Seaside',
    'figma-templates': 'City',
    'jitter': 'Moments',
    'bundles': 'Stories',
}


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

            original_title = os.path.splitext(obj_file.filename)[0].replace('_', ' ').replace('-', ' ').strip()
            display_title = photo_title or original_title or PHOTO_TAGS[photo_tag]
            if len(files) > 1 and photo_title:
                display_title = f"{photo_title} {index + 1:02d}"

            meta[save_name] = {
                'title': display_title,
                'collection': photo_tag,
                'uploaded_by': client_id,
                'uploaded_at': datetime.now().strftime('%Y.%m.%d'),
            }

        if saved_count:
            save_image_meta(meta)

        return redirect(url_for('root.gallery'))

    except Exception as e:
        print('Exception : ', e)
        return redirect(url_for('upload.upload'))
