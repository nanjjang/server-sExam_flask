import os

from flask import Blueprint, render_template, request, send_from_directory, url_for

from config import IMAGE_PATH, THUMB_PATH

root_bp = Blueprint('root', __name__)


def get_gallery_photos(limit=4):
    allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
    display_titles = ['바닷가 산책', '부산의 오후', '느린 파도', '도시의 해변']
    display_likes = ['6,923', '9,923', '7,032', '8,249']
    display_dates = ['2026.01.01', '2026.09.13', '2026.11.05', '2026.08.24']
    display_locations = ['Haeundae', 'Busan', 'Blue hour', 'Seaside']
    photos = []

    for filename in sorted(os.listdir(IMAGE_PATH)):
        stem, ext = os.path.splitext(filename)
        if ext.lower() not in allowed_extensions:
            continue

        owner = stem.split('_', 1)[0]
        image_url = url_for('root.media', filename=filename)
        thumb_path = os.path.join(THUMB_PATH, filename)
        if os.path.exists(thumb_path):
            image_url = url_for('root.thumbnail', filename=filename)

        index = len(photos)
        photos.append({
            'filename': filename,
            'owner': owner,
            'title': display_titles[index] if index < len(display_titles) else owner,
            'likes': display_likes[index] if index < len(display_likes) else f"{692312 + index * 299535:,}",
            'date': display_dates[index] if index < len(display_dates) else f"20260{index + 1:02d}{(index * 8 + 1):02d}",
            'location': display_locations[index] if index < len(display_locations) else 'Archive',
            'url': image_url,
        })

    return photos[:limit]


@root_bp.route('/')
def root():
    return render_template('home.html', photos=get_gallery_photos(3), body_class='page-home')


@root_bp.route('/feature')
def feature():
    return render_template('feature.html', body_class='page-feature')


@root_bp.route('/gallery')
def gallery():
    query = request.args.get('q', '').strip()
    photos = get_gallery_photos(12)
    if query:
        lowered_query = query.lower()
        photos = [
            photo for photo in photos
            if lowered_query in photo['title'].lower()
            or lowered_query in photo['owner'].lower()
            or lowered_query in photo['date'].lower()
            or lowered_query in photo['location'].lower()
        ]

    return render_template('gallery.html', photos=photos, query=query, body_class='page-gallery')


@root_bp.route('/media/<path:filename>')
def media(filename):
    return send_from_directory(IMAGE_PATH, filename)


@root_bp.route('/thumb/<path:filename>')
def thumbnail(filename):
    return send_from_directory(THUMB_PATH, filename)
