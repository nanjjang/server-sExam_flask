import json
import os

from flask import Blueprint, redirect, render_template, request, send_from_directory, session, url_for

from config import IMAGE_META_PATH, IMAGE_PATH, THUMB_PATH

root_bp = Blueprint('root', __name__)


NEWS_POSTS = [
    {
        'slug': 'how-to-organize-photos',
        'title': '사진 정리하는 법',
        'excerpt': '쌓여만 가는 사진을 깔끔하게 보관하고 나중에 다시 찾는 방법을 소개합니다.',
        'date': 'Jun 22, 2026',
    },
    {
        'slug': 'pick-your-best-shots',
        'title': '남길 사진 고르는 기준',
        'excerpt': '수백 장 중에서 진짜 남길 한 장을 고르는 나만의 방법을 공유합니다.',
        'date': 'Jun 21, 2026',
    },
    {
        'slug': 'everyday-photo-tips',
        'title': '일상 사진 잘 찍는 법',
        'excerpt': '특별한 장비 없이 스마트폰으로도 기억에 남는 사진을 찍을 수 있습니다.',
        'date': 'Jun 20, 2026',
    },
    {
        'slug': 'why-we-take-photos',
        'title': '사진을 찍는 이유',
        'excerpt': '순간을 기록하는 것이 왜 중요한지, 나중에 꺼내 볼 때의 기분을 이야기합니다.',
        'date': 'Jun 19, 2026',
    },
    {
        'slug': 'season-photo-backgrounds',
        'title': '계절마다 달라지는 배경',
        'excerpt': '봄, 여름, 가을, 겨울 — 계절에 따라 사진 분위기가 이렇게 달라집니다.',
        'date': 'Jun 18, 2026',
    },
    {
        'slug': 'title-your-photos',
        'title': '사진에 제목을 붙이는 습관',
        'excerpt': '업로드할 때 제목을 잘 붙여두면 나중에 찾을 때 훨씬 편합니다.',
        'date': 'Jun 17, 2026',
    },
    {
        'slug': 'golden-hour',
        'title': '골든아워에 찍은 사진은 왜 다를까',
        'excerpt': '해 뜨고 지는 시간대의 빛이 사진을 완전히 다르게 만드는 이유를 이야기합니다.',
        'date': 'Jun 16, 2026',
    },
    {
        'slug': 'photo-angle',
        'title': '같은 장소, 다른 각도',
        'excerpt': '카메라 위치만 조금 바꿔도 전혀 다른 사진이 나옵니다. 각도가 주는 차이를 소개합니다.',
        'date': 'Jun 15, 2026',
    },
    {
        'slug': 'delete-bravely',
        'title': '과감하게 지우는 것도 실력',
        'excerpt': '좋은 사진을 남기려면 아쉬운 사진을 지울 줄도 알아야 합니다.',
        'date': 'Jun 14, 2026',
    },
    {
        'slug': 'background-matters',
        'title': '배경이 사진의 반이다',
        'excerpt': '피사체만큼 배경 선택이 중요합니다. 깔끔한 배경을 고르는 방법을 공유합니다.',
        'date': 'Jun 13, 2026',
    },
]

POPULAR_NEWS_SCORES = {
    'how-to-organize-photos': 100,
    'pick-your-best-shots': 90,
    'everyday-photo-tips': 80,
}


REVIEW_CARDS = [
    {
        'quote': 'Flask Blueprint로 화면별 라우트를 나누고, 템플릿에서 필요한 데이터만 전달하도록 구성했습니다.',
        'name': '라우팅',
        'role': 'routes/root.py, routes/upload.py',
        'initials': 'RT',
        'accent': 'blue',
    },
    {
        'quote': '업로드한 이미지 파일은 images 폴더에 저장하고, 제목과 분류 정보는 JSON 파일에 함께 기록합니다.',
        'name': '데이터 저장',
        'role': 'database/images, image_meta.json',
        'initials': 'DB',
        'accent': 'green',
    },
    {
        'quote': '전체 갤러리와 내 갤러리를 분리해 로그인한 사용자 기준으로 사진을 확인할 수 있게 했습니다.',
        'name': '갤러리',
        'role': 'gallery.html, my_gallery.html',
        'initials': 'GA',
        'accent': 'rose',
    },
    {
        'quote': '사진 제목과 업로더 이름으로 검색할 수 있어 저장된 이미지가 많아져도 원하는 항목을 찾을 수 있습니다.',
        'name': '검색',
        'role': 'query parameter filtering',
        'initials': 'SE',
        'accent': 'gold',
    },
    {
        'quote': '카드 이미지 비율과 버튼 크기를 통일해 화면 캡처 시 큰 규격 차이가 보이지 않도록 정리했습니다.',
        'name': 'UI 정리',
        'role': 'CSS layout cleanup',
        'initials': 'UI',
        'accent': 'violet',
    },
    {
        'quote': '복잡한 장식 코드와 실제 기능과 맞지 않는 문구를 줄여 사진 아카이브 목적에 맞게 다듬었습니다.',
        'name': '코드 정리',
        'role': 'simpler templates and CSS',
        'initials': 'CL',
        'accent': 'steel',
    },
]


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


@root_bp.route('/blog')
def blog():
    posts = get_news_posts()
    hero_post, grid_posts = split_news_index_posts(posts)
    return render_template('blog.html', hero_post=hero_post, posts=grid_posts, body_class='news')


@root_bp.route('/')
def root():
    photos = get_gallery_photos()
    products = [
        {'slug': p['slug'], 'title': p['title'], 'image_url': p['url'], 'collection_label': p['owner'], 'compare_price': p['date'], 'price': p['date']}
        for p in photos
    ]
    return render_template('home.html', products=products, body_class='home')


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
    photos = get_gallery_photos()
    products = [
        {'slug': p['slug'], 'title': p['title'], 'image_url': p['url'], 'collection_label': p['owner'], 'price': p['date']}
        for p in photos
    ]
    return render_template('feature.html', products=products, body_class='feature')


@root_bp.route('/reviews')
def reviews():
    photos = get_gallery_photos(limit=8)
    products = [
        {'slug': p['slug'], 'title': p['title'], 'image_url': p['url']}
        for p in photos
    ]
    return render_template('reviews.html', reviews=REVIEW_CARDS, products=products, body_class='reviews')



@root_bp.route('/products/<slug>')
def product(slug):
    return redirect(url_for('root.gallery'))


@root_bp.route('/media/<path:filename>')
def media(filename):
    return send_from_directory(IMAGE_PATH, filename)


@root_bp.route('/thumb/<path:filename>')
def thumbnail(filename):
    return send_from_directory(THUMB_PATH, filename)
