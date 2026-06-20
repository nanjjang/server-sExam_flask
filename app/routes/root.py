import json
import os

from flask import Blueprint, render_template, request, send_from_directory, url_for

from config import IMAGE_META_PATH, IMAGE_PATH, THUMB_PATH

root_bp = Blueprint('root', __name__)


COLLECTIONS = {
    'all': {
        'label': 'All Photos',
        'title': 'All archives',
        'description': 'Every saved photograph in photoArchive, gathered in one quiet shelf.',
    },
    'after-effects': {
        'label': 'Seaside',
        'title': 'Blue photos from the edge of the city',
        'description': 'Beach walks, horizon lines, waves, and soft daylight saved as a calm archive.',
    },
    'figma-templates': {
        'label': 'City',
        'title': 'Urban frames for everyday memory',
        'description': 'Buildings, streets, signs, and passing views organized into visual records.',
    },
    'jitter': {
        'label': 'Moments',
        'title': 'Small scenes worth keeping',
        'description': 'Personal snapshots and quiet moments that become searchable memories.',
    },
    'bundles': {
        'label': 'Stories',
        'title': 'Photo stories grouped by mood',
        'description': 'Curated sets of photos collected by place, date, color, and atmosphere.',
    },
    'new-releases': {
        'label': 'New Uploads',
        'title': 'Recently added photographs',
        'description': 'The newest images uploaded to photoArchive, ready to browse and save.',
    },
}

DEFAULT_COLLECTION_ORDER = ['after-effects', 'figma-templates', 'jitter', 'bundles']

LEGACY_PRODUCT_SLUGS = [
    'archive-grid',
    'visual-shelf',
    'mood-board',
    'city-light-pack',
    'seaside-memory',
]

PAGES = {
    'licenses': {
        'label': 'Archive Rule',
        'title': 'Photos stay inside your archive',
        'body': 'photoArchive is a personal project space for uploading, browsing, and organizing photographs.',
    },
    'contact-us': {
        'label': 'Contact',
        'title': 'Talk to photoArchive',
        'body': 'Questions about upload flow, gallery layout, or future archive features can be sent through the project contact channel.',
    },
    'about-us': {
        'label': 'About',
        'title': 'A calm place for saved photographs',
        'body': 'photoArchive turns uploaded images into a curated visual shelf, connecting dates, places, moods, and stories inside one clean browsing experience.',
    },
    'refunds-policy': {
        'label': 'Data Guide',
        'title': 'Prototype data guide',
        'body': 'This project uses local uploaded images for display. Future versions can add account storage, privacy controls, tags, favorites, and recovery tools.',
    },
    'seller-profile': {
        'label': 'Profile',
        'title': 'Created for photoArchive',
        'body': 'A visual identity focused on clean grids, large photography, searchable memories, and a portfolio-grade archive interface.',
    },
    'privacy-policy': {
        'label': 'Privacy',
        'title': 'Privacy for personal archives',
        'body': 'This prototype keeps uploaded images in the local project directory. Production storage should add explicit permissions and recovery controls.',
    },
}

NEWS_POSTS = [
    {
        'slug': 'curation-becomes-portfolio',
        'title': 'When curation becomes your portfolio',
        'excerpt': 'We built a way to turn your photoArchive profile into a visual story.',
        'date': 'May 21, 2026',
        'body': [
            'Your archive can be more than a place to keep files. It can become a living portfolio of taste, mood, location, and memory.',
            'This update brings clearer visual collections, stronger image rhythm, and a simpler way to present the photographs that shape your work.',
        ],
    },
    {
        'slug': 'introducing-upload-board',
        'title': 'Introducing the photoArchive upload board',
        'excerpt': 'A calmer workflow for saving images, arranging them, and returning to the moments that matter.',
        'date': 'May 8, 2026',
        'body': [
            'The upload board is designed for the first few seconds after inspiration arrives.',
            'We focused on a faster path from upload to gallery so your newest references can move into collections without getting buried.',
        ],
    },
    {
        'slug': 'readymade-archive-conversation',
        'title': 'A conversation about quiet visual archives',
        'excerpt': 'What makes a personal photo shelf worth revisiting again and again.',
        'date': 'Apr 13, 2026',
        'body': [
            'The best archives do not shout. They make it easy to notice patterns across time, place, color, and feeling.',
            'This note looks at how photoArchive can help small collections grow into a useful visual memory system.',
        ],
    },
    {
        'slug': 'portfolio-tool-we-wanted',
        'title': 'We built the portfolio tool we always wanted',
        'excerpt': 'A simple way to turn saved photographs into a browsable body of work.',
        'date': 'Feb 11, 2026',
        'body': [
            'A portfolio should feel easy to update. Recent work and old favorites can live inside the same clean flow.',
            'Collections, detail views, and search now work together as one connected archive surface.',
        ],
    },
    {
        'slug': 'comments-are-here',
        'title': 'Comments are here',
        'excerpt': 'A lightweight layer for leaving context beside the images you save.',
        'date': 'Feb 10, 2026',
        'body': [
            'Every saved image has a reason behind it. Comments give those reasons a place to live beside the photograph.',
            'Use them for location notes, project context, small memories, or reminders for what to revisit next.',
        ],
    },
    {
        'slug': 'your-data-is-yours',
        'title': 'Your data is yours',
        'excerpt': 'A straightforward note on ownership, local project data, and future privacy controls.',
        'date': 'Feb 9, 2026',
        'body': [
            'photoArchive is built around the idea that personal images should remain personal unless you decide otherwise.',
            'The current prototype keeps images in the local project structure.',
        ],
    },
    {
        'slug': 'eight-years-community',
        'title': '8 years. A love letter to visual memory.',
        'excerpt': 'A small celebration of the habit of saving what keeps inspiring you.',
        'date': 'Nov 13, 2025',
        'body': [
            'The habit is simple: notice something, save it, return later with new eyes.',
            'photoArchive is our way of giving that habit a quieter and more beautiful home.',
        ],
    },
    {
        'slug': 'new-space-for-teams',
        'title': 'A new space for your team archive',
        'excerpt': 'Shared collections for groups that think through images together.',
        'date': 'Aug 26, 2025',
        'body': [
            'Team archives need shared context without making the interface feel heavy.',
            'This direction explores grouped collections, clearer story shelves, and quick access to the images everyone comes back to.',
        ],
    },
    {
        'slug': 'photoarchive-and-whats-next',
        'title': 'photoArchive.com and what is next',
        'excerpt': 'A cleaner archive surface, richer discovery, and a better way to come back to saved moments.',
        'date': 'Aug 15, 2025',
        'body': [
            'Back in 2015, the archive was a simple place to keep visual notes. We kept returning to the same idea: make rediscovery quieter and easier.',
            'The next version of photoArchive focuses on fewer clicks between upload, sorting, and returning to the images that still matter.',
        ],
    },
    {
        'slug': 'reimagined-search',
        'title': 'How we reimagined search on photoArchive',
        'excerpt': 'Search should feel like returning to a place, not filling out a database form.',
        'date': 'Jul 3, 2025',
        'body': [
            'A personal archive grows through small details: dates, places, colors, seasons, and the words you remember later.',
            'This note outlines how search can become more visual while staying simple enough for daily use.',
        ],
    },
    {
        'slug': 'valuable-skill-taste',
        'title': 'The most valuable skill you can have as a designer: Taste',
        'excerpt': 'An archive is not only storage. It is a record of what keeps catching your eye.',
        'date': 'May 20, 2025',
        'body': [
            'Taste improves when you keep noticing what you return to.',
            'photoArchive gives those repetitions a shape so your own references can teach you something over time.',
        ],
    },
    {
        'slug': 'motion-reference-guide',
        'title': 'Quick guide on how to update your motion references',
        'excerpt': 'A practical way to keep inspiration boards fresh without losing old context.',
        'date': 'May 12, 2025',
        'body': [
            'Motion references tend to scatter across screenshots, folders, and temporary links.',
            'A clear archive lets new ideas sit beside older ones without turning the workspace into noise.',
        ],
    },
    {
        'slug': 'new-way-to-save',
        'title': 'A new way to save what inspires you',
        'excerpt': 'Notes on collecting visual material while you browse and returning to it later.',
        'date': 'Apr 23, 2025',
        'body': [
            'Saving an image is only the first step. The important part is finding it again at the right moment.',
            'We are thinking about lightweight capture flows that preserve the context around a saved photograph.',
        ],
    },
    {
        'slug': 'discover-more-like-this',
        'title': 'Discover more like this: a seamless way to find new inspiration',
        'excerpt': 'Related saves can make an archive feel alive instead of static.',
        'date': 'Dec 29, 2024',
        'body': [
            'The best recommendation is often one that starts from your own archive.',
            'By connecting nearby colors, places, and moods, photoArchive can make rediscovery feel intentional.',
        ],
    },
    {
        'slug': 'archive-turns-seven',
        'title': 'photoArchive turns 7',
        'excerpt': 'A small note on keeping a side project simple enough to keep improving.',
        'date': 'Aug 9, 2024',
        'body': [
            'The projects that last usually have one clear habit at the center.',
            'For photoArchive, that habit is saving what matters visually and giving yourself a reason to come back.',
        ],
    },
    {
        'slug': 'five-new-features',
        'title': 'Five new features: saved videos, mobile app, simple tagging and more',
        'excerpt': 'A roadmap for turning a small photo shelf into a stronger creative tool.',
        'date': 'Jun 23, 2024',
        'body': [
            'A good archive should meet you where you work.',
            'This roadmap brings together upload improvements, mobile browsing, richer tags, and more useful saved records.',
        ],
    },
    {
        'slug': 'marketplace-craft',
        'title': 'Introducing our marketplace craft with photoArchive',
        'excerpt': 'A behind-the-scenes look at building a visual system around saved photographs.',
        'date': 'Feb 29, 2024',
        'body': [
            'The interface should disappear just enough for the images to feel important.',
            'We designed the archive around large previews, compact metadata, and a rhythm that rewards scrolling.',
        ],
    },
    {
        'slug': 'beauty-matters',
        'title': 'Because beauty matters',
        'excerpt': 'Why small visual decisions make an archive easier to love and easier to use.',
        'date': 'Dec 29, 2023',
        'body': [
            'A beautiful archive is not about decoration. It is about making the act of returning feel worthwhile.',
            'Spacing, rhythm, and image size all shape whether someone wants to keep browsing.',
        ],
    },
    {
        'slug': 'one-million-saves',
        'title': 'photoArchive reaches one million saves',
        'excerpt': 'A milestone for the small habit of saving visual memory.',
        'date': 'Dec 19, 2023',
        'body': [
            'A million saves is not only a number. It is a million small moments someone thought were worth keeping.',
            'This is a celebration of those quiet decisions and the shelves they create.',
        ],
    },
    {
        'slug': 'adding-images-to-board',
        'title': 'Adding images to a board',
        'excerpt': 'How to move from upload to a useful board without interrupting your flow.',
        'date': 'Dec 3, 2023',
        'body': [
            'A board should be fast enough to catch a thought before it disappears.',
            'This update keeps the path from saved image to sorted archive short and predictable.',
        ],
    },
    {
        'slug': 'conversation-about-memory',
        'title': 'A conversation about visual memory',
        'excerpt': 'What personal archives can learn from designers, photographers, and everyday collectors.',
        'date': 'Nov 27, 2023',
        'body': [
            'Visual memory is built from the things you decide to keep and the way you return to them.',
            'We talked through the habits that make an archive useful after the first upload.',
        ],
    },
]

POPULAR_NEWS_SCORES = {
    'introducing-upload-board': 98,
    'curation-becomes-portfolio': 94,
    'readymade-archive-conversation': 88,
    'comments-are-here': 82,
    'your-data-is-yours': 78,
    'portfolio-tool-we-wanted': 74,
}


def load_image_meta():
    if not os.path.exists(IMAGE_META_PATH):
        return {}

    try:
        with open(IMAGE_META_PATH, 'r', encoding='utf-8') as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        return {}


def get_gallery_photos(limit=None):
    allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
    display_titles = ['바닷가 산책', '부산의 오후', '느린 파도', '도시의 해변']
    display_likes = ['6,923', '9,923', '7,032', '8,249']
    display_dates = ['2026.01.01', '2026.09.13', '2026.11.05', '2026.08.24']
    display_locations = ['Haeundae', 'Busan', 'Blue hour', 'Seaside']
    meta = load_image_meta()
    photos = []

    filenames = []
    if os.path.exists(IMAGE_PATH):
        for filename in os.listdir(IMAGE_PATH):
            stem, ext = os.path.splitext(filename)
            if ext.lower() in allowed_extensions:
                filenames.append(filename)

    filenames.sort(key=lambda filename: os.path.getmtime(os.path.join(IMAGE_PATH, filename)), reverse=True)

    for filename in filenames:
        stem, _ = os.path.splitext(filename)
        owner = stem.split('_', 1)[0]
        image_url = url_for('root.media', filename=filename)
        thumb_path = os.path.join(THUMB_PATH, filename)
        if os.path.exists(thumb_path):
            image_url = url_for('root.thumbnail', filename=filename)

        index = len(photos)
        fallback_collection = DEFAULT_COLLECTION_ORDER[index % len(DEFAULT_COLLECTION_ORDER)]
        photo_meta = meta.get(filename, {})
        collection = photo_meta.get('collection', fallback_collection)
        if collection not in COLLECTIONS or collection in {'all', 'new-releases'}:
            collection = fallback_collection

        photos.append({
            'filename': filename,
            'slug': stem,
            'owner': owner,
            'title': photo_meta.get('title') or (display_titles[index] if index < len(display_titles) else f'Archive Photo {index + 1:02d}'),
            'likes': display_likes[index] if index < len(display_likes) else f'{692312 + index * 299535:,}',
            'date': photo_meta.get('uploaded_at') or (display_dates[index] if index < len(display_dates) else f'2026.{(index % 12) + 1:02d}.{(index * 8 % 28) + 1:02d}'),
            'location': display_locations[index] if index < len(display_locations) else 'Archive',
            'collection': collection,
            'collection_label': COLLECTIONS[collection]['label'],
            'url': image_url,
        })

    return photos[:limit] if limit else photos


def get_market_products(limit=None):
    products = []
    for photo in get_gallery_photos():
        products.append({
            'slug': photo['slug'],
            'title': photo['title'],
            'collection': photo['collection'],
            'collection_label': photo['collection_label'],
            'price': f"{photo['likes']} likes",
            'compare_price': photo['date'],
            'image_url': photo['url'],
            'description': 'A saved photo record organized for browsing, collecting, and rediscovering later.',
        })

    return products[:limit] if limit else products


def get_market_product(slug):
    products = get_market_products()
    product = next((product for product in products if product['slug'] == slug), None)
    if product:
        return product

    if slug in LEGACY_PRODUCT_SLUGS and products:
        return products[LEGACY_PRODUCT_SLUGS.index(slug) % len(products)]

    return None


def get_news_posts(limit=None):
    products = get_market_products()
    posts = []

    for index, post in enumerate(NEWS_POSTS):
        product = products[index % len(products)] if products else None
        posts.append({
            **post,
            'image_url': product['image_url'] if product else '',
            'image_alt': product['title'] if product else post['title'],
            'collection_label': product['collection_label'] if product else 'Update',
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
    return render_template(
        'home.html',
        products=get_market_products(),
        body_class='page-home',
    )


@root_bp.route('/feature')
def feature():
    return render_template(
        'feature.html',
        products=get_market_products(),
        body_class='page-feature',
    )


@root_bp.route('/whats-new')
def whats_new():
    posts = get_news_posts()
    hero_post, grid_posts = split_news_index_posts(posts)
    return render_template(
        'whats_new.html',
        hero_post=hero_post,
        posts=grid_posts,
        body_class='page-whats-new',
    )


@root_bp.route('/whats-new/<slug>')
def whats_new_detail(slug):
    posts = get_news_posts()
    post = next((item for item in posts if item['slug'] == slug), None)
    if not post:
        hero_post, grid_posts = split_news_index_posts(posts)
        return render_template(
            'whats_new.html',
            hero_post=hero_post,
            posts=grid_posts,
            body_class='page-whats-new',
        ), 404

    return render_template('news_detail.html', post=post, body_class='page-news-detail')


@root_bp.route('/gallery')
def gallery():
    return render_market_listing()


@root_bp.route('/search')
def search():
    return render_market_listing()


def render_market_listing():
    query = request.args.get('q', '').strip()
    products = get_market_products()
    if query:
        lowered_query = query.lower()
        products = [
            product for product in products
            if lowered_query in product['title'].lower()
            or lowered_query in product['collection_label'].lower()
            or lowered_query in product['description'].lower()
            or lowered_query in product['compare_price'].lower()
        ]

    return render_template(
        'gallery.html',
        products=products,
        query=query,
        collections=COLLECTIONS,
        body_class='page-gallery',
    )


@root_bp.route('/collections/<slug>')
def collection(slug):
    if slug == 'figma':
        slug = 'figma-templates'

    collection_data = COLLECTIONS.get(slug)
    if not collection_data:
        return render_market_listing(), 404

    products = get_market_products()
    if slug not in {'all', 'new-releases'}:
        products = [product for product in products if product['collection'] == slug]
    elif slug == 'new-releases':
        products = products[:6]

    return render_template(
        'collection.html',
        collection_slug=slug,
        collection=collection_data,
        products=products,
        collections=COLLECTIONS,
        body_class='page-gallery',
    )


@root_bp.route('/products/<slug>')
def product(slug):
    product_data = get_market_product(slug)
    if not product_data:
        return render_template('gallery.html', products=get_market_products(), query='', collections=COLLECTIONS, body_class='page-gallery'), 404

    related = [product for product in get_market_products(5) if product['slug'] != slug][:4]
    return render_template('product.html', product=product_data, related=related, body_class='page-product')


@root_bp.route('/cart')
def cart():
    return render_template('cart.html', products=get_market_products(3), body_class='page-cart')


@root_bp.route('/pages/<slug>')
def page(slug):
    page_data = PAGES.get(slug)
    if not page_data:
        return render_template('page.html', page=PAGES['about-us'], body_class='page-static'), 404

    return render_template('page.html', page=page_data, body_class='page-static')


@root_bp.route('/media/<path:filename>')
def media(filename):
    return send_from_directory(IMAGE_PATH, filename)


@root_bp.route('/thumb/<path:filename>')
def thumbnail(filename):
    return send_from_directory(THUMB_PATH, filename)
