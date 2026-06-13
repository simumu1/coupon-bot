#!/usr/bin/env python3
"""Coupon Bot — Web前台 (GEO优化版)"""
import json, os
from flask import Flask, render_template, jsonify, request
from datetime import datetime

from config import COUPON_FILE, TARGET_NICHES

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
    'BarkBox': [
        {"q": "Does BarkBox offer first box discount?", "a": "Yes, get 20% off your first month with code BARK20."},
        {"q": "Can I cancel BarkBox anytime?", "a": "Yes, BarkBox has no long-term commitment. You can cancel or skip months anytime."},
    ],
    'Furbo': [
        {"q": "Does Furbo have a discount for first-time buyers?", "a": "Yes, get 20% off your first Furbo order with code FURBO20."},
    ],
    'LitterRobot': [
        {"q": "Does LitterRobot offer a discount?", "a": "Yes, save $50 on your first LitterRobot order with code LITTER10."},
        {"q": "What is LitterRobot's warranty?", "a": "LitterRobot comes with a 1-year warranty and a 90-day in-home trial."},
    ],
    'TheFarmersDog': [
        {"q": "Does The Farmer's Dog offer a first order discount?", "a": "Yes, get 30% off your first order with code FARMER30."},
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
    'Lululemon': [
        {"q": "Does Lululemon offer a first order discount?", "a": "Yes, new customers save 25% on their first order with code HELLO25."},
    ],
    'Hydrow': [
        {"q": "Does Hydrow offer a discount?", "a": "Yes, save $200 on a Hydrow rowing machine with code HYDROW200."},
        {"q": "Does Hydrow offer a free trial?", "a": "Yes, Hydrow offers a 30-day free trial with code HYDROWFREE."},
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


if __name__ == '__main__':
    print('🚀 Coupon Bot Web (GEO版) @ http://localhost:5000')
    app.run(host='0.0.0.0', port=5000, debug=False)
