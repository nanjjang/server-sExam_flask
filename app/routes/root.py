import json
import os

from flask import Blueprint, redirect, render_template, request, send_from_directory, session, url_for

from config import IMAGE_META_PATH, IMAGE_PATH, THUMB_PATH

root_bp = Blueprint('root', __name__)



def load_image_meta():
    if not os.path.exists(IMAGE_META_PATH):
        return {}
    try:
        with open(IMAGE_META_PATH, 'r', encoding='utf-8') as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        return {}


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
        photos.append({
            'filename': filename,
            'slug': stem,
            'owner': file_owner,
            'title': photo_meta.get('title') or f'Photo {len(photos) + 1:02d}',
            'date': photo_meta.get('uploaded_at') or '',
            'url': image_url,
        })

    return photos[:limit] if limit else photos


@root_bp.route('/blog')
def blog():
    return render_template('blog.html', body_class='news')


@root_bp.route('/')
def root():
    return render_template('home.html', body_class='home')


@root_bp.route('/gallery')
def gallery():
    query = request.args.get('q', '').strip()
    photos = get_gallery_photos()
    if query:
        lowered = query.lower()
        photos = [p for p in photos if lowered in p['title'].lower() or lowered in p['owner'].lower()]
    return render_template('gallery.html', photos=photos, query=query, body_class='gallery')


@root_bp.route('/my-gallery')
def my_gallery():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login'))
    photos = get_gallery_photos(owner=user_id)
    return render_template('my_gallery.html', photos=photos, body_class='gallery')


@root_bp.route('/feature')
def feature():
    return render_template('feature.html', body_class='feature')


@root_bp.route('/reviews')
def reviews():
    return render_template('reviews.html', body_class='reviews')




@root_bp.route('/media/<path:filename>')
def media(filename):
    return send_from_directory(IMAGE_PATH, filename)


@root_bp.route('/thumb/<path:filename>')
def thumbnail(filename):
    return send_from_directory(THUMB_PATH, filename)
