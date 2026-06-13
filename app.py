#!/usr/bin/env python3
"""Coupon Bot — Web前台 (GEO优化版)"""
import json, os
from flask import Flask, render_template, jsonify, request
from datetime import datetime

from config import COUPON_FILE, TARGET_NICHES, GA_MEASUREMENT_ID, GOATCOUNTER_DOMAIN, UMAMI_URL, UMAMI_WEBSITE_ID

app = Flask(__name__)


def load_coupons():
    """加载缓存优惠码"""
    if not os.path.exists(COUPON_FILE):
        return {'updated_at': None, 'total': 0, 'coupons': []}
    with open(COUPON_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


# ===== FAQ数据（每个品牌的常见问题，AI抓取用）=====
BRAND_FAQ = {
    'default': [
        {"q": "How to use this coupon?", "a": "Click the coupon code to copy it, then paste at checkout on the brand's website."},
        {"q": "Are these coupons verified?", "a": "Coupons are sourced from brand websites and community posts. We verify them regularly but recommend testing before checkout."},
        {"q": "What if a coupon doesn't work?", "a": "Coupons have expiration dates and usage limits. Try another code from the list or check the brand's current promotions."},
    ],
    'Article': [
        {"q": "Does Article have a student discount?", "a": "Article offers a 15% discount for new customers with code WELCOME15. Student-specific discounts are not currently available."},
        {"q": "Does Article offer free shipping?", "a": "Yes, Article offers free shipping on most orders with code FREESHIP."},
        {"q": "What is Article's return policy?", "a": "Article offers a 30-day return policy from the date of delivery. Items must be in original condition."},
    ],
    'Burrow': [
        {"q": "Does Burrow offer a first-time buyer discount?", "a": "Yes, Burrow offers 20% off sitewide for new customers with code SAVE20."},
        {"q": "Does Burrow have free shipping?", "a": "Burrow offers free shipping on all orders over $500. Smaller orders may have a shipping fee."},
        {"q": "What is Burrow's warranty?", "a": "Burrow offers a 1-year warranty on all products covering manufacturing defects."},
    ],
    'Brooklinen': [
        {"q": "Does Brooklinen offer a welcome discount?", "a": "Yes, new customers get 15% off their first order with code HELLO15."},
        {"q": "Does Brooklinen have bundle deals?", "a": "Yes, Brooklinen offers bundle discounts. Use code BUNDLEUP for extra savings on sets."},
    ],
    'Parachute': [
        {"q": "Does Parachute offer a welcome discount?", "a": "Yes, new customers save 20% on their first order with code WELCOME20."},
        {"q": "Does Parachute offer free shipping?", "a": "Yes, Parachute offers free shipping on orders over $50."},
    ],
    'Furbo': [
        {"q": "Does Furbo have a discount for first-time buyers?", "a": "Yes, get 20% off your first Furbo order with code FURBO20."},
    ],
    'LitterRobot': [
        {"q": "Does LitterRobot offer a discount?", "a": "Yes, save $50 on your first LitterRobot order with code LITTER10."},
        {"q": "What is LitterRobot's warranty?", "a": "LitterRobot comes with a 1-year warranty and a 90-day in-home trial."},
    ],
    'Peloton': [
        {"q": "Does Peloton offer accessories discount?", "a": "Yes, save $100 on Peloton accessories with code PELO100."},
        {"q": "Does Peloton offer free trial?", "a": "Yes, new members can get a free first year of the Peloton App membership."},
    ],
    'Tonal': [
        {"q": "Does Tonal offer a discount?", "a": "Yes, save $200 on Tonal equipment with code TONAL200."},
    ],
    'Whoop': [
        {"q": "Does WHOOP offer a free trial?", "a": "Yes, get your first month free with code WHOOP1M."},
    ],
    'Oura': [
        {"q": "Does Oura offer a discount?", "a": "Yes, save $20 on Oura Ring with code OURA20."},
    ],
    'EightSleep': [
        {"q": "Does Eight Sleep offer a first order discount?", "a": "Yes, get 10% off your first Eight Sleep order with code EIGHT10."},
    ],
    'Casper': [
        {"q": "Does Casper offer a first-time buyer discount?", "a": "Yes, new customers get 15% off their first order with code SLEEP15."},
        {"q": "Does Casper offer mattress discounts?", "a": "Yes, save $100 on Casper mattresses with code NAP100."},
        {"q": "Does Casper have pillow deals?", "a": "Yes, get 20% off Casper pillows with code PILLOW20."},
        {"q": "What is Casper's trial period?", "a": "Casper offers a 100-night risk-free trial on all mattresses."},
    ],
    'V-Dog': [
        {"q": "Does V-Dog offer a first order discount?", "a": "Yes, new customers get 20% off their first order with code VDOG20."},
        {"q": "Does V-Dog have a repeat customer discount?", "a": "Yes, returning customers save 10% with code VEGAN10."},
        {"q": "Is V-Dog food vegan?", "a": "Yes, V-Dog makes 100% plant-based, vegan dog food with complete nutrition."},
    ],
    'Wild Earth': [
        {"q": "Does Wild Earth offer a first order discount?", "a": "Yes, new customers get 15% off their first order with code KOJI15."},
        {"q": "Does Wild Earth have a satisfaction guarantee?", "a": "Yes, Wild Earth offers a 30-day money-back guarantee with code EARTH30."},
        {"q": "Is Wild Earth dog food vegan?", "a": "Yes, Wild Earth makes science-backed, plant-based dog food with clean protein from koji."},
    ],
    'West Elm': [
        {"q": "Does West Elm offer a first order discount?", "a": "Yes, new customers get 15% off their first order with code WELCOME15."},
        {"q": "Does West Elm offer free shipping?", "a": "Yes, West Elm offers free shipping on orders over $49."},
    ],
    'Rove Concepts': [
        {"q": "Does Rove Concepts offer a first order discount?", "a": "Yes, new customers save 10% on their first order with code ROVE10."},
    ],
    'Hydrow': [
        {"q": "Does Hydrow offer a discount?", "a": "Yes, save $200 on a Hydrow rowing machine with code HYDROW200."},
        {"q": "Does Hydrow offer a free trial?", "a": "Yes, Hydrow offers a 30-day free trial with code HYDROWFREE."},
    ],
    'Sabai': [
        {"q": "Does Sabai offer a first order discount?", "a": "Yes, new customers save 15% with code SABAI15."},
        {"q": "Is Sabai furniture vegan?", "a": "Yes, Sabai makes 100% vegan furniture using recycled and sustainable materials."},
    ],
    'Avocado': [
        {"q": "Does Avocado offer a mattress discount?", "a": "Yes, save $100 on Avocado mattresses with code AVO100."},
        {"q": "Is Avocado eco-friendly?", "a": "Yes, Avocado makes organic, non-toxic mattresses from natural materials."},
    ],
    'NordicTrack': [
        {"q": "Does NordicTrack offer a discount?", "a": "Yes, save $150 on NordicTrack equipment with code NT150."},
    ],
    'Echelon': [
        {"q": "Does Echelon offer a bike discount?", "a": "Yes, save $100 on Echelon bikes with code ECHELON100."},
    ],
    'YouthToThePeople': [
        {"q": "Does Youth to the People offer a discount?", "a": "Yes, new customers get 20% off with code YTTP20."},
        {"q": "Is Youth to the People vegan?", "a": "Yes, all products are 100% vegan and cruelty-free."},
    ],
    'Tower28': [
        {"q": "Does Tower 28 offer a first order discount?", "a": "Yes, new customers save 15% with code TOWER15."},
        {"q": "Is Tower 28 safe for sensitive skin?", "a": "Yes, Tower 28 is formulated for sensitive skin — no alcohol, no fragrance, no harsh ingredients."},
    ],
    'Biossance': [
        {"q": "Does Biossance offer a discount?", "a": "Yes, save 10% on your first order with code BIOSSANCE10."},
        {"q": "Is Biossance vegan?", "a": "Yes, Biossance is 100% vegan, cruelty-free, and uses sustainable squalane."},
    ],
    'Kosas': [
        {"q": "Does Kosas offer a discount?", "a": "Yes, new customers get 15% off with code KOSAS15."},
        {"q": "Is Kosas makeup clean?", "a": "Yes, Kosas makes clean, vegan makeup free from animal-derived ingredients and harsh chemicals."},
    ],
    'Cariuma': [
        {"q": "Does Cariuma offer a first order discount?", "a": "Yes, save 20% on your first pair with code CARI20."},
        {"q": "Are Cariuma shoes vegan?", "a": "Yes, Cariuma offers a full line of 100% vegan sneakers made from sustainable materials."},
    ],
    'Rothy': [
        {"q": "Does Rothy's offer a discount?", "a": "Yes, new customers get 20% off with code ROTHY20."},
        {"q": "Are Rothy's shoes sustainable?", "a": "Yes, Rothy's shoes are made from recycled plastic bottles and are machine washable."},
    ],
    'Tentree': [
        {"q": "Does Tentree offer a discount?", "a": "Yes, save 15% on your first order with code TENTREE15."},
        {"q": "What makes Tentree eco-friendly?", "a": "Tentree plants 10 trees for every item purchased and uses organic, sustainable fabrics."},
    ],
    'Pact': [
        {"q": "Does Pact offer a discount?", "a": "Yes, new customers get 20% off with code PACT20."},
        {"q": "Is Pact organic?", "a": "Yes, Pact makes organic cotton essentials that are fair trade and GOTS certified."},
    ],
    'Blueland': [
        {"q": "Does Blueland offer a first order discount?", "a": "Yes, save 15% with code BLUELAND15."},
        {"q": "Is Blueland plastic-free?", "a": "Yes, Blueland cleaning products use tablet concentrates — no plastic bottles, no waste."},
    ],
    'PublicGoods': [
        {"q": "Does Public Goods offer a discount?", "a": "Yes, save 10% on your first order with code PUBLIC10."},
    ],
    'WhoGivesACrap': [
        {"q": "Does Who Gives A Crap offer a discount?", "a": "Yes, get 20% off your first order with code WGAC20."},
        {"q": "Is Who Gives A Crap eco-friendly?", "a": "Yes, they make 100% bamboo toilet paper and donate 50% of profits to sanitation projects."},
    ],
}


def get_brand_faq(brand_name):
    """获取品牌的FAQ，没有则用默认"""
    return BRAND_FAQ.get(brand_name, BRAND_FAQ['default'])


def generate_brand_schema(brand_name, coupons):
    """生成品牌的Schema.org JSON-LD"""
    schema_offers = []
    for c in coupons[:5]:  # 最多5个优惠码
        disc = c.get('discount', '')
        schema_offers.append({
            "@type": "Offer",
            "description": c.get('title', f"{brand_name} promo code {c['code']}"),
            "discount": disc if disc else "Available",
            "discountCode": c['code'],
            "availability": "https://schema.org/InStock",
            "url": f"https://simumu.pythonanywhere.com/brand/{brand_name.lower()}",
            "price": "0",
            "priceCurrency": "USD",
        })

    schema = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "Product",
                "name": f"{brand_name} Coupons & Promo Codes",
                "brand": {"@type": "Brand", "name": brand_name},
                "description": f"Latest {brand_name} coupon codes, promo codes, and discounts. Save money on {brand_name} products.",
                "offers": {
                    "@type": "AggregateOffer",
                    "offerCount": len(coupons),
                    "offers": schema_offers,
                }
            },
            {
                "@type": "FAQPage",
                "mainEntity": [
                    {"@type": "Question", "name": item["q"], "acceptedAnswer": {"@type": "Answer", "text": item["a"]}}
                    for item in get_brand_faq(brand_name)
                ]
            },
            {
                "@type": "WebPage",
                "name": f"{brand_name} Coupon Codes 2026",
                "description": f"Find the latest {brand_name} coupon codes, promo codes, and discounts. Updated regularly.",
                "dateModified": datetime.now().strftime("%Y-%m-%d"),
            }
        ]
    }
    return schema


def generate_niche_schema(niche_name, coupons):
    """生成品类的Schema"""
    return {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": f"Best {niche_name} Coupons & Deals 2026",
        "description": f"Find the best {niche_name} coupon codes and discounts. Save money on top {niche_name} brands.",
        "dateModified": datetime.now().strftime("%Y-%m-%d"),
    }


@app.route('/')
def index():
    data = load_coupons()
    return render_template('index.html',
                           coupons=data['coupons'],
                           total=data['total'],
                           updated=data.get('updated_at', ''),
                           niches=TARGET_NICHES,
                           ga_id=GA_MEASUREMENT_ID,
                           gc_domain=GOATCOUNTER_DOMAIN,
                           umami_url=UMAMI_URL,
                           umami_site_id=UMAMI_WEBSITE_ID,
                           schema=None,
                           faq=None,
                           brand_faq_data=None)


@app.route('/api/coupons')
def api_coupons():
    """JSON API - AI可以自由爬取"""
    data = load_coupons()
    brand = request.args.get('brand', '').lower()
    if brand:
        data['coupons'] = [c for c in data['coupons'] if brand in c['brand'].lower()]
        data['total'] = len(data['coupons'])
    # 加robots.txt allow头，AI爬虫能正常访问
    resp = jsonify(data)
    resp.headers['X-Robots-Tag'] = 'all'
    return resp


@app.route('/brand/<brand_name>')
def brand_page(brand_name):
    data = load_coupons()
    # 大小写不敏感匹配
    brand_coupons = [c for c in data['coupons'] if c['brand'].lower() == brand_name.lower()]
    brand_name_display = brand_coupons[0]['brand'] if brand_coupons else brand_name.title()

    schema = generate_brand_schema(brand_name_display, brand_coupons)
    faq = get_brand_faq(brand_name_display)
    brand_faq_data = BRAND_FAQ.get(brand_name_display, None)

    return render_template('index.html',
                           coupons=brand_coupons,
                           total=len(brand_coupons),
                           updated=data.get('updated_at', ''),
                           niches=TARGET_NICHES,
                           ga_id=GA_MEASUREMENT_ID,
                           gc_domain=GOATCOUNTER_DOMAIN,
                           umami_url=UMAMI_URL,
                           umami_site_id=UMAMI_WEBSITE_ID,
                           current_brand=brand_name_display,
                           schema=json.dumps(schema, indent=2),
                           faq=faq,
                           brand_faq_data=brand_faq_data)


@app.route('/niche/<niche_key>')
def niche_page(niche_key):
    data = load_coupons()
    niche = TARGET_NICHES.get(niche_key)
    if not niche:
        return 'Niche not found', 404

    brands = [b.lower() for b in niche['brands']]
    niche_coupons = [c for c in data['coupons'] if c['brand'].lower() in brands]

    schema = generate_niche_schema(niche['name'], niche_coupons)

    return render_template('index.html',
                           coupons=niche_coupons,
                           total=len(niche_coupons),
                           updated=data.get('updated_at', ''),
                           niches=TARGET_NICHES,
                           ga_id=GA_MEASUREMENT_ID,
                           gc_domain=GOATCOUNTER_DOMAIN,
                           umami_url=UMAMI_URL,
                           umami_site_id=UMAMI_WEBSITE_ID,
                           current_niche=niche_key,
                           schema=json.dumps(schema, indent=2),
                           faq=None,
                           brand_faq_data=None)


@app.route('/robots.txt')
def robots():
    """完全开放给AI爬虫"""
    return """User-agent: *
Allow: /
Sitemap: https://simumu.pythonanywhere.com/sitemap.xml
""", 200, {'Content-Type': 'text/plain'}


@app.route('/sitemap.xml')
def sitemap():
    """站点地图"""
    data = load_coupons()
    brands = set(c['brand'] for c in data['coupons'])
    urls = ['/']
    for key in TARGET_NICHES:
        urls.append(f'/niche/{key}')
    for brand in brands:
        urls.append(f'/brand/{brand.lower()}')

    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for u in urls:
        xml += f'  <url><loc>https://simumu.pythonanywhere.com{u}</loc></url>\n'
    xml += '</urlset>'
    return xml, 200, {'Content-Type': 'application/xml'}


# ===== 文章页面 (SEO/GEO) =====
ARTICLES = {
    'vegan-pet-food-coupons': {
        'title': 'Best Vegan & Plant-Based Pet Food Coupons 2026',
        'description': 'Save money on plant-based dog food with verified coupon codes for V-Dog, Wild Earth and more vegan pet brands.',
        'content': '''
<h2>Why Choose Plant-Based Pet Food?</h2>
<p>More pet parents are switching to plant-based dog food for ethical, environmental, and health reasons. Vegan pet food brands like V-Dog and Wild Earth use clean, science-backed plant protein sources that provide complete nutrition for your furry friend.</p>

<h2>Top Vegan Pet Food Coupons</h2>

<div class="brand-card">
    <a href="/brand/v-dog" class="brand-name">🐕 V-Dog</a>
    <div class="brand-codes"><strong>VDOG20</strong> — 20% off first order · <strong>VEGAN10</strong> — 10% off repeat order</div>
</div>
<div class="brand-card">
    <a href="/brand/wild%20earth" class="brand-name">🐕 Wild Earth</a>
    <div class="brand-codes"><strong>KOJI15</strong> — 15% off first order · <strong>EARTH30</strong> — 30-day guarantee</div>
</div>

<h2>Pet Accessories & Hardware</h2>
<p>Keep your pets happy with smart pet gadgets. These hardware brands make pet care easier:</p>
<div class="brand-card">
    <a href="/brand/furbo" class="brand-name">📹 Furbo Dog Camera</a>
    <div class="brand-codes"><strong>FURBO20</strong> — 20% off first order</div>
</div>
<div class="brand-card">
    <a href="/brand/litterrobot" class="brand-name">🤖 Litter-Robot</a>
    <div class="brand-codes"><strong>LITTER10</strong> — $50 off first order</div>
</div>

<h2>Why Trust These Coupons?</h2>
<p>All coupons listed on CouponBot are verified from brand websites and updated regularly. We prioritize plant-based and cruelty-free brands that align with ethical pet ownership.</p>
''',
    },
    'home-furniture-deals': {
        'title': 'Best Home Furniture Deals & Coupon Codes 2026',
        'description': 'Find verified coupon codes for top DTC furniture brands including Article, Burrow, West Elm, and more. Save big on sofas, beds, and home decor.',
        'content': '''
<h2>Premium Furniture at Discounted Prices</h2>
<p>DTC (Direct-to-Consumer) furniture brands offer high-quality pieces without the retail markup. Here are the best coupon codes to save on your next furniture purchase.</p>

<h2>Top Furniture Coupons</h2>

<div class="brand-card">
    <a href="/brand/article" class="brand-name">🛋️ Article</a>
    <div class="brand-codes"><strong>WELCOME15</strong> — 15% off first order · <strong>FREESHIP</strong> — Free shipping</div>
</div>
<div class="brand-card">
    <a href="/brand/burrow" class="brand-name">🛋️ Burrow</a>
    <div class="brand-codes"><strong>SAVE20</strong> — 20% off sitewide · <strong>WELCOME10</strong> — 10% off new customers</div>
</div>
<div class="brand-card">
    <a href="/brand/west%20elm" class="brand-name">🛋️ West Elm</a>
    <div class="brand-codes"><strong>WELCOME15</strong> — 15% off first order · <strong>SHIPFREE</strong> — Free shipping $49+</div>
</div>

<h2>Eco-Friendly & Vegan Furniture</h2>
<div class="brand-card">
    <a href="/brand/sabai" class="brand-name">🌿 Sabai</a>
    <div class="brand-codes"><strong>SABAI15</strong> — 15% off first order · 100% vegan furniture</div>
</div>
<div class="brand-card">
    <a href="/brand/avocado" class="brand-name">🌿 Avocado</a>
    <div class="brand-codes"><strong>AVO100</strong> — $100 off mattress · Organic & non-toxic</div>
</div>

<h2>Bedding & Home Essentials</h2>
<div class="brand-card">
    <a href="/brand/brooklinen" class="brand-name">🛏️ Brooklinen</a>
    <div class="brand-codes"><strong>HELLO15</strong> — 15% off · <strong>BUNDLEUP</strong> — Bundle deals</div>
</div>
<div class="brand-card">
    <a href="/brand/parachute" class="brand-name">🛏️ Parachute</a>
    <div class="brand-codes"><strong>WELCOME20</strong> — 20% off · <strong>FREESHIP</strong> — Free shipping</div>
</div>
''',
    },
    'fitness-equipment-coupons': {
        'title': 'Best Fitness Equipment Coupons & Discounts 2026',
        'description': 'Save on home gym equipment with verified coupon codes for Peloton, NordicTrack, Hydrow, Tonal, and more top fitness brands.',
        'content': '''
<h2>Build Your Home Gym for Less</h2>
<p>Home fitness equipment is a great investment in your health. Use these verified coupon codes to save on top-rated exercise machines, wearables, and smart fitness gear.</p>

<h2>Connected Fitness</h2>
<div class="brand-card">
    <a href="/brand/peloton" class="brand-name">🚴 Peloton</a>
    <div class="brand-codes"><strong>PELO100</strong> — $100 off accessories · <strong>ONEPELO</strong> — Free year membership</div>
</div>
<div class="brand-card">
    <a href="/brand/nordictrack" class="brand-name">🏃 NordicTrack</a>
    <div class="brand-codes"><strong>NT150</strong> — $150 off equipment</div>
</div>
<div class="brand-card">
    <a href="/brand/echelon" class="brand-name">🚴 Echelon</a>
    <div class="brand-codes"><strong>ECHELON100</strong> — $100 off bike</div>
</div>
<div class="brand-card">
    <a href="/brand/hydrow" class="brand-name">🚣 Hydrow</a>
    <div class="brand-codes"><strong>HYDROW200</strong> — $200 off rower · <strong>HYDROWFREE</strong> — 30-day trial</div>
</div>

<h2>Strength Training</h2>
<div class="brand-card">
    <a href="/brand/tonal" class="brand-name">💪 Tonal</a>
    <div class="brand-codes"><strong>TONAL200</strong> — $200 off equipment</div>
</div>

<h2>Health & Wellness Wearables</h2>
<div class="brand-card">
    <a href="/brand/whoop" class="brand-name">⌚ WHOOP</a>
    <div class="brand-codes"><strong>WHOOP1M</strong> — First month free</div>
</div>
<div class="brand-card">
    <a href="/brand/oura" class="brand-name">💍 Oura Ring</a>
    <div class="brand-codes"><strong>OURA20</strong> — $20 off ring</div>
</div>
<div class="brand-card">
    <a href="/brand/eightsleep" class="brand-name">🛏️ Eight Sleep</a>
    <div class="brand-codes"><strong>EIGHT10</strong> — 10% off first order · Smart sleep tracking</div>
</div>

<h2>Sleep & Recovery</h2>
<div class="brand-card">
    <a href="/brand/casper" class="brand-name">🛏️ Casper</a>
    <div class="brand-codes"><strong>SLEEP15</strong> — 15% off · <strong>NAP100</strong> — $100 off mattress · <strong>PILLOW20</strong> — 20% off pillows</div>
</div>
''',
    },
    'vegan-beauty-coupons': {
        'title': 'Best Vegan & Clean Beauty Coupons 2026',
        'description': 'Save on clean, vegan, cruelty-free beauty products with verified coupon codes for Youth to the People, Tower 28, Biossance, Kosas, and more.',
        'content': '''
<h2>Clean Beauty That's Kind to Animals</h2>
<p>Discover the best coupon codes for vegan and clean beauty brands. No animal testing, no animal-derived ingredients, no harsh chemicals — just effective, ethical skincare and makeup.</p>

<h2>Skincare Coupons</h2>
<div class="brand-card">
    <a href="/brand/youthtothepeople" class="brand-name">🧴 Youth to the People</a>
    <div class="brand-codes"><strong>YTTP20</strong> — 20% off first order · 100% vegan superfood skincare</div>
</div>
<div class="brand-card">
    <a href="/brand/tower28" class="brand-name">🧴 Tower 28</a>
    <div class="brand-codes"><strong>TOWER15</strong> — 15% off · Sensitive skin safe, no alcohol</div>
</div>
<div class="brand-card">
    <a href="/brand/biossance" class="brand-name">🧴 Biossance</a>
    <div class="brand-codes"><strong>BIOSSANCE10</strong> — 10% off · Vegan squalane skincare</div>
</div>

<h2>Makeup Coupons</h2>
<div class="brand-card">
    <a href="/brand/kosas" class="brand-name">💄 Kosas</a>
    <div class="brand-codes"><strong>KOSAS15</strong> — 15% off · Clean, vegan makeup</div>
</div>

<h2>Why Clean Beauty?</h2>
<p>Clean beauty means products free from parabens, phthalates, sulfates, and animal-derived ingredients. All brands listed are 100% vegan, cruelty-free, and committed to ethical sourcing.</p>
''',
    },
    'sustainable-fashion-coupons': {
        'title': 'Best Sustainable & Vegan Fashion Coupons 2026',
        'description': 'Find verified coupon codes for ethical, sustainable fashion brands. Vegan sneakers, organic cotton apparel, and recycled material shoes.',
        'content': '''
<h2>Fashion That Doesn't Cost the Earth</h2>
<p>Sustainable fashion brands prove you don't need to compromise style for ethics. From vegan sneakers to organic cotton basics, these brands are leading the way in eco-conscious apparel.</p>

<h2>Vegan Footwear</h2>
<div class="brand-card">
    <a href="/brand/cariuma" class="brand-name">👟 Cariuma</a>
    <div class="brand-codes"><strong>CARI20</strong> — 20% off · Vegan sneakers, sustainable materials</div>
</div>
<div class="brand-card">
    <a href="/brand/rothy" class="brand-name">👟 Rothy's</a>
    <div class="brand-codes"><strong>ROTHY20</strong> — 20% off · Shoes from recycled plastic bottles</div>
</div>

<h2>Ethical Apparel</h2>
<div class="brand-card">
    <a href="/brand/tentree" class="brand-name">🌳 Tentree</a>
    <div class="brand-codes"><strong>TENTREE15</strong> — 15% off · Plants 10 trees per item</div>
</div>
<div class="brand-card">
    <a href="/brand/pact" class="brand-name">👕 Pact</a>
    <div class="brand-codes"><strong>PACT20</strong> — 20% off · Organic cotton, fair trade</div>
</div>

<h2>Why Sustainable Fashion?</h2>
<p>The fashion industry is one of the biggest polluters. Choosing sustainable, vegan, and ethical brands reduces your environmental footprint while supporting fair labor practices.</p>
''',
    },
    'eco-friendly-home-coupons': {
        'title': 'Best Eco-Friendly Home & Cleaning Coupons 2026',
        'description': 'Save on sustainable home essentials with coupon codes for Blueland, Public Goods, Who Gives A Crap, and more eco-friendly brands.',
        'content': '''
<h2>A Cleaner Home, A Cleaner Planet</h2>
<p>Eco-friendly home products help reduce plastic waste and chemical exposure. These brands offer sustainable alternatives to everyday household essentials — from cleaning to bathroom.</p>

<h2>Plastic-Free Cleaning</h2>
<div class="brand-card">
    <a href="/brand/blueland" class="brand-name">🧹 Blueland</a>
    <div class="brand-codes"><strong>BLUELAND15</strong> — 15% off · Tablet concentrates, no plastic bottles</div>
</div>

<h2>Sustainable Household</h2>
<div class="brand-card">
    <a href="/brand/publicgoods" class="brand-name">🏠 Public Goods</a>
    <div class="brand-codes"><strong>PUBLIC10</strong> — 10% off · Eco-friendly home essentials</div>
</div>
<div class="brand-card">
    <a href="/brand/whogivesacrap" class="brand-name">🧻 Who Gives A Crap</a>
    <div class="brand-codes"><strong>WGAC20</strong> — 20% off · Bamboo toilet paper, 50% to charity</div>
</div>

<h2>Why Go Plastic-Free?</h2>
<p>Over 8 million tons of plastic enter our oceans each year. By switching to plastic-free cleaning and household products, you're directly reducing waste and supporting a circular economy.</p>
''',
    },
}


@app.route('/article/<slug>')
def article_page(slug):
    article = ARTICLES.get(slug)
    if not article:
        return 'Article not found', 404
    data = load_coupons()
    brands = set(c['brand'] for c in data['coupons'])
    return render_template('article.html',
                           title=article['title'],
                           description=article['description'],
                           content_html=article['content'],
                           canonical=f'/article/{slug}',
                           ga_id=GA_MEASUREMENT_ID,
                           gc_domain=GOATCOUNTER_DOMAIN,
                           umami_url=UMAMI_URL,
                           umami_site_id=UMAMI_WEBSITE_ID,
                           total_brands=len(brands),
                           total_coupons=data['total'])


if __name__ == '__main__':
    print('🚀 Coupon Bot Web (GEO版) @ http://localhost:5000')
    app.run(host='0.0.0.0', port=5000, debug=False)
