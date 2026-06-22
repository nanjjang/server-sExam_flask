import json
import os

from flask import Blueprint, redirect, render_template, request, send_from_directory, session, url_for

from config import IMAGE_META_PATH, IMAGE_PATH, THUMB_PATH

root_bp = Blueprint('root', __name__)


PAGES = {
    'licenses': {
        'label': 'Scope',
        'title': '구현한 기능',
        'body': 'photoArchive는 사진 업로드, 전체 갤러리, 내 갤러리, 검색 화면을 구현한 개인 사진 아카이브입니다.',
    },
    'contact-us': {
        'label': 'Contact',
        'title': '개선할 점',
        'body': '현재 버전에서 더 발전시킬 수 있는 기능은 업로드 검증, 이미지 삭제, 태그 필터, 썸네일 최적화입니다.',
    },
    'about-us': {
        'label': 'About',
        'title': '프로젝트 목적',
        'body': '흩어진 사진을 웹에서 업로드하고 다시 찾아볼 수 있도록 만들었습니다. Flask 라우팅, 템플릿 렌더링, 파일 저장 구조를 직접 확인할 수 있습니다.',
    },
    'refunds-policy': {
        'label': 'Data',
        'title': '데이터 저장 방식',
        'body': '업로드된 이미지는 app/database/images 폴더에 저장하고, 제목과 분류 같은 정보는 image_meta.json 파일에 기록합니다.',
    },
    'seller-profile': {
        'label': 'Profile',
        'title': '프로젝트 구성',
        'body': '라우트, 템플릿, 정적 CSS, 이미지 저장 폴더를 나누어 관리했습니다. 화면은 사진이 잘 보이도록 큰 카드와 명확한 버튼 중심으로 정리했습니다.',
    },
    'privacy-policy': {
        'label': 'Privacy',
        'title': '개인 사진 보관 안내',
        'body': '현재 버전은 로컬 프로젝트 폴더에 사진을 저장합니다. 실제 서비스로 확장한다면 사용자 권한, 삭제 기능, 저장 용량 제한이 추가로 필요합니다.',
    },
}

NEWS_POSTS = [
    {
        'slug': 'project-overview',
        'title': '프로젝트 개요',
        'excerpt': '사진을 업로드하고 다시 찾아볼 수 있는 Flask 기반 아카이브를 만들었습니다.',
        'date': 'Jun 22, 2026',
        'body': [
            'photoArchive는 개인 사진을 업로드하고 다시 찾아보기 위해 만든 웹 아카이브입니다.',
            '업로드, 전체 갤러리, 내 갤러리, 검색 화면을 하나의 흐름으로 연결했습니다.',
        ],
    },
    {
        'slug': 'upload-flow',
        'title': '업로드 기능 구현',
        'excerpt': '사용자가 선택한 이미지를 서버 폴더에 저장하고 메타데이터를 JSON으로 관리합니다.',
        'date': 'Jun 21, 2026',
        'body': [
            '업로드 라우트에서 파일 확장자를 확인한 뒤 app/database/images 폴더에 저장합니다.',
            '사진 제목, 분류, 업로드 날짜 같은 정보는 image_meta.json에 기록해 갤러리에서 다시 사용합니다.',
        ],
    },
    {
        'slug': 'gallery-search',
        'title': '갤러리와 검색',
        'excerpt': '저장된 사진을 같은 카드 규격으로 보여주고 제목과 업로더 기준으로 검색합니다.',
        'date': 'Jun 20, 2026',
        'body': [
            '전체 갤러리는 이미지 폴더를 읽어 최신 업로드 순서로 사진을 보여줍니다.',
            '검색어가 있으면 제목과 업로더 이름을 비교해 필요한 사진만 남깁니다.',
        ],
    },
    {
        'slug': 'my-gallery',
        'title': '내 갤러리 화면',
        'excerpt': '로그인한 사용자가 업로드한 사진만 따로 확인할 수 있게 구성했습니다.',
        'date': 'Jun 19, 2026',
        'body': [
            '파일명 앞에 저장된 사용자 이름을 기준으로 사진 소유자를 구분합니다.',
            '로그인하지 않은 상태에서 내 갤러리에 접근하면 로그인 화면으로 이동합니다.',
        ],
    },
    {
        'slug': 'layout-cleanup',
        'title': '레이아웃 정리',
        'excerpt': '카드 이미지 비율, 버튼 크기, 텍스트 줄바꿈을 맞춰 화면 완성도를 높였습니다.',
        'date': 'Jun 18, 2026',
        'body': [
            '카드마다 다른 이미지 높이를 통일하고 텍스트 영역이 밀리지 않도록 CSS를 정리했습니다.',
            '필요 없는 마케팅 문구와 복잡한 장식 코드를 줄여 프로젝트 목적이 더 잘 보이게 만들었습니다.',
        ],
    },
    {
        'slug': 'next-steps',
        'title': '추가로 개선할 점',
        'excerpt': '삭제 기능, 태그 필터, 썸네일 최적화가 다음 개선 후보입니다.',
        'date': 'Jun 17, 2026',
        'body': [
            '현재 버전은 업로드와 조회 흐름에 집중했습니다.',
            '추후에는 사진 삭제, 태그별 필터, 이미지 압축, 사용자별 저장 공간 제한을 추가할 수 있습니다.',
        ],
    },
]

POPULAR_NEWS_SCORES = {
    'project-overview': 100,
    'upload-flow': 90,
    'gallery-search': 80,
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


def get_news_posts(limit=None):
    photos = get_gallery_photos()
    posts = []

    for index, post in enumerate(NEWS_POSTS):
        photo = photos[index % len(photos)] if photos else None
        posts.append({
            **post,
            'image_url': photo['url'] if photo else '',
            'image_alt': photo['title'] if photo else post['title'],
            'url': url_for('root.whats_new_detail', slug=post['slug']),
        })

    return posts[:limit] if limit else posts


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


@root_bp.route('/whats-new')
def whats_new():
    posts = get_news_posts()
    hero_post, grid_posts = split_news_index_posts(posts)
    return render_template('whats_new.html', hero_post=hero_post, posts=grid_posts, body_class='news')


@root_bp.route('/whats-new/<slug>')
def whats_new_detail(slug):
    posts = get_news_posts()
    post = next((item for item in posts if item['slug'] == slug), None)
    if not post:
        hero_post, grid_posts = split_news_index_posts(posts)
        return render_template('whats_new.html', hero_post=hero_post, posts=grid_posts, body_class='news'), 404

    return render_template('news_detail.html', post=post, body_class='news-post')


@root_bp.route('/pages/<slug>')
def page(slug):
    page_data = PAGES.get(slug)
    if not page_data:
        return render_template('page.html', page=PAGES['about-us'], body_class='info'), 404

    return render_template('page.html', page=page_data, body_class='info')


@root_bp.route('/products/<slug>')
def product(slug):
    return redirect(url_for('root.gallery'))


@root_bp.route('/media/<path:filename>')
def media(filename):
    return send_from_directory(IMAGE_PATH, filename)


@root_bp.route('/thumb/<path:filename>')
def thumbnail(filename):
    return send_from_directory(THUMB_PATH, filename)
