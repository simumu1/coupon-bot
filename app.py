#!/usr/bin/env python3
"""Coupon Bot — Web前台 (GEO优化版 v2)"""
import json, os
from flask import Flask, render_template, jsonify, request
from datetime import datetime

from config import COUPON_FILE, TARGET_NICHES, GA_MEASUREMENT_ID, GOATCOUNTER_DOMAIN, UMAMI_URL, UMAMI_WEBSITE_ID

app = Flask(__name__)

SITE_URL = "https://simumu.pythonanywhere.com"
TODAY = datetime.now().strftime("%Y-%m-%d")
VOTE_FILE = os.path.join(os.path.dirname(__file__), 'data', 'votes.json')
SUBMIT_FILE = os.path.join(os.path.dirname(__file__), 'data', 'submissions.json')

# ===== Jinja2 Filters =====
@app.template_filter('timeago')
def timeago_filter(dt_str):
    """将ISO时间转为友好显示：Verified today / yesterday / 3 days ago"""
    if not dt_str:
        return ''
    try:
        dt = datetime.fromisoformat(dt_str)
    except (ValueError, TypeError):
        return dt_str[:10] if dt_str else ''
    now = datetime.now()
    diff = now - dt
    if diff.days < 0:
        return 'Verified today'
    if diff.days == 0:
        secs = diff.seconds
        if secs < 3600:
            mins = secs // 60
            return f'Verified {mins}m ago' if mins > 0 else 'Verified just now'
        hours = secs // 3600
        return f'Verified {hours}h ago'
    if diff.days == 1:
        return 'Verified yesterday'
    if diff.days < 7:
        return f'Verified {diff.days} days ago'
    if diff.days < 30:
        weeks = diff.days // 7
        return f'Verified {weeks} week{"s" if weeks > 1 else ""} ago'
    if diff.days < 365:
        months = diff.days // 30
        return f'Verified {months} month{"s" if months > 1 else ""} ago'
    return f'Verified {diff.days // 365}y ago'

# ===== 多语言翻译 =====
LANG = {
    'en': {
        'site_title': 'Best DTC Brand Coupon Codes 2026 — Verified Promo Codes',
        'site_desc': 'Find verified coupon codes for 135+ top DTC brands — furniture, pet, fitness, beauty, fashion, home, food, tech, and more. Real savings, updated daily.',
        'h1': '🏷️ Best DTC Coupon Codes',
        'h1_sub': 'Real deals from top DTC brands across 15 categories — sustainable, vegan & give-back brands',
        'nav_all': '🏠 All',
        'total_brands': 'Total Brands',
        'total_coupons': 'Total Coupons',
        'last_checked': 'Last checked',
        'verified_works': '✓ Verified · Works',
        'report_expired': 'Report expired',
        'submit_title': '➕ Submit a Coupon',
        'submit_desc': 'Help the community — share a verified coupon code from your favorite brand',
        'submit_btn': 'Submit Coupon',
        'submit_note': 'Submitted coupons will be reviewed before going live',
        'submit_success': '✅ Thanks!',
        'submit_success_desc': 'Your coupon has been submitted for review.',
        'browse_by': '📋 Browse by Category',
        'guides': '📝 Guides & Articles',
        'footer_text': 'CouponBot · Real deals from top DTC brands',
        'footer_verify': 'Always verify coupon validity before checkout',
        'footer_copyright': 'Open data for everyone',
        'submit_link': '+ Submit a Coupon',
        'lang_switch': '中文',
        'lang_href': '/zh/',
        'faq_title': '❓ Frequently Asked Questions',
        'cta_text': '🔍 Browse All',
        'cta_suffix': 'Brands & Coupons →',
        'vote_yes': 'Works',
        'vote_no': 'Expired',
        'back_home': '← Back to CouponBot Home',
    },
    'zh': {
        'site_title': '2026年最优DTC品牌优惠码合集 — 真实折扣，每日更新',
        'site_desc': '精选135+个DTC品牌的优惠券和折扣码，覆盖家居、宠物、健身、美妆、时尚、食品、科技等品类。真实折扣，每日更新。',
        'h1': '🏷️ DTC品牌优惠码大全',
        'h1_sub': '精选15大品类135+个纯素/环保/公益品牌优惠，真实折扣每日更新',
        'nav_all': '🏠 全部',
        'total_brands': '品牌总数',
        'total_coupons': '优惠总数',
        'last_checked': '更新日期',
        'verified_works': '✅ 已验证 · 有效',
        'report_expired': '报告过期',
        'submit_title': '➕ 提交优惠码',
        'submit_desc': '分享你发现的品牌优惠码，帮助更多人省钱',
        'submit_btn': '提交优惠码',
        'submit_note': '提交后我们将审核再上线',
        'submit_success': '✅ 感谢提交！',
        'submit_success_desc': '你的优惠码已提交审核，我们会尽快验证上线。',
        'browse_by': '📋 按分类浏览',
        'guides': '📝 导购文章',
        'footer_text': 'CouponBot · 真实DTC品牌优惠信息',
        'footer_verify': '使用前请确认优惠码仍有效',
        'footer_copyright': '开放数据，服务大家',
        'submit_link': '+ 提交优惠码',
        'lang_switch': 'English',
        'lang_href': '/',
        'faq_title': '❓ 常见问题',
        'cta_text': '🔍 浏览全部',
        'cta_suffix': '个品牌和优惠 →',
        'vote_yes': '有效',
        'vote_no': '过期',
        'back_home': '← 返回CouponBot首页',
    }
}

def load_votes():
    if not os.path.exists(VOTE_FILE):
        return {}
    try:
        with open(VOTE_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_votes(votes):
    os.makedirs(os.path.dirname(VOTE_FILE), exist_ok=True)
    with open(VOTE_FILE, 'w') as f:
        json.dump(votes, f, indent=2)

def load_coupons():
    """加载缓存优惠码"""
    if not os.path.exists(COUPON_FILE):
        return {'updated_at': None, 'total': 0, 'coupons': []}
    with open(COUPON_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

# ===== 首页FAQ（GEO核心）=====
HOMEPAGE_FAQ = [
    {"q": "What are DTC brands?", "a": "DTC (Direct-to-Consumer) brands sell directly to customers online, cutting out retail middlemen. This means better prices, higher quality, and unique products you won't find in stores."},
    {"q": "Are these coupon codes verified?", "a": "Yes, all coupon codes on CouponBot are sourced directly from brand websites. We verify them regularly, but recommend testing the code at checkout before completing your purchase."},
    {"q": "How do I use a coupon code?", "a": "Click the coupon code button to copy it, then paste the code at checkout on the brand's website. Most codes require an email signup to activate."},
    {"q": "Do you offer coupon codes for non-vegan products?", "a": "We focus on vegan, cruelty-free, and sustainable brands. Our 135+ brands across 20+ categories are carefully selected to align with ethical and eco-conscious values."},
    {"q": "How often are coupons updated?", "a": "We check brand websites regularly for new offers and remove expired codes. Check the 'Last checked' date on each page to see freshness."},
    {"q": "Can I get a refund if a coupon doesn't work?", "a": "CouponBot is a free reference site. We recommend trying another code from our list or checking the brand's current promotions directly."},
]

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
        {"q": "Does Casper offer a first-time buyer discount?", "a": "Yes, new customers can save 15% off their first order with email signup."},
        {"q": "Does Casper offer mattress discounts?", "a": "Yes, save $100 on Casper mattresses with current mattress deals."},
        {"q": "Does Casper have pillow deals?", "a": "Yes, get 20% off Casper pillows during seasonal sales."},
        {"q": "What is Casper's trial period?", "a": "Casper offers a 100-night risk-free trial on all mattresses."},
    ],
    'V-Dog': [
        {"q": "Does V-Dog offer a first order discount?", "a": "Yes, new customers get 20% off their first order through email signup."},
        {"q": "Does V-Dog have a repeat customer discount?", "a": "Yes, returning customers save 10% on subscription orders."},
        {"q": "Is V-Dog food vegan?", "a": "Yes, V-Dog makes 100% plant-based, vegan dog food with complete nutrition."},
    ],
    'Wild Earth': [
        {"q": "Does Wild Earth offer a first order discount?", "a": "Yes, new customers get 15% off their first order through email signup."},
        {"q": "Does Wild Earth have a satisfaction guarantee?", "a": "Yes, Wild Earth offers a 30-day money-back guarantee."},
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
    'Herbivore': [
        {"q": "Does Herbivore offer a first order discount?", "a": "Yes, new customers save 15% on their first order with code HERB15."},
        {"q": "Is Herbivore vegan?", "a": "Yes, Herbivore is 100% vegan, cruelty-free, and uses natural, plant-based ingredients."},
    ],
    'Ilia': [
        {"q": "Does ILIA offer a discount?", "a": "Yes, new customers get 20% off their first order with code ILIA20."},
        {"q": "Is ILIA makeup clean?", "a": "Yes, ILIA makes clean, vegan makeup with active levels of skincare ingredients."},
    ],
    'Drunk Elephant': [
        {"q": "Does Drunk Elephant offer a first order discount?", "a": "Yes, save 20% on your first order with code DE20."},
        {"q": "Is Drunk Elephant vegan?", "a": "Yes, Drunk Elephant is 100% vegan and cruelty-free, formulated without the Suspicious 6."},
    ],
    'Mate the Label': [
        {"q": "Does Mate the Label offer a discount?", "a": "Yes, new customers get 15% off with code MATELAB15."},
        {"q": "Is Mate the Label organic?", "a": "Yes, Mate the Label uses organic cotton and non-toxic dyes for all their apparel."},
    ],
    'Pangaia': [
        {"q": "Does Pangaia offer a first order discount?", "a": "Yes, save 20% with code PANG20."},
        {"q": "Is Pangaia sustainable?", "a": "Yes, Pangaia uses innovative materials like seaweed fiber, recycled cotton, and plant-based dyes."},
    ],
    'Grove Collaborative': [
        {"q": "Does Grove Collaborative offer a discount?", "a": "Yes, new customers save 15% with code GROVE15."},
        {"q": "Is Grove Collaborative eco-friendly?", "a": "Yes, Grove offers sustainable, plastic-free cleaning and home products."},
    ],
    'Magic Spoon': [
        {"q": "Does Magic Spoon offer a discount?", "a": "Yes, get 20% off your first order through email signup."},
        {"q": "Is Magic Spoon keto-friendly?", "a": "Yes, Magic Spoon is keto-friendly, high-protein, grain-free, and gluten-free cereal."},
    ],
    'Huel': [
        {"q": "Does Huel offer a first order discount?", "a": "Yes, new customers save 10% through email signup."},
        {"q": "Is Huel vegan?", "a": "Yes, Huel offers vegan options with complete plant-based nutrition."},
    ],
    'Oatly': [
        {"q": "Does Oatly offer a discount?", "a": "Yes, save 10% on your first order through email signup."},
        {"q": "Is Oatly vegan?", "a": "Yes, Oatly is 100% plant-based oat milk — dairy-free, vegan, and sustainable."},
    ],
    'Califia Farms': [
        {"q": "Does Califia Farms offer a discount?", "a": "Yes, save 20% on your first order through email signup."},
        {"q": "Is Califia Farms plant-based?", "a": "Yes, Califia Farms makes plant-based milks, creamers, and cold brew coffees."},
    ],
    'Biena': [
        {"q": "Does Biena offer a discount?", "a": "Yes, new customers save 20% through email signup."},
        {"q": "Are Biena snacks vegan?", "a": "Yes, Biena makes chickpea-based snacks that are vegan, gluten-free, and high in protein."},
    ],
    'Pela': [
        {"q": "Does Pela offer a discount?", "a": "Yes, save 15% on your first order through email signup."},
        {"q": "Are Pela cases compostable?", "a": "Yes, Pela makes 100% compostable phone cases from flax shive and plant-based biopolymers."},
    ],
    'Casetify': [
        {"q": "Does Casetify offer a discount?", "a": "Yes, get 20% off sitewide through email signup."},
        {"q": "Are Casetify cases eco-friendly?", "a": "Yes, Casetify offers a line of eco-friendly cases made from recycled materials and plant-based plastics."},
    ],
    'Nomad': [
        {"q": "Does Nomad offer a discount?", "a": "Yes, new customers save 15% through email signup."},
        {"q": "Does Nomad offer vegan products?", "a": "Yes, Nomad offers a range of vegan-friendly cables, chargers, and accessories alongside their leather line."},
    ],
    'Anker': [
        {"q": "Does Anker offer a discount?", "a": "Yes, save 10% on your first order through email signup."},
        {"q": "What does Anker make?", "a": "Anker makes high-quality chargers, cables, power banks, earbuds, and audio equipment."},
    ],
    'Nothing': [
        {"q": "Does Nothing offer a discount?", "a": "Yes, save 10% on Nothing products through email signup."},
        {"q": "What products does Nothing make?", "a": "Nothing makes transparent-design tech products including wireless earbuds and smartphones."},
    ],
    'Away': [
        {"q": "Does Away offer a first order discount?", "a": "Yes, new customers save 20% through email signup."},
        {"q": "What is Away's warranty?", "a": "Away offers a 100-day trial and a limited lifetime warranty on all luggage."},
    ],
    'Monos': [
        {"q": "Does Monos offer a discount?", "a": "Yes, save 15% on your first order through email signup."},
        {"q": "Is Monos sustainable?", "a": "Yes, Monos uses recycled materials and carbon-neutral shipping for their premium luggage."},
    ],
    'Paravel': [
        {"q": "Does Paravel offer a discount?", "a": "Yes, get 20% off sitewide through email signup."},
        {"q": "Is Paravel eco-friendly?", "a": "Yes, Paravel makes luggage from recycled materials and offsets carbon emissions on every order."},
    ],
    'Roam': [
        {"q": "Does Roam offer a discount?", "a": "Yes, new customers save 15% through email signup."},
        {"q": "Can I customize Roam luggage?", "a": "Yes, Roam offers fully customizable luggage with interchangeable colors and monogramming."},
    ],
    'Honest Company': [
        {"q": "Does Honest Company offer a discount?", "a": "Yes, new customers save 20% through email signup."},
        {"q": "Is Honest Company vegan?", "a": "Yes, Honest Company products are vegan, cruelty-free, and free from harsh chemicals."},
    ],
    "Burt's Bees Baby": [
        {"q": "Does Burt's Bees Baby offer a discount?", "a": "Yes, save 20% on your first order through email signup."},
        {"q": "Is Burt's Bees Baby organic?", "a": "Yes, Burt's Bees Baby makes GOTS-certified organic cotton baby clothes."},
    ],
    'Once Upon a Farm': [
        {"q": "Does Once Upon a Farm offer a discount?", "a": "Yes, get 20% off through email signup."},
        {"q": "Is Once Upon a Farm organic?", "a": "Yes, they make organic, plant-based baby food with cold-pressed nutrition."},
    ],
    'Lalo': [
        {"q": "Does Lalo offer a discount?", "a": "Yes, new customers save 15% through email signup."},
        {"q": "What does Lalo make?", "a": "Lalo makes modern, eco-friendly baby chairs, play gyms, and feeding essentials."},
    ],
    'Happy Family': [
        {"q": "Does Happy Family offer a discount?", "a": "Yes, save 20% on your first order through email signup."},
        {"q": "Is Happy Family organic?", "a": "Yes, Happy Family makes organic baby food and toddler snacks."},
    ],
    'ThirdLove': [
        {"q": "Does ThirdLove offer a discount?", "a": "Yes, new customers save 20% with code THIRD20."},
        {"q": "Does ThirdLove offer half sizes?", "a": "Yes, ThirdLove invented half-cup sizes for a perfect fit."},
    ],
    'CUUP': [
        {"q": "Does CUUP offer a discount?", "a": "Yes, save 15% on your first order with code CUUP15."},
        {"q": "Is CUUP vegan?", "a": "Yes, CUUP bras are made from vegan, sustainable materials."},
    ],
    'Parade': [
        {"q": "Does Parade offer a discount?", "a": "Yes, new customers get 20% off with code PARADE20."},
        {"q": "Is Parade sustainable?", "a": "Yes, Parade uses recycled materials and deadstock fabric for their underwear."},
    ],
    'MeUndies': [
        {"q": "Does MeUndies offer a discount?", "a": "Yes, save 20% on your first order with code MEUNDIES20."},
        {"q": "What is MeUndies known for?", "a": "MeUndies makes ultra-soft, comfortable underwear and loungewear in fun patterns."},
    ],
    'Lively': [
        {"q": "Does Lively offer a discount?", "a": "Yes, new customers save 20% with code LIVELY20."},
        {"q": "What does Lively make?", "a": "Lively makes wire-free bras, underwear, and loungewear for all-day comfort."},
    ],
    'Boy Smells': [
        {"q": "Does Boy Smells offer a discount?", "a": "Yes, save 15% on your first order with code BOY15."},
        {"q": "Are Boy Smells candles vegan?", "a": "Yes, Boy Smells candles are 100% vegan, coconut and beeswax free — made from natural waxes."},
    ],
    'Otherland': [
        {"q": "Does Otherland offer a discount?", "a": "Yes, get 20% off your first order with code OTHER20."},
        {"q": "What is Otherland?", "a": "Otherland makes art-inspired candles with unique, complex fragrances."},
    ],
    'P.F. Candle Co': [
        {"q": "Does P.F. Candle Co offer a discount?", "a": "Yes, save 20% with code PFC20."},
        {"q": "Are P.F. Candle Co candles vegan?", "a": "Yes, they use 100% natural soy wax, cotton wicks, and premium fragrance oils."},
    ],
    'Homesick': [
        {"q": "Does Homesick offer a discount?", "a": "Yes, new customers save 20% with code HOMESICK20."},
        {"q": "What makes Homesick unique?", "a": "Homesick candles are themed around places, memories, and experiences."},
    ],
    'Snif': [
        {"q": "Does Snif offer a discount?", "a": "Yes, save 15% on your first order with code SNIF15."},
        {"q": "Is Snif vegan?", "a": "Yes, Snif fragrances are 100% vegan and cruelty-free."},
    ],
    'Trade Coffee': [
        {"q": "Does Trade Coffee offer a discount?", "a": "Yes, new customers save 15% with code TRADE15."},
        {"q": "How does Trade Coffee work?", "a": "Trade connects you with specialty roasters based on your taste preferences."},
    ],
    'Atlas Coffee Club': [
        {"q": "Does Atlas Coffee Club offer a discount?", "a": "Yes, save 20% on your first order with code ATLAS20."},
        {"q": "What is Atlas Coffee Club?", "a": "Atlas delivers single-origin coffee from different countries around the world each month."},
    ],
    'Art of Tea': [
        {"q": "Does Art of Tea offer a discount?", "a": "Yes, save 15% on your first order with code TEAB15."},
        {"q": "Is Art of Tea organic?", "a": "Yes, Art of Tea offers organic, premium loose leaf teas from around the world."},
    ],
    'Wandering Bear': [
        {"q": "Does Wandering Bear offer a discount?", "a": "Yes, get 20% off with code Bemail signup."},
        {"q": "What is Wandering Bear?", "a": "Wandering Bear makes organic, shelf-stable cold brew coffee in convenient boxes."},
    ],
}

# NICHE_FAQ — 每个niche 5条FAQ，长尾关键词优化
NICHE_FAQ = {
    'home_garden': [
        {"q": "Which DTC furniture brand has the best sofa deals?", "a": "Article offers 15% off for new customers with code WELCOME15, while Burrow gives 20% off with SAVE20. West Elm runs regular sales up to 50% off. Compare prices across brands for the best sofa deal."},
        {"q": "Does Burrow offer free shipping on furniture?", "a": "Burrow offers free shipping on orders over $500. Smaller orders may have a shipping fee. Use coupon code SAVE20 for 20% off sitewide to offset shipping costs."},
        {"q": "What is the best eco-friendly furniture brand?", "a": "Sabai makes 100% vegan furniture from recycled and sustainable materials with 15% off for new customers. Avocado offers organic, non-toxic mattresses with $100 off using code AVO100."},
        {"q": "Does Brooklinen have bundle deals?", "a": "Yes, Brooklinen offers bundle savings on sheet sets and bedding bundles. New customers get 15% off with code HELLO15, and bundle codes like BUNDLEUP provide extra savings on sets."},
        {"q": "What is the return policy for Parachute?", "a": "Parachute offers free shipping on orders over $50 and a 30-day return policy. Their bedding and home products come with a satisfaction guarantee. Use code WELCOME20 for 20% off your first order."},
    ],
    'pet_supplies': [
        {"q": "What is the best vegan dog food brand?", "a": "V-Dog and Wild Earth are the top plant-based dog food brands. V-Dog offers 20% off first orders with email signup, plus 10% off recurring subscription orders. Wild Earth gives 15% off for new customers with a 30-day satisfaction guarantee."},
        {"q": "Does V-Dog have a discount code?", "a": "Yes, V-Dog offers 20% off first orders for new customers when you sign up for emails. Returning customers can save 10% on subscription orders. Free shipping is available on orders over $50."},
        {"q": "Is Litter-Robot worth the price?", "a": "Litter-Robot offers a $50 discount for first-time buyers, a 90-day in-home trial, and free shipping. While the upfront cost is higher than traditional litter boxes, the self-cleaning convenience saves time and reduces litter waste."},
        {"q": "Does Furbo dog camera have a coupon?", "a": "Yes, Furbo offers 20% off your first order with email signup. The Furbo dog camera lets you see, talk to, and toss treats to your dog remotely."},
        {"q": "What makes Wild Earth dog food different?", "a": "Wild Earth uses koji protein (a fungi-based protein) as its main ingredient. They offer 15% off first orders and a 30-day money-back guarantee."},
    ],
    'fitness_wellness': [
        {"q": "What is the best home gym equipment deal?", "a": "Hydrow offers $200 off rowing machines, Tonal gives $200 off smart home gyms, and Peloton has $100 off accessories with bike purchase. For budget options, NordicTrack offers up to $150 off select equipment."},
        {"q": "Does Peloton have a discount for accessories?", "a": "Yes, save $100 on Peloton accessories with any bike purchase. New members can also get a free 30-day trial of the Peloton App. The bundle deal saves up to $300."},
        {"q": "How much does Oura Ring cost with a coupon?", "a": "Oura Ring costs $299-$549 depending on model. Use the email signup code for $20 off. Free shipping is available on all orders. The ring tracks sleep, readiness, and activity."},
        {"q": "Does WHOOP have a free trial?", "a": "Yes, WHOOP offers your first month free with email signup. After the trial, membership is $30/month. Save 20% on the WHOOP band when you purchase an annual membership."},
        {"q": "What fitness tracker has the best discount?", "a": "WHOOP offers a free first month, Oura gives $20 off the ring, and EightSleep provides 10% off smart bed covers. Tonal ($200 off) and Hydrow ($200 off) offer the highest dollar discounts."},
    ],
    'beauty_skincare': [
        {"q": "What is the best clean beauty brand for skincare?", "a": "Youth to the People offers 20% off with email signup for vegan superfood skincare. Tower28 gives 15% off safe-for-sensitive-skin products. Biossance provides 10% off with vegan squalane skincare."},
        {"q": "Does Kosas have a makeup discount?", "a": "Kosas offers 15% off for new customers. Their clean makeup line includes foundation, concealer, lipstick, and brow products — all vegan, cruelty-free, and free from harsh chemicals."},
        {"q": "What vegan beauty brand has the best first-order discount?", "a": "Youth to the People and Glow Recipe both offer 20% off first orders — the highest among clean beauty brands. Tower28, Kosas, and Herbivore offer 15% off. Most require email signup."},
        {"q": "Is Tower 28 good for sensitive skin?", "a": "Yes, Tower28 is specifically formulated for sensitive skin — no alcohol, no fragrance, no harsh ingredients. New customers save 15% with email signup."},
        {"q": "Does Drunk Elephant have sales?", "a": "Drunk Elephant offers 20% off for new customers with email signup. They also run seasonal sales and value sets. Their products are 100% vegan and formulated without the Suspicious 6 ingredients."},
    ],
    'fashion': [
        {"q": "What is the best vegan sneaker brand?", "a": "Cariuma and Rothy's are the top vegan sneaker brands. Cariuma offers 20% off first orders with sustainable materials. Rothy's makes shoes from recycled plastic bottles with 20% off for new customers."},
        {"q": "Does Cariuma have a discount code?", "a": "Yes, Cariuma offers 20% off your first pair with email signup. They use sustainable materials like organic cotton, recycled rubber, and bamboo."},
        {"q": "Are Rothy's shoes sustainable?", "a": "Yes, Rothy's are made from recycled plastic bottles and are machine washable. The shoes are 100% vegan. New customers get 20% off with email signup."},
        {"q": "What organic cotton clothing brand has coupons?", "a": "Pact offers 20% off first orders with GOTS-certified organic cotton essentials. Tentree gives 15% off while planting 10 trees per item."},
        {"q": "Does Tentree plant trees?", "a": "Yes, Tentree plants 10 trees for every item purchased — over 100 million trees planted. New customers save 15% with email signup."},
    ],
    'eco_living': [
        {"q": "What is the best plastic-free cleaning brand?", "a": "Blueland is the leading plastic-free cleaning brand with tablet concentrates. Save 15% on starter kits. They offer cleaning, laundry, and personal care in reusable bottles."},
        {"q": "Does Blueland offer a starter kit discount?", "a": "Yes, Blueland offers 15% off their starter cleaning kit for new customers. Includes reusable bottles and cleaning tablets — no plastic waste."},
        {"q": "Is bamboo toilet paper better than regular?", "a": "Yes, bamboo toilet paper from Who Gives A Crap is softer, stronger, and more sustainable. 50% of profits go to sanitation projects."},
        {"q": "What zero waste home brands have discounts?", "a": "Blueland (15% off), Public Goods (10% off), Who Gives A Crap (20% off), and Etee (15% off) all offer new customer discounts."},
        {"q": "Does Grove Collaborative offer free shipping?", "a": "Yes, Grove Collaborative offers free shipping on orders over $30. New members save 15% with their first order."},
    ],
    'food_beverage': [
        {"q": "What plant-based milk brand has the best coupon?", "a": "Califia Farms offers 20% off sitewide — the best plant-based milk discount. Oatly gives 10% off first orders. Both offer subscription savings."},
        {"q": "Does Magic Spoon cereal have a discount?", "a": "Magic Spoon offers 20% off first orders with email signup. Their high-protein, grain-free cereal comes in fruity and dessert-inspired flavors."},
        {"q": "What is the best Huel discount?", "a": "Huel offers 10% off first orders. Subscription pricing saves up to 15% on recurring orders. Huel provides complete plant-based nutrition."},
        {"q": "Does Oatly offer a first order discount?", "a": "Yes, Oatly offers 10% off your first order. Subscribe & save for free shipping on recurring orders."},
        {"q": "What vegan snack brands have coupons?", "a": "Biena offers 20% off chickpea snacks. Partake Foods gives 20% off allergy-friendly cookies. No Cow provides 10% off protein bars."},
    ],
    'tech_gadgets': [
        {"q": "What is the best compostable phone case brand?", "a": "Pela makes 100% compostable phone cases from flax shive and plant-based biopolymers. 15% off for new customers. Full drop protection."},
        {"q": "Does Casetify have a promo code?", "a": "Yes, Casetify offers 20% off sitewide. Their eco-friendly Impact collection uses recycled materials and plant-based plastics."},
        {"q": "What is the best Anker coupon?", "a": "Anker offers 10% off first orders. They make high-quality chargers, power banks, cables, and earbuds."},
        {"q": "Does Nomad offer discounts on cables?", "a": "Nomad offers 15% off first orders. Premium, durable cables and charging accessories using recycled materials."},
        {"q": "What sustainable tech accessories save the most?", "a": "Nothing gives 10% off, Pela offers 15% off compostable cases, and Casetify provides 20% off eco-friendly cases."},
    ],
    'travel': [
        {"q": "What is the best luggage brand with a coupon?", "a": "Away offers 20% off first orders with a 100-day trial. Monos gives 15% off sustainable luggage. Paravel has 20% off carbon-neutral luggage."},
        {"q": "Does Away luggage have a warranty?", "a": "Yes, Away offers a limited lifetime warranty and 100-day risk-free trial. New customers save 20% with email signup."},
        {"q": "Is Monos luggage sustainable?", "a": "Yes, Monos uses recycled materials and carbon-neutral shipping. 15% off first orders."},
        {"q": "Does Paravel have eco-friendly luggage?", "a": "Yes, Paravel makes luggage from recycled materials and offsets carbon emissions. 20% off sitewide."},
        {"q": "What travel accessories have the best discounts?", "a": "Away (20% off), Monos (15% off), and Beis (15% off) offer the best first-order discounts on luggage."},
    ],
    'baby_kids': [
        {"q": "Does Honest Company have a discount code?", "a": "Yes, Honest Company offers 20% off first orders. Plant-based diapers and baby care that's vegan and cruelty-free."},
        {"q": "What is the best organic baby clothing brand?", "a": "Burt's Bees Baby offers GOTS-certified organic cotton baby clothes. 20% off for new customers."},
        {"q": "Does Once Upon a Farm offer baby food discounts?", "a": "Yes, Once Upon a Farm offers 20% off first orders with cold-pressed, organic baby food."},
        {"q": "What eco-friendly baby brands have coupons?", "a": "Honest Company (20% off), Burt's Bees Baby (20% off), Once Upon a Farm (20% off), and Lalo (15% off) all offer first-order discounts."},
        {"q": "What is the best vegan diaper brand?", "a": "Honest Company and Bambo Nature offer plant-based, eco-friendly diapers. Honest gives 20% off first orders."},
    ],
    'intimates': [
        {"q": "What is the best bra brand with a discount?", "a": "ThirdLove offers 20% off with half-cup sizing. CUUP gives 15% off premium bras. Lively has 20% off wire-free bras."},
        {"q": "Does ThirdLove have a first-time buyer discount?", "a": "Yes, ThirdLove offers 20% off for new customers with half-cup sizes for a perfect fit."},
        {"q": "What is the best sustainable underwear brand?", "a": "Parade uses recycled materials with 20% off first orders. MeUndies offers 20% off ultra-soft underwear."},
        {"q": "Does CUUP make vegan bras?", "a": "Yes, CUUP bras are made from vegan, sustainable materials. New customers save 15% with email signup."},
        {"q": "What intimates brand has the best subscription deal?", "a": "MeUndies offers 20% off first orders and free shipping. Lively and Parade also offer subscription options."},
    ],
    'candles_fragrance': [
        {"q": "What is the best vegan candle brand?", "a": "Boy Smells makes 100% vegan candles with gender-inclusive fragrances. 15% off first orders."},
        {"q": "Does Boy Smells offer a first order discount?", "a": "Yes, 15% off your first order. Coconut wax candles, all vegan and cruelty-free."},
        {"q": "How long do Otherland candles burn?", "a": "Otherland candles have 50-60 hour burn time with natural soy wax. 20% off first orders."},
        {"q": "What is the best eco-friendly candle brand?", "a": "P.F. Candle Co uses 100% natural soy wax. Homesick creates place-themed candles. Snif offers vegan fragrances."},
        {"q": "Does P.F. Candle Co have natural ingredients?", "a": "Yes, 100% natural soy wax, cotton wicks, premium fragrance oils — no phthalates or parabens."},
    ],
    'coffee_tea': [
        {"q": "What is the best coffee subscription with a discount?", "a": "Atlas Coffee Club offers 20% off first boxes from a different country each month. Trade Coffee gives 15% off."},
        {"q": "Does Atlas Coffee Club have a promo code?", "a": "Yes, 20% off your first order. Fresh-roasted single-origin coffee from featured countries."},
        {"q": "What is the best organic cold brew brand?", "a": "Wandering Bear makes organic, shelf-stable cold brew. 20% off first orders."},
        {"q": "Does Trade Coffee work with local roasters?", "a": "Yes, connects with 500+ specialty roasters. 15% off new orders with code TRADE15."},
        {"q": "What organic tea brands have coupons?", "a": "Art of Tea offers 15% off premium organic loose leaf teas from around the world."},
    ],
}

# NICHE_CONTENT — 每个niche的富内容（200-300字）
NICHE_CONTENT = {
    'home_garden': """
<h2>Save on Premium Home & Garden Brands</h2>
<p>DTC furniture brands have revolutionized how we furnish our homes. By cutting out retail middlemen, brands like Article, Burrow, Brooklinen, and Parachute offer designer-quality furniture, bedding, and home decor at direct-to-consumer prices. Whether you're looking for a modern sofa, a comfortable mattress, or eco-friendly home essentials, these brands combine style, sustainability, and value.</p>
<p>The best way to save on DTC home brands is through email signup discounts (typically 15-20% off first orders), bundle deals on sets, and seasonal sales during major holidays. Signing up for brand newsletters gives you access to the best exclusive offers.</p>
<p>For eco-conscious shoppers, Sabai makes 100% vegan furniture from recycled materials, and Avocado offers organic, non-toxic mattresses. These sustainable options don't compromise on quality or style.</p>
""",
    'pet_supplies': """
<h2>Save on Plant-Based Pet Food & Smart Pet Gadgets</h2>
<p>Pet care is expensive, but verified coupon codes help you save on everything from vegan dog food to smart pet cameras. V-Dog and Wild Earth lead the plant-based pet food revolution with science-backed, complete nutrition for dogs. For tech-savvy pet parents, Furbo cameras and Litter-Robot self-cleaning litter boxes make pet care easier.</p>
<p>Most pet brands offer 15-20% off first orders through email signup, plus subscribe & save discounts for recurring deliveries. This is especially valuable for pet food, where subscriptions ensure you never run out.</p>
""",
    'fitness_wellness': """
<h2>Save on Home Gym Equipment & Fitness Wearables</h2>
<p>Building a home gym is a significant investment, but verified coupon codes can save you hundreds on premium fitness equipment. From Peloton bikes and Tonal smart gyms to Hydrow rowers and NordicTrack equipment, DTC fitness brands offer substantial first-order discounts and seasonal sales.</p>
<p>Wearable fitness trackers like WHOOP, Oura Ring, and EightSleep provide valuable health insights with free trials and first-month deals. The best savings opportunities come during New Year, Memorial Day, and Black Friday sales, when discounts can reach $200-300 off premium equipment.</p>
""",
    'beauty_skincare': """
<h2>Save on Clean, Vegan & Cruelty-Free Beauty</h2>
<p>Clean beauty brands prove that effective skincare and makeup don't need harsh chemicals or animal testing. Youth to the People, Tower 28, Kosas, Biossance, and Drunk Elephant offer high-performance, vegan formulations that are gentle on your skin and the planet.</p>
<p>The best way to save on clean beauty is through email signup for 10-20% off first orders, gift sets that offer better value than individual products, and subscription discounts on favorites. Most brands use sustainable packaging and transparent ingredient sourcing.</p>
""",
    'fashion': """
<h2>Save on Sustainable & Vegan Fashion</h2>
<p>Sustainable fashion brands prove you can look good while doing good. Cariuma and Rothy's make premium vegan sneakers from recycled and sustainable materials. Tentree plants 10 trees per item, and Pact uses GOTS-certified organic cotton. These brands are leading the shift toward ethical, eco-conscious fashion.</p>
<p>Signing up for email newsletters gives you 15-20% off first orders. Many brands also offer referral programs where both you and a friend save $15-25. Seasonal sales during Earth Day and Black Friday provide additional savings.</p>
""",
    'eco_living': """
<h2>Save on Plastic-Free & Sustainable Home Products</h2>
<p>Reducing plastic waste at home is easier with eco-friendly DTC brands. Blueland's tablet-based cleaning system eliminates plastic bottles, Public Goods offers sustainable home essentials, and Who Gives A Crap makes bamboo toilet paper that gives back.</p>
<p>Most eco-friendly brands offer 10-20% off first orders plus subscribe & save discounts. Bundles (starter kits, variety packs) offer the best value for new customers looking to switch to plastic-free alternatives.</p>
""",
    'food_beverage': """
<h2>Save on Plant-Based Food & Beverages</h2>
<p>Plant-based eating is more accessible than ever with DTC food brands. Magic Spoon makes keto-friendly vegan cereal, Huel provides complete plant-based nutrition, and Oatly and Califia Farms offer delicious dairy-free milks. Biena and No Cow supply healthy vegan snacks.</p>
<p>Subscription savings are the biggest money-saver for plant-based food — most brands offer 10-20% off recurring orders. First-time buyers typically get 15-20% off through email signup.</p>
""",
    'tech_gadgets': """
<h2>Save on Sustainable Tech Accessories</h2>
<p>Tech accessories don't have to create e-waste. Pela's compostable phone cases, Casetify's recycled material cases, and Nomad's premium cables prove that great design and sustainability can coexist. Anker and Nothing offer innovative chargers, earbuds, and audio gear.</p>
<p>First-order discounts range from 10-20% off across most tech accessory brands. Bundling multiple items often unlocks additional savings. Major sales events like Prime Day and Black Friday offer the deepest discounts.</p>
""",
    'travel': """
<h2>Save on Premium Luggage & Travel Gear</h2>
<p>Quality luggage is an investment in stress-free travel. Away, Monos, Paravel, and Roam make premium, durable suitcases with sustainable materials and thoughtful design. From hard-shell carry-ons to checked luggage, these DTC brands offer excellent warranties and risk-free trials.</p>
<p>New customers save 15-20% with email signup. Away offers a limited lifetime warranty and 100-day trial. Monos provides carbon-neutral shipping. Seasonal sales offer the best deals.</p>
""",
    'baby_kids': """
<h2>Save on Organic & Eco-Friendly Baby Essentials</h2>
<p>Raising little ones is expensive, but organic and eco-friendly baby brands help you save while keeping your baby safe. Honest Company makes plant-based diapers, Burt's Bees Baby offers GOTS-certified organic clothes, and Once Upon a Farm provides organic baby food.</p>
<p>Most baby brands offer 15-20% off first orders. Subscriptions for diapers, wipes, and baby food add 10-15% off recurring orders. Baby registries unlock completion discounts.</p>
""",
    'intimates': """
<h2>Save on Comfortable, Sustainable Underwear & Bras</h2>
<p>Comfortable, well-fitting underwear and bras don't have to cost a fortune. ThirdLove invented half-cup bra sizing, CUUP makes premium vegan bras, Parade uses recycled materials, and MeUndies delivers ultra-soft comfort.</p>
<p>Email signup discounts of 15-20% off first orders are standard. Many offer buy more save more promotions and subscription options that ensure fresh pairs at discounted prices.</p>
""",
    'candles_fragrance': """
<h2>Save on Vegan Candles & Home Fragrance</h2>
<p>Create the perfect ambiance with vegan, cruelty-free candles and home fragrances. Boy Smells makes gender-inclusive candles with coconut wax, Otherland offers art-inspired scents, P.F. Candle Co uses natural soy wax.</p>
<p>New customers save 15-20% off first orders. Gift sets and discovery packs offer the best value for trying multiple scents.</p>
""",
    'coffee_tea': """
<h2>Save on Specialty Coffee & Tea Subscriptions</h2>
<p>Elevate your daily brew with specialty coffee and tea subscriptions. Atlas Coffee Club delivers single-origin coffee from a different country each month. Trade Coffee matches you with roasters based on your taste. Wandering Bear provides organic cold brew.</p>
<p>First boxes are discounted 15-20%. Subscription pricing saves 10-15% on recurring orders with free shipping.</p>
""",
}



# ===== 品牌购物政策（按品类）=====
BRAND_POLICIES = {
    'pet_supplies': {'return': '30-day return policy', 'shipping': 'Free shipping on orders over $49', 'warranty': 'Varies by brand', 'return_url': ''},
    'home_garden': {'return': '30-day return policy', 'shipping': 'Free shipping on most orders', 'warranty': '1-year warranty on most products', 'return_url': ''},
    'beauty_skincare': {'return': '30-day return policy', 'shipping': 'Free shipping on orders over $50', 'warranty': 'Satisfaction guaranteed', 'return_url': ''},
    'fashion': {'return': '30-day return policy', 'shipping': 'Free shipping on orders over $50', 'warranty': 'Varies by brand', 'return_url': ''},
    'fitness_wellness': {'return': '30-day risk-free trial', 'shipping': 'Free shipping on most orders', 'warranty': '1-year warranty', 'return_url': ''},
    'eco_living': {'return': '30-day return policy', 'shipping': 'Free shipping on orders over $50', 'warranty': 'Varies by brand', 'return_url': ''},
    'food_beverage': {'return': 'Satisfaction guaranteed', 'shipping': 'Free shipping on subscriptions', 'warranty': 'Money-back guarantee', 'return_url': ''},
    'tech_gadgets': {'return': '30-day return policy', 'shipping': 'Free shipping', 'warranty': '1-2 year warranty', 'return_url': ''},
    'baby_kids': {'return': '30-day return policy', 'shipping': 'Free shipping on orders over $50', 'warranty': 'Varies by brand', 'return_url': ''},
    'travel': {'return': '30-day return policy', 'shipping': 'Free shipping & returns', 'warranty': 'Varies by brand', 'return_url': ''},
    'candles_fragrance': {'return': '30-day return policy', 'shipping': 'Free shipping on orders over $50', 'warranty': 'Varies by brand', 'return_url': ''},
    'coffee_tea': {'return': 'Satisfaction guaranteed', 'shipping': 'Free shipping on subscriptions', 'warranty': 'Money-back guarantee', 'return_url': ''},
    'intimates': {'return': '30-day return policy', 'shipping': 'Free shipping on orders over $50', 'warranty': 'Varies by brand', 'return_url': ''},
    'social_impact': {'return': '30-day return policy or satisfaction guarantee', 'shipping': 'Free shipping on most orders', 'warranty': 'Varies by brand', 'return_url': ''},
    'vegan_food': {'return': 'Satisfaction guaranteed', 'shipping': 'Free shipping on subscriptions', 'warranty': 'Money-back guarantee', 'return_url': ''},
    'personal_care': {'return': '30-day return policy', 'shipping': 'Free shipping on orders over $50', 'warranty': 'Satisfaction guaranteed', 'return_url': ''},
    'accessories': {'return': '30-day return policy', 'shipping': 'Free shipping on orders over $50', 'warranty': 'Varies by brand', 'return_url': ''},
    'mattresses': {'return': '100-night risk-free trial', 'shipping': 'Free shipping', 'warranty': '10-25 year warranty', 'return_url': ''},
    'fitness_expanded': {'return': '30-day risk-free trial', 'shipping': 'Free shipping on most orders', 'warranty': '1-year warranty', 'return_url': ''},
    'fashion_expanded': {'return': '30-day return policy', 'shipping': 'Free shipping on orders over $50', 'warranty': 'Varies by brand', 'return_url': ''},
    'food_snacks': {'return': 'Satisfaction guaranteed', 'shipping': 'Free shipping on subscriptions', 'warranty': 'Money-back guarantee', 'return_url': ''},
    'tech_expanded': {'return': '30-day return policy', 'shipping': 'Free shipping', 'warranty': '1-2 year warranty', 'return_url': ''},
    'beauty_expanded': {'return': '30-day return policy', 'shipping': 'Free shipping on orders over $50', 'warranty': 'Satisfaction guaranteed', 'return_url': ''},
}

# 省钱技巧（按品类）
BRAND_TIPS = {
    'pet_supplies': ['Sign up for email to get first-order discount', 'Subscribe & save for up to 20% off recurring orders', 'Stock up during major sales (Memorial Day, Black Friday)'],
    'home_garden': ['New customer email signup = best first-time discount', 'Bundle items to hit free shipping threshold', 'Major furniture sales: Labor Day, Memorial Day, Presidents Day'],
    'beauty_skincare': ['Sign up for email = 10-20% off first order', 'Subscribe & save for recurring discounts', 'Gift sets often offer best value per item'],
    'fashion': ['Email signup = 15-20% off first order', 'Clearance sections often have extra % off', 'Refer a friend programs = $20-$50 credit each'],
    'fitness_wellness': ['Check for open-box/refurbished equipment deals', 'New Year and Memorial Day = deepest discounts', 'Financing options available for premium equipment'],
    'eco_living': ['Subscribe & save for best recurring price', 'Bundles offer better value than single items', 'Referral programs = store credit for both parties'],
    'food_beverage': ['Subscribe & save for 10-20% off each order', 'Variety packs = value', 'First order often comes with welcome discount'],
    'tech_gadgets': ['Look for refurbished/open-box deals', 'Bundle accessories = save 10-15%', 'Major sales: Prime Day, Black Friday, Cyber Monday'],
    'baby_kids': ['Subscribe & save for recurring essentials', 'Create a baby registry for completion discounts', 'Bundle deals for multiple items'],
    'travel': ['Email signup for first-time discount', 'Outlet/clearance sections for best deals', 'Major seasonal sales: Memorial Day, Black Friday'],
    'candles_fragrance': ['Subscribe for recurring scent deliveries', 'Gift sets offer best value', 'Seasonal sales = 20-30% off'],
    'coffee_tea': ['Subscribe & save free shipping + 10-20% off', 'Variety packs to try new flavors', 'Holiday blends released Oct-Nov'],
    'intimates': ['Email signup = 15-20% off', 'Buy more save more bundles', 'Seasonal sales offer best value'],
    'social_impact': ['Email signup for first-time discount (10-20% off)', 'Referral programs = $20-25 credit each way', 'Major sales: Black Friday, Earth Day, Giving Tuesday'],
    'vegan_food': ['Subscribe & save for 10-20% off recurring orders', 'First order welcome discount (15-20% off)', 'Bundle deals save on variety packs'],
    'personal_care': ['Subscribe & save for recurring essentials (10-20% off)', 'Starter kits offer best value for new customers', 'Bundles save 15-25% vs buying individually'],
    'accessories': ['Email signup for 10-20% off first order', 'Referral programs earn $20-30 credit', 'Seasonal sales (Black Friday, holiday) = deepest discounts'],
    'mattresses': ['Best deals: Presidents Day, Memorial Day, Black Friday ($100-300 off)', 'Email signup = 10-15% off first order', 'Bundle (mattress + pillows + sheets) saves 20-30%'],
    'fitness_expanded': ['Major sales: New Year, Memorial Day, Black Friday = deepest discounts', 'Open-box/refurbished equipment = save 20-40%', 'Financing options available on premium equipment'],
    'fashion_expanded': ['Email signup = 15-20% off first order', 'Subscribe to SMS alerts for flash sales', 'Referral programs = $20-50 credit each'],
    'food_snacks': ['Subscribe & save for 10-20% off recurring orders', 'Variety packs offer best value to try new flavors', 'New customer discount = 15-20% off first order'],
    'tech_expanded': ['Bundle accessories = save 10-15%', 'Refurbished/open-box deals = save 20-40%', 'Major sales: Prime Day, Black Friday, Cyber Monday'],
    'beauty_expanded': ['Email signup = 15-20% off first order', 'Subscribe & save for recurring discounts', 'Gift sets offer best value per item (save 20-30%)'],
}

def get_brand_niche(brand_name):
    """查找品牌属于哪个品类"""
    data = load_coupons()
    for c in data['coupons']:
        if c['brand'].lower() == brand_name.lower():
            for key, niche in TARGET_NICHES.items():
                if brand_name.lower() in [b.lower() for b in niche['brands']]:
                    return key
    return None

def get_competitor_brands(brand_name):
    """获取同品类竞品品牌"""
    for key, niche in TARGET_NICHES.items():
        brands = [b for b in niche['brands'] if b.lower() != brand_name.lower()]
        if len(brands) < len(niche['brands']):  # 找到了当前品牌
            return brands[:5]  # 最多5个
    return []

def get_brand_details(brand_name):
    """获取品牌详情：购物政策+省钱技巧+竞品"""
    niche_key = get_brand_niche(brand_name)
    policies = BRAND_POLICIES.get(niche_key, BRAND_POLICIES['home_garden'])
    tips = BRAND_TIPS.get(niche_key, BRAND_TIPS['home_garden'])
    competitors = get_competitor_brands(brand_name)
    
    # 从优惠券数据提取最佳折扣作为省钱技巧补充
    try:
        data = load_coupons()
        brand_coupons = [c for c in data['coupons'] if c['brand'].lower() == brand_name.lower()]
        best_discount = ''
        for c in brand_coupons:
            disc = c.get('discount', '')
            if any(k in disc for k in ['OFF', '%', 'Free', 'Save', '$']):
                best_discount = disc
                break
        if best_discount:
            has_email = any('new' in c.get('title','').lower() or 'welcome' in c.get('title','').lower() for c in brand_coupons)
            if has_email:
                tips.insert(0, f'Current best deal: {best_discount} — sign up for emails')
    except Exception:
        pass
    
    return {
        'policies': policies,
        'tips': tips[:4],  # 最多4条
        'competitors': competitors,
        'niche_key': niche_key,
    }

def get_brand_faq(brand_name):
    """获取品牌的FAQ，有手写则用手写，没有则从优惠券数据自动生成"""
    custom = BRAND_FAQ.get(brand_name)
    if custom:
        return custom

    # Auto-generate from coupon data
    try:
        data = load_coupons()
    except Exception:
        return BRAND_FAQ['default']

    brand_coupons = [c for c in data['coupons'] if c['brand'].lower() == brand_name.lower()]
    if not brand_coupons:
        return BRAND_FAQ['default']

    faq = []
    seen_q = set()

    # 1. Best deal question
    best = None
    for c in brand_coupons:
        disc = c.get('discount', '')
        if any(k in disc for k in ['OFF', '%', 'Free', 'Save', '$', 'Off']):
            best = c
            break
    if not best:
        best = brand_coupons[0]

    if best:
        q = f"What is the best {brand_name} deal right now?"
        a = f"The best {brand_name} offer is {best.get('title', best.get('discount', 'available'))}."
        if best.get('code'):
            a += f" Use code {best['code']} at checkout."
        faq.append({"q": q, "a": a})
        seen_q.add(q.lower())

    # 2. First-time/new customer discount
    new_offers = [c for c in brand_coupons
                  if any(k in c.get('title','').lower() for k in ['new', 'welcome', 'first'])]
    if new_offers:
        nc = new_offers[0]
        q = f"Does {brand_name} offer a first-time customer discount?"
        a = f"Yes, new customers can get {nc['discount']}."
        if nc.get('code'):
            a += f" Use code {nc['code']} on your first order."
        faq.append({"q": q, "a": a})
        seen_q.add(q.lower())

    # 3. Free shipping
    free_offers = [c for c in brand_coupons if 'free' in c.get('title','').lower() and 'ship' in c.get('title','').lower()]
    if free_offers:
        fc = free_offers[0]
        q = f"Does {brand_name} offer free shipping?"
        a = f"Yes, {fc.get('title', 'free shipping is available')}."
        if fc.get('code'):
            a += f" Use code {fc['code']}."
        faq.append({"q": q, "a": a})
        seen_q.add(q.lower())

    # 4. Subscription / save deals
    sub_offers = [c for c in brand_coupons if any(k in c.get('title','').lower() for k in ['subscrib', 'save', 'repeat'])]
    if sub_offers:
        sc = sub_offers[0]
        q = f"Does {brand_name} have a subscription or repeat customer discount?"
        a = f"Yes, {sc.get('title', 'repeat customers can save')}."
        if sc.get('code'):
            a += f" Code: {sc['code']}."
        faq.append({"q": q, "a": a})
        seen_q.add(q.lower())

    # 5. Free trial (if applicable)
    trial_offers = [c for c in brand_coupons if 'trial' in c.get('title','').lower()]
    if trial_offers:
        tc = trial_offers[0]
        q = f"Does {brand_name} offer a free trial?"
        a = f"Yes, {tc.get('title', 'a free trial is available')}."
        if tc.get('code'):
            a += f" Use code {tc['code']}."
        faq.append({"q": q, "a": a})

    # 6. How to use
    q = f"How do I use a {brand_name} coupon?"
    if q.lower() not in seen_q:
        a = f"Click the offer to go to {brand_name}'s website. Add items to your cart, then enter the coupon code at checkout."
        faq.append({"q": q, "a": a})

    # 7. Verified question
    q = f"Are {brand_name} coupons verified?"
    if q.lower() not in seen_q:
        a = f"Yes. All {brand_name} deals on CouponBot are sourced directly from the brand website or official channels."
        faq.append({"q": q, "a": a})

    # 8. How often updated
    q = f"How often are {brand_name} coupons updated?"
    if q.lower() not in seen_q:
        a = f"We check {brand_name} deals regularly. Bookmark this page for the latest offers."
        faq.append({"q": q, "a": a})

    # Ensure at least 5 questions
    if len(faq) < 5:
        generic_questions = [
            {"q": f"What is the return policy for {brand_name}?",
             "a": f"Check {brand_name}'s website for their current return policy. Most DTC brands offer 30-day returns."},
            {"q": f"Does {brand_name} ship internationally?",
             "a": f"Most DTC brands ship within the US. Check {brand_name}'s shipping page for international options."},
        ]
        for gq in generic_questions:
            if gq['q'].lower() not in seen_q and len(faq) < 7:
                faq.append(gq)

    return faq

def make_faqpage_schema(questions):
    """生成FAQPage JSON-LD"""
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": item["q"], "acceptedAnswer": {"@type": "Answer", "text": item["a"]}}
            for item in questions
        ]
    }

def make_faq_html(questions):
    """生成FAQ的HTML展示"""
    html = ''
    for i, item in enumerate(questions):
        html += f'''<div class="faq-item" itemscope itemprop="mainEntity" itemtype="https://schema.org/Question">
    <div class="faq-q" onclick="toggleFaq(this)" itemprop="name">{item["q"]}</div>
    <div class="faq-a" itemscope itemprop="acceptedAnswer" itemtype="https://schema.org/Answer">
        <div itemprop="text">{item["a"]}</div>
    </div>
</div>
'''
    return html

def generate_homepage_schema():
    """首页Schema：Organization + WebSite + FAQPage + WebPage"""
    faq_schema = make_faqpage_schema(HOMEPAGE_FAQ)
    return {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "Organization",
                "name": "CouponBot",
                "url": SITE_URL,
                "description": "Real deals and offers from top DTC brands.",
            },
            {
                "@type": "WebSite",
                "name": "CouponBot",
                "url": SITE_URL,
            },
            {
                "@type": "WebPage",
                "name": "Best DTC Brand Deals & Offers 2026",
                "description": "Real deals from top DTC brands across 20+ categories. Email signup discounts, free shipping, subscription savings — 135+ brands.",
                "dateModified": TODAY,
            },
            faq_schema,
        ]
    }

def generate_brand_schema(brand_name, coupons):
    """生成品牌的Schema.org JSON-LD"""
    schema_offers = []
    for c in coupons[:5]:
        disc = c.get('discount', '')
        schema_offers.append({
            "@type": "Offer",
            "description": c.get('title', f"{brand_name} promo code {c['code']}"),
            "discount": disc if disc else "Available",
            "discountCode": c['code'],
            "availability": "https://schema.org/InStock",
            "url": f"{SITE_URL}/brand/{brand_name.lower()}",
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
            make_faqpage_schema(get_brand_faq(brand_name)),
            {
                "@type": "WebPage",
                "name": f"{brand_name} Coupon Codes 2026",
                "description": f"Find the latest {brand_name} coupon codes, promo codes, and discounts. Updated regularly.",
                "dateModified": TODAY,
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
        "dateModified": TODAY,
    }

def generate_article_schema(title, description, slug, faq_questions=None):
    """文章Schema：Article + FAQPage"""
    article_url = f"{SITE_URL}/article/{slug}"
    graph = [
        {
            "@type": "Article",
            "headline": title,
            "description": description,
            "datePublished": TODAY,
            "dateModified": TODAY,
            "author": {"@type": "Organization", "name": "CouponBot"},
            "publisher": {"@type": "Organization", "name": "CouponBot", "url": SITE_URL},
            "mainEntityOfPage": {"@type": "WebPage", "@id": article_url},
        }
    ]
    if faq_questions:
        graph.append(make_faqpage_schema(faq_questions))
    return {"@context": "https://schema.org", "@graph": graph}

@app.route('/')
def index():
    return _index('en')

@app.route('/zh/')
def index_zh():
    return _index('zh')

def _index(lang='en'):
    data = load_coupons()
    schema = generate_homepage_schema()
    faq_html = make_faq_html(HOMEPAGE_FAQ)
    # Popular brands for homepage: pick top brands from each popular category
    popular_brands = ['Article', 'Burrow', 'Casper', 'Peloton', 'Away', 'Allbirds',
                      'TOMS', 'V-Dog', 'Magic Spoon', 'Cariuma', 'Blueland', 'Native',
                      'Mejuri', 'Supergoop', 'Everlane', 'Trade Coffee']
    return render_template('index.html',
                           coupons=data['coupons'],
                           total=data['total'],
                           updated=data.get('updated_at', ''),
                           niches=TARGET_NICHES,
                           ga_id=GA_MEASUREMENT_ID,
                           gc_domain=GOATCOUNTER_DOMAIN,
                           umami_url=UMAMI_URL,
                           umami_site_id=UMAMI_WEBSITE_ID,
                           schema=json.dumps(schema, indent=2),
                           faq=HOMEPAGE_FAQ,
                           brand_faq_data=None,
                           faq_html=faq_html,
                           popular_brands=popular_brands,
                           lang=lang,
                           lang_data=LANG[lang])

@app.route('/api/coupons')
def api_coupons():
    data = load_coupons()
    brand = request.args.get('brand', '').lower()
    if brand:
        data['coupons'] = [c for c in data['coupons'] if brand in c['brand'].lower()]
        data['total'] = len(data['coupons'])
    resp = jsonify(data)
    resp.headers['X-Robots-Tag'] = 'all'
    return resp

@app.route('/brand/<brand_name>')
def brand_page(brand_name):
    return _brand_page(brand_name, 'en')

@app.route('/zh/brand/<brand_name>')
def brand_page_zh(brand_name):
    return _brand_page(brand_name, 'zh')

def _brand_page(brand_name, lang='en'):
    data = load_coupons()
    brand_coupons = [c for c in data['coupons'] if c['brand'].lower() == brand_name.lower()]
    brand_name_display = brand_coupons[0]['brand'] if brand_coupons else brand_name.title()

    schema = generate_brand_schema(brand_name_display, brand_coupons)
    # Breadcrumb for SEO
    breadcrumb = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE_URL}/"},
            {"@type": "ListItem", "position": 2, "name": brand_name_display, "item": f"{SITE_URL}/brand/{brand_name_display.lower()}"}
        ]
    }
    faq = get_brand_faq(brand_name_display)
    brand_details = get_brand_details(brand_name_display)
    brand_faq_data = BRAND_FAQ.get(brand_name_display, None)
    faq_html = make_faq_html(faq)

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
                           breadcrumb=json.dumps(breadcrumb),
                           faq=faq,
                           brand_details=brand_details,
                           brand_faq_data=brand_faq_data,
                           faq_html=faq_html,
                           lang=lang,
                           lang_data=LANG[lang])

@app.route('/niche/<niche_key>')
def niche_page(niche_key):
    return _niche_page(niche_key, 'en')

@app.route('/zh/niche/<niche_key>')
def niche_page_zh(niche_key):
    return _niche_page(niche_key, 'zh')

def _niche_page(niche_key, lang='en'):
    data = load_coupons()
    niche = TARGET_NICHES.get(niche_key)
    if not niche:
        return 'Niche not found', 404

    brands = [b.lower() for b in niche['brands']]
    niche_coupons = [c for c in data['coupons'] if c['brand'].lower() in brands]

    schema = generate_niche_schema(niche['name'], niche_coupons)
    niche_faq = NICHE_FAQ.get(niche_key, None)
    niche_content = NICHE_CONTENT.get(niche_key, None)
    if niche_faq:
        faq_schema = make_faqpage_schema(niche_faq)
        schema = {"@context": "https://schema.org", "@graph": [schema, faq_schema]}
    faq_html = make_faq_html(niche_faq) if niche_faq else None

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
                           faq=niche_faq,
                           niche_content=niche_content,
                           brand_faq_data=None,
                           faq_html=faq_html,
                           lang=lang,
                           lang_data=LANG[lang])

@app.route('/robots.txt')
def robots():
    return """User-agent: *
Allow: /
Sitemap: https://simumu.pythonanywhere.com/sitemap.xml
""", 200, {'Content-Type': 'text/plain'}

@app.route('/static/<path:filename>')
def serve_static(filename):
    safe = os.path.join(os.path.dirname(__file__), 'static', filename.replace('..', ''))
    if os.path.exists(safe):
        return open(safe, 'rb').read(), 200, {'Content-Type': 'image/png'}
    return '', 404

@app.route('/sitemap.xml')
def sitemap():
    data = load_coupons()
    brands = set(c['brand'] for c in data['coupons'])
    urls = ['/']
    for key in TARGET_NICHES:
        urls.append(f'/niche/{key}')
    for brand in brands:
        urls.append(f'/brand/{brand.lower()}')
    for slug in ARTICLES:
        urls.append(f'/article/{slug}')
    # Chinese (zh) versions
    urls.append('/zh/')
    for key in TARGET_NICHES:
        urls.append(f'/zh/niche/{key}')
    for brand in brands:
        urls.append(f'/zh/brand/{brand.lower()}')
    for slug in ARTICLES:
        urls.append(f'/zh/article/{slug}')

    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for u in urls:
        xml += f'  <url><loc>{SITE_URL}{u}</loc></url>\n'
    xml += '</urlset>'
    return xml, 200, {'Content-Type': 'application/xml'}

# ===== 文章FAQ（每篇文章专用）=====
ARTICLE_FAQ = {
    'vegan-pet-food-coupons': [
        {"q": "Is vegan dog food healthy?", "a": "Yes, plant-based dog food from brands like V-Dog and Wild Earth provides complete nutrition with plant proteins, essential amino acids, and added vitamins. Many dogs thrive on vegan diets."},
        {"q": "Do vegan dog food coupons really work?", "a": "Yes, codes from V-Dog and Wild Earth are verified and active at checkout. Check the pet supplies category for current deals."},
        {"q": "Which is better — V-Dog or Wild Earth?", "a": "Both are excellent. V-Dog offers a more established line and a 20% first-order discount, while Wild Earth uses koji protein and offers a 30-day satisfaction guarantee."},
    ],
    'home-furniture-deals': [
        {"q": "Which furniture brand has the best coupon?", "a": "Burrow offers 20% off sitewide, while Avocado gives $100 off mattresses. Article and Parachute both offer 15-20% off for new customers."},
        {"q": "Is eco-friendly furniture worth it?", "a": "Yes, brands like Sabai and Avocado use sustainable materials and are 100% vegan. They offer comparable quality to traditional brands with better environmental impact."},
    ],
    'fitness-equipment-coupons': [
        {"q": "Which fitness brand saves me the most?", "a": "Hydrow saves you $200 on a rower, Tonal offers $200 off, and Peloton gives $100 off accessories plus a free trial. NordicTrack saves up to $150."},
        {"q": "Can I stack multiple fitness coupons?", "a": "Usually not — most fitness brands accept one promo code per order. Choose the code that saves you the most."},
    ],
    'vegan-beauty-coupons': [
        {"q": "Is clean beauty really better?", "a": "Clean beauty products are free from parabens, phthalates, sulfates, and animal-derived ingredients. They're gentler on your skin and better for the environment."},
        {"q": "Which vegan beauty brand saves me the most?", "a": "Youth to the People (20% off), Tower 28 (15% off), and Kosas (15% off) offer the best first-order discounts."},
    ],
    'sustainable-fashion-coupons': [
        {"q": "What makes a fashion brand sustainable?", "a": "Sustainable brands use organic or recycled materials, pay fair wages, minimize waste, and often offer vegan alternatives. Cariuma uses sustainable materials, Tentree plants 10 trees per item."},
        {"q": "Are vegan sneakers as durable as leather?", "a": "Yes, vegan sneakers from Cariuma and Rothy's use high-quality recycled and synthetic materials that are durable, water-resistant, and machine washable."},
    ],
    'eco-friendly-home-coupons': [
        {"q": "Are plastic-free cleaning products effective?", "a": "Yes, tablet-based cleaners from Blueland are just as effective as liquid cleaners. They dissolve in water and come in reusable bottles — no plastic waste."},
        {"q": "Is bamboo toilet paper worth it?", "a": "Yes, bamboo toilet paper from Who Gives A Crap is softer, stronger, and more sustainable than traditional paper. Plus they donate 50% of profits to sanitation projects."},
    ],
    'vegan-food-beverage-coupons': [
        {"q": "Which plant-based milk brand saves me the most?", "a": "Califia Farms offers 20% off sitewide through email signup, and Oatly gives 10% off first orders. Both are excellent dairy-free alternatives."},
        {"q": "Are vegan meal replacements nutritious?", "a": "Yes, Huel provides complete plant-based nutrition with protein, carbs, fats, and 26 essential vitamins and minerals in every serving."},
    ],
    'tech-gadget-coupons': [
        {"q": "Are compostable phone cases durable?", "a": "Yes, Pela cases are made from flax shive and plant-based biopolymers. They're fully compostable but provide the same drop protection as traditional cases."},
    ],
    'travel-luggage-coupons': [
        {"q": "Which luggage brand offers the best warranty?", "a": "Away offers a limited lifetime warranty and 100-day trial. Monos and Paravel also offer excellent warranties with sustainable materials."},
    ],
    'baby-kids-coupons': [
        {"q": "What makes baby products 'clean'?", "a": "Clean baby products are free from harsh chemicals, phthalates, and synthetic fragrances. Brands like Honest Company and Burt's Bees Baby use organic, plant-based ingredients."},
    ],
    'intimates-loungewear-coupons': [
        {"q": "Which intimates brand offers the best discount?", "a": "ThirdLove and Parade both offer 20% off for new customers. MeUndies also gives 20% off with code MEUNDIES20."},
    ],
    'candles-home-fragrance-coupons': [
        {"q": "Are soy candles better than paraffin?", "a": "Yes, soy wax candles (like Boy Smells and P.F. Candle Co) burn cleaner, last longer, and don't release toxic chemicals unlike paraffin wax."},
    ],
    'coffee-tea-subscription-coupons': [
        {"q": "Which coffee subscription saves me the most?", "a": "Atlas Coffee Club offers 20% off with code ATLAS20, and Trade Coffee gives 15% off with TRADE15. Wandering Bear offers 20% off organic cold brew."},
    ],
}

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
    <div class="brand-codes"><strong>vdog_email</strong> — 20% OFF first order · <strong>vdog_sub</strong> — 10% OFF Subscription</div>
</div>
<div class="brand-card">
    <a href="/brand/wild%20earth" class="brand-name">🐕 Wild Earth</a>
    <div class="brand-codes"><strong>wildearth_email</strong> — 15% OFF first order · <strong>wildearth_guarantee</strong> — 30-Day Guarantee</div>
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
    <div class="brand-codes"><strong>casper_rmn</strong> — 15% OFF · <strong>casp5</strong> — 5% OFF · Email signup for best deals</div>
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
    'vegan-food-beverage-coupons': {
        'title': 'Best Vegan Food & Plant-Based Beverage Coupons 2026',
        'description': 'Save money on plant-based foods with verified coupon codes for Magic Spoon, Huel, Oatly, Califia Farms, Biena, and more vegan food brands.',
        'content': '''
<h2>Delicious Plant-Based Eating for Less</h2>
<p>Eating plant-based doesn't have to be expensive. These verified coupon codes help you save on vegan cereal, oat milk, meal replacements, healthy snacks, and more.</p>

<h2>Vegan Cereal & Snacks</h2>
<div class="brand-card">
    <a href="/brand/magic%20spoon" class="brand-name">🥣 Magic Spoon</a>
    <div class="brand-codes"><strong>magic_20</strong> — 20% OFF first order · Email signup for subscription deals</div>
</div>
<div class="brand-card">
    <a href="/brand/biena" class="brand-name">🥜 Biena</a>
    <div class="brand-codes">Email signup for 20% OFF first order, free shipping $25+</div>
</div>

<h2>Plant-Based Milk & Coffee</h2>
<div class="brand-card">
    <a href="/brand/oatly" class="brand-name">🥛 Oatly</a>
    <div class="brand-codes">Email signup for 10% OFF first order, free shipping on subscriptions</div>
</div>
<div class="brand-card">
    <a href="/brand/califia%20farms" class="brand-name">☕ Califia Farms</a>
    <div class="brand-codes">Email signup for 20% OFF sitewide, subscription savings available</div>
</div>

<h2>Meal Replacements</h2>
<div class="brand-card">
    <a href="/brand/huel" class="brand-name">🥤 Huel</a>
    <div class="brand-codes"><strong>huel_email</strong> — 10% OFF first order · <strong>huel_sub</strong> — Up to 15% OFF Subscription</div>
</div>

<h2>Why Plant-Based?</h2>
<p>Plant-based eating reduces your carbon footprint, supports animal welfare, and can improve your health. These brands make it easy and affordable with high-quality vegan products.</p>
''',
    },
    'tech-gadget-coupons': {
        'title': 'Best Eco-Friendly Tech & Gadget Coupons 2026',
        'description': 'Find verified coupon codes for sustainable tech accessories. Compostable phone cases, wireless earbuds, chargers, and smart devices from Pela, Casetify, Anker, and more.',
        'content': '''
<h2>Smart Tech, Sustainable Choices</h2>
<p>Tech accessories don't have to harm the planet. From compostable phone cases to energy-efficient chargers, these brands prove that great design and sustainability can go hand in hand.</p>

<h2>Phone Cases & Protection</h2>
<div class="brand-card">
    <a href="/brand/pela" class="brand-name">📱 Pela</a>
    <div class="brand-codes">Email signup for deals on 100% compostable phone cases</div>
</div>
<div class="brand-card">
    <a href="/brand/casetify" class="brand-name">📱 Casetify</a>
    <div class="brand-codes">Email signup for 20% OFF sitewide, eco-friendly Impact collection</div>
</div>

<h2>Chargers, Cables & Power</h2>
<div class="brand-card">
    <a href="/brand/nomad" class="brand-name">🔌 Nomad</a>
    <div class="brand-codes">Premium cables & charging, free shipping available</div>
</div>
<div class="brand-card">
    <a href="/brand/anker" class="brand-name">🔋 Anker</a>
    <div class="brand-codes">Email signup for 10% OFF first order, seasonal sales up to 20% off</div>
</div>

<h2>Audio & Wearables</h2>
<div class="brand-card">
    <a href="/brand/nothing" class="brand-name">🎧 Nothing</a>
    <div class="brand-codes">Email signup for deals on transparent-design earbuds and audio</div>
</div>

<h2>Why Sustainable Tech?</h2>
<p>The electronics industry generates over 50 million tons of e-waste annually. Choosing brands that prioritize recycled materials, compostable packaging, and repairable design helps reduce this growing problem.</p>
''',
    },
    'travel-luggage-coupons': {
        'title': 'Best Travel & Luggage Coupon Codes 2026',
        'description': 'Save on premium luggage with verified coupon codes for Away, Monos, Paravel, Roam, and more sustainable travel brands.',
        'content': '''
<h2>Travel in Style, Save Big</h2>
<p>Quality luggage is an investment. Use these verified coupon codes to save on premium, sustainable luggage.</p>

<h2>Premium Luggage</h2>
<div class="brand-card">
    <a href="/brand/away" class="brand-name">🧳 Away</a>
    <div class="brand-codes">Email signup for 20% OFF first order, bundle savings on sets</div>
</div>
<div class="brand-card">
    <a href="/brand/monos" class="brand-name">🧳 Monos</a>
    <div class="brand-codes">Email signup for 15% OFF first order, free shipping included</div>
</div>

<h2>Sustainable & Eco-Friendly Travel</h2>
<div class="brand-card">
    <a href="/brand/paravel" class="brand-name">🌿 Paravel</a>
    <div class="brand-codes">Email signup for 20% OFF sitewide, free shipping included</div>
</div>
<div class="brand-card">
    <a href="/brand/roam" class="brand-name">🎨 Roam</a>
    <div class="brand-codes">Customizable, premium luggage, free shipping available</div>
</div>

<h2>Why Invest in Good Luggage?</h2>
<p>Quality luggage lasts longer, reduces waste, and makes travel more enjoyable.</p>
''',
    },
    'baby-kids-coupons': {
        'title': "Best Baby & Kids Coupons 2026 — Honest Company, Burt's Bees Baby & More",
        'description': "Find verified coupon codes for baby essentials. Vegan diapers, organic baby clothes, plant-based baby food from Honest Company, Burt's Bees Baby, Once Upon a Farm, and more.",
        'content': '''
<h2>Eco-Friendly Baby Essentials for Less</h2>
<p>Raising little ones is expensive. Save on safe, vegan, and organic baby products with these verified coupon codes.</p>

<h2>Diapers & Baby Care</h2>
<div class="brand-card">
    <a href="/brand/honest%20company" class="brand-name">🍼 Honest Company</a>
    <div class="brand-codes">Email signup for 20% OFF first order, subscription savings available</div>
</div>

<h2>Baby Clothes & Gear</h2>
<div class="brand-card">
    <a href="/brand/burts%20bees%20baby" class="brand-name">👶 Burt's Bees Baby</a>
    <div class="brand-codes">Email signup for 20% OFF first order, free shipping included</div>
</div>
<div class="brand-card">
    <a href="/brand/lalo" class="brand-name">🪑 Lalo</a>
    <div class="brand-codes">Modern eco-friendly baby gear, free shipping available</div>
</div>

<h2>Baby Food & Snacks</h2>
<div class="brand-card">
    <a href="/brand/once%20upon%20a%20farm" class="brand-name">🥬 Once Upon a Farm</a>
    <div class="brand-codes">Email signup for 20% OFF first order, subscription savings available</div>
</div>
<div class="brand-card">
    <a href="/brand/happy%20family" class="brand-name">👶 Happy Family</a>
    <div class="brand-codes">Organic baby food, free shipping available</div>
</div>

<h2>Why Choose Clean Baby Brands?</h2>
<p>Babies have sensitive skin and developing immune systems. Choosing organic, vegan, and chemical-free products gives you peace of mind.</p>
''',
    },
    'intimates-loungewear-coupons': {
        'title': "Best Intimates & Loungewear Coupons 2026 — ThirdLove, CUUP, Parade & More",
        'description': 'Save on premium bras, underwear, and loungewear with verified coupon codes for ThirdLove, CUUP, Parade, MeUndies, Lively, and more.',
        'content': '''
<h2>Comfort Meets Style for Less</h2>
<p>Premium intimates shouldn't break the bank. These DTC brands offer better fits, sustainable materials, and inclusive sizing.</p>

<h2>Bras & Underwear</h2>
<div class="brand-card">
    <a href="/brand/thirdlove" class="brand-name">👙 ThirdLove</a>
    <div class="brand-codes"><strong>THIRD20</strong> — 20% off · Half-cup sizes for perfect fit</div>
</div>
<div class="brand-card">
    <a href="/brand/cuup" class="brand-name">👙 CUUP</a>
    <div class="brand-codes"><strong>CUUP15</strong> — 15% off · Vegan, minimalist bras</div>
</div>
<div class="brand-card">
    <a href="/brand/parade" class="brand-name">🩲 Parade</a>
    <div class="brand-codes"><strong>PARADE20</strong> — 20% off · Recycled materials, inclusive sizing</div>
</div>

<h2>Everyday Essentials</h2>
<div class="brand-card">
    <a href="/brand/meundies" class="brand-name">🧦 MeUndies</a>
    <div class="brand-codes"><strong>MEUNDIES20</strong> — 20% off · Ultra-soft fabric, fun patterns</div>
</div>
<div class="brand-card">
    <a href="/brand/lively" class="brand-name">💃 Lively</a>
    <div class="brand-codes"><strong>LIVELY20</strong> — 20% off · Wire-free comfort, all-day wear</div>
</div>

<h2>Why DTC Intimates?</h2>
<p>DTC intimates brands offer better quality, inclusive sizing (XS-6X), and sustainable materials at lower prices than traditional retailers.</p>
''',
    },
    'candles-home-fragrance-coupons': {
        'title': "Best Candle & Home Fragrance Coupons 2026 — Boy Smells, Otherland & More",
        'description': 'Discover verified coupon codes for artisanal candles and home fragrances. Vegan soy candles, unique scents from Boy Smells, Otherland, P.F. Candle Co, Homesick, and Snif.',
        'content': '''
<h2>Set the Mood for Less</h2>
<p>Artisanal candles transform your space. These DTC fragrance brands offer unique scents using clean, vegan ingredients.</p>

<h2>Artisanal Candles</h2>
<div class="brand-card">
    <a href="/brand/boy%20smells" class="brand-name">🕯️ Boy Smells</a>
    <div class="brand-codes"><strong>BOY15</strong> — 15% off · Vegan coconut wax, gender-neutral scents</div>
</div>
<div class="brand-card">
    <a href="/brand/otherland" class="brand-name">🎨 Otherland</a>
    <div class="brand-codes"><strong>OTHER20</strong> — 20% off · Art-inspired fragrances</div>
</div>
<div class="brand-card">
    <a href="/brand/pf%20candle%20co" class="brand-name">🕯️ P.F. Candle Co</a>
    <div class="brand-codes"><strong>PFC20</strong> — 20% off · Soy wax, cotton wicks</div>
</div>

<h2>Fragrance & Home Scents</h2>
<div class="brand-card">
    <a href="/brand/homesick" class="brand-name">🏠 Homesick</a>
    <div class="brand-codes"><strong>HOMESICK20</strong> — 20% off · Place-inspired candles</div>
</div>
<div class="brand-card">
    <a href="/brand/snif" class="brand-name">🌸 Snif</a>
    <div class="brand-codes"><strong>SNIF15</strong> — 15% off · Vegan fragrances</div>
</div>

<h2>Why Choose Clean Fragrance?</h2>
<p>Many mass-market candles use paraffin wax and synthetic fragrances. These brands use natural soy wax, essential oils, and phthalate-free fragrances for a cleaner burn.</p>
''',
    },
    'coffee-tea-subscription-coupons': {
        'title': 'Best Coffee & Tea Subscription Coupons 2026',
        'description': 'Find verified coupon codes for coffee and tea subscriptions. Save on specialty coffee, single-origin roasts, premium loose leaf tea, and cold brew from top DTC brands.',
        'content': '''
<h2>Your Daily Brew for Less</h2>
<p>Great coffee and tea don't have to be expensive. These subscription services deliver premium beans and leaves straight to your door.</p>

<h2>Coffee Subscriptions</h2>
<div class="brand-card">
    <a href="/brand/trade%20coffee" class="brand-name">☕ Trade Coffee</a>
    <div class="brand-codes"><strong>TRADE15</strong> — 15% off · Personalized roaster matching</div>
</div>
<div class="brand-card">
    <a href="/brand/atlas%20coffee%20club" class="brand-name">🌍 Atlas Coffee Club</a>
    <div class="brand-codes"><strong>ATLAS20</strong> — 20% off · World coffee tour at home</div>
</div>

<h2>Cold Brew</h2>
<div class="brand-card">
    <a href="/brand/wandering%20bear" class="brand-name">🐻 Wandering Bear</a>
    <div class="brand-codes"><strong>Bemail signup</strong> — 20% off · Organic cold brew, shelf-stable</div>
</div>

<h2>Premium Tea</h2>
<div class="brand-card">
    <a href="/brand/art%20of%20tea" class="brand-name">🍵 Art of Tea</a>
    <div class="brand-codes"><strong>TEAB15</strong> — 15% off · Organic loose leaf tea</div>
</div>

<h2>Why Subscribe?</h2>
<p>Coffee and tea subscriptions ensure you never run out of your favorite brew. Most services offer flexible scheduling and free shipping.</p>
''',
    },
    'burrow-vs-article-furniture': {
        'title': 'Burrow vs Article: Which DTC Furniture Brand Has Better Coupons?',
        'description': 'Compare Burrow and Article furniture: pricing, coupons, quality, shipping, and return policies. Find out which DTC furniture brand is right for you.',
        'content': '''
<h2>Burrow vs Article: Head-to-Head Comparison</h2>
<p>Burrow and Article are two of the most popular DTC furniture brands. Both offer modern, high-quality pieces without the retail markup. But which one saves you more? We compare their coupon codes, pricing, and policies.</p>

<h2>Coupon Comparison</h2>
<div class="brand-card">
    <a href="/brand/burrow" class="brand-name">🛋️ Burrow</a>
    <div class="brand-codes"><strong>SAVE20</strong> — 20% off sitewide · <strong>WELCOME10</strong> — 10% off new customers · Free shipping $500+</div>
</div>
<div class="brand-card">
    <a href="/brand/article" class="brand-name">🛋️ Article</a>
    <div class="brand-codes"><strong>WELCOME15</strong> — 15% off first order · <strong>FREESHIP</strong> — Free shipping</div>
</div>

<h2>Which Is Better?</h2>
<table style="width:100%;border-collapse:collapse;">
<tr style="background:#f5f5f7;"><th style="padding:8px;text-align:left;">Feature</th><th style="padding:8px;text-align:left;">Burrow</th><th style="padding:8px;text-align:left;">Article</th></tr>
<tr><td style="padding:8px;border-top:1px solid #eee;">Best Coupon</td><td style="padding:8px;border-top:1px solid #eee;">20% off sitewide</td><td style="padding:8px;border-top:1px solid #eee;">15% off first order</td></tr>
<tr><td style="padding:8px;border-top:1px solid #eee;">Free Shipping</td><td style="padding:8px;border-top:1px solid #eee;">Orders $500+</td><td style="padding:8px;border-top:1px solid #eee;">Always free</td></tr>
<tr><td style="padding:8px;border-top:1px solid #eee;">Return Policy</td><td style="padding:8px;border-top:1px solid #eee;">30 days</td><td style="padding:8px;border-top:1px solid #eee;">30 days</td></tr>
<tr><td style="padding:8px;border-top:1px solid #eee;">Warranty</td><td style="padding:8px;border-top:1px solid #eee;">1 year</td><td style="padding:8px;border-top:1px solid #eee;">1 year</td></tr>
<tr><td style="padding:8px;border-top:1px solid #eee;">Price Range</td><td style="padding:8px;border-top:1px solid #eee;">$$-$$$</td><td style="padding:8px;border-top:1px solid #eee;">$$-$$$$</td></tr>
</table>

<h2>Verdict</h2>
<p><strong>Choose Burrow</strong> if you want the biggest instant discount (20% off) and modern modular furniture. <strong>Choose Article</strong> for consistently free shipping and a wider selection of premium pieces. Remember you can use our coupons on both to maximize savings.</p>
''',
    },
    'best-time-to-buy-furniture': {
        'title': 'When Is the Best Time to Buy Furniture? Seasonal Sales Calendar 2026',
        'description': 'The ultimate furniture shopping calendar. Know exactly when to buy sofas, mattresses, bedding, and home decor for the biggest discounts.',
        'content': '''
<h2>Furniture Sales Calendar: Never Pay Full Price</h2>
<p>Furniture is one of the most discounted categories in online retail — if you buy at the right time. Here's when every major DTC furniture brand runs its best sales.</p>

<h2>Biggest Furniture Sales of the Year</h2>
<div class="brand-card"><strong>🎆 Memorial Day (Late May)</strong> — Burrow 20% off, Article 15% off sitewide, mattress brands offer $100-200 off</div>
<div class="brand-card"><strong>🦃 Labor Day (Early September)</strong> — Up to 25% off sitewide at Burrow, mattress sales peak. Best time for sofas and sectionals.</div>
<div class="brand-card"><strong>🛍️ Black Friday / Cyber Monday (Late November)</strong> — Deepest discounts of the year. Burrow up to 30% off, mattress bundles with free pillows and sheets.</div>
<div class="brand-card"><strong>🎄 Presidents Day (February)</strong> — Comparable to Labor Day. Good for bedroom furniture and mattresses.</div>

<h2>Best Time to Buy by Category</h2>
<table style="width:100%;border-collapse:collapse;">
<tr style="background:#f5f5f7;"><th style="padding:8px;text-align:left;">Category</th><th style="padding:8px;text-align:left;">Best Time</th><th style="padding:8px;text-align:left;">Typical Discount</th></tr>
<tr><td style="padding:8px;border-top:1px solid #eee;">Sofas & Sectionals</td><td style="padding:8px;border-top:1px solid #eee;">Labor Day, Black Friday</td><td style="padding:8px;border-top:1px solid #eee;">20-30% off</td></tr>
<tr><td style="padding:8px;border-top:1px solid #eee;">Mattresses</td><td style="padding:8px;border-top:1px solid #eee;">Presidents Day, Memorial Day</td><td style="padding:8px;border-top:1px solid #eee;">$100-300 off + free accessories</td></tr>
<tr><td style="padding:8px;border-top:1px solid #eee;">Bedding & Linens</td><td style="padding:8px;border-top:1px solid #eee;">White Sales (January), Black Friday</td><td style="padding:8px;border-top:1px solid #eee;">15-40% off</td></tr>
<tr><td style="padding:8px;border-top:1px solid #eee;">Outdoor Furniture</td><td style="padding:8px;border-top:1px solid #eee;">End of Summer (August-September)</td><td style="padding:8px;border-top:1px solid #eee;">30-50% off clearance</td></tr>
</table>

<h2>Pro Tips</h2>
<p>📧 Always sign up for email before buying — most brands offer 10-20% off your first order. Stack email signup discount with sale prices when store policy allows.</p>
<p>🛒 Create an account and add items to your cart. Some brands send a discount code within 24 hours if you leave items in your cart.</p>
<p>📦 Bundle items to hit free shipping thresholds. Adding a small accessory can save you $15-50 in shipping costs.</p>
''',
    },
    'dtc-mattress-guide': {
        'title': 'Best DTC Mattress Deals 2026: Casper, Avocado, Eight Sleep & More',
        'description': 'Compare mattress coupons and discounts from top DTC brands. Save $100-300 on premium mattresses with verified coupon codes.',
        'content': '''
<h2>Your Perfect Mattress at the Best Price</h2>
<p>DTC mattress brands cut out the middleman, offering premium quality at better prices. We've compared the top brands so you can find the best deal on your next mattress.</p>

<h2>Mattress Brand Coupon Comparison</h2>
<div class="brand-card">
    <a href="/brand/casper" class="brand-name">🛏️ Casper</a>
    <div class="brand-codes"><strong>email signup</strong> — 15% off sitewide · <strong>mattress discount</strong> — $100 off mattress · 100-night trial</div>
</div>
<div class="brand-card">
    <a href="/brand/avocado" class="brand-name">🌿 Avocado</a>
    <div class="brand-codes"><strong>AVO100</strong> — $100 off mattress · Organic, non-toxic materials · 1-year trial</div>
</div>
<div class="brand-card">
    <a href="/brand/eightsleep" class="brand-name">🌡️ Eight Sleep</a>
    <div class="brand-codes"><strong>EIGHT10</strong> — 10% off first order · Smart temperature control · 30-night trial</div>
</div>

<h2>Which Mattress Is Right for You?</h2>
<table style="width:100%;border-collapse:collapse;">
<tr style="background:#f5f5f7;"><th style="padding:8px;text-align:left;">Brand</th><th style="padding:8px;text-align:left;">Best For</th><th style="padding:8px;text-align:left;">Trial</th><th style="padding:8px;text-align:left;">Warranty</th></tr>
<tr><td style="padding:8px;border-top:1px solid #eee;">Casper</td><td style="padding:8px;border-top:1px solid #eee;">All-around comfort, great value</td><td style="padding:8px;border-top:1px solid #eee;">100 nights</td><td style="padding:8px;border-top:1px solid #eee;">10 years</td></tr>
<tr><td style="padding:8px;border-top:1px solid #eee;">Avocado</td><td style="padding:8px;border-top:1px solid #eee;">Eco-conscious, organic materials</td><td style="padding:8px;border-top:1px solid #eee;">1 year</td><td style="padding:8px;border-top:1px solid #eee;">25 years</td></tr>
<tr><td style="padding:8px;border-top:1px solid #eee;">Eight Sleep</td><td style="padding:8px;border-top:1px solid #eee;">Temperature regulation, smart features</td><td style="padding:8px;border-top:1px solid #eee;">30 nights</td><td style="padding:8px;border-top:1px solid #eee;">10 years</td></tr>
</table>

<h2>How to Save on a DTC Mattress</h2>
<p>💰 Most brands offer $100-200 off during major sales (Presidents Day, Memorial Day, Black Friday).</p>
<p>📧 Email signup typically gives 10-15% off (check brand pages for current codes).</p>
<p>🎁 Bundle deals (mattress + pillows + sheets) can save 20-30% vs buying separately.</p>
''',
    },
    'pet-supplies-savings-guide': {
        'title': 'Smart Ways to Save on Pet Supplies: Verified Coupons & Tips',
        'description': 'Save money on pet food, accessories, and supplies with verified coupon codes for top pet brands. From dog cameras to litter robots, find the best deals.',
        'content': '''
<h2>Pet Parenting for Less</h2>
<p>Our furry friends deserve the best, but pet supplies can add up fast. Here's how to save on everything from dog food to smart pet gadgets using verified coupon codes.</p>

<h2>Top Pet Brand Coupons</h2>
<div class="brand-card">
    <a href="/brand/v-dog" class="brand-name">🐕 V-Dog</a>
    <div class="brand-codes"><strong>email signup</strong> — 20% off first order · <strong>subscription discount</strong> — 10% off repeat · 100% plant-based dog food</div>
</div>
<div class="brand-card">
    <a href="/brand/wild%20earth" class="brand-name">🐕 Wild Earth</a>
    <div class="brand-codes"><strong>email signup</strong> — 15% off first order · <strong>satisfaction guarantee</strong> — 30-day guarantee · Koji protein dog food</div>
</div>
<div class="brand-card">
    <a href="/brand/furbo" class="brand-name">📹 Furbo Dog Camera</a>
    <div class="brand-codes"><strong>FURBO20</strong> — 20% off · Treat-tossing camera with bark alert</div>
</div>
<div class="brand-card">
    <a href="/brand/litterrobot" class="brand-name">🤖 Litter-Robot</a>
    <div class="brand-codes"><strong>LITTER10</strong> — $50 off · Self-cleaning litter box · 90-day trial</div>
</div>

<h2>Money-Saving Tips for Pet Parents</h2>
<p>🔄 Subscribe & save: Most pet food brands offer 10-20% off recurring orders — set up autoship for the best price.</p>
<p>📧 Email signup: Always sign up before buying. New customer discounts are typically 15-20% off.</p>
<p>📦 Stock up during sales: Memorial Day, Prime Day, and Black Friday are the best times to buy pet supplies.</p>
<p>🏷️ Referral programs: Many pet brands give $20-50 credit for referring friends.</p>
''',
    },
    'eco-cleaning-guide': {
        'title': 'Complete Guide to Eco-Friendly & Plastic-Free Cleaning Coupons',
        'description': 'Save money on eco-friendly cleaning products. Verified coupon codes for Blueland, Who Gives A Crap, Public Goods, and Grove Collaborative.',
        'content': '''
<h2>Clean Home, Clean Planet</h2>
<p>Switching to eco-friendly cleaning products reduces plastic waste and chemical exposure. These verified coupon codes make sustainable cleaning affordable.</p>

<h2>Best Eco Cleaning Coupons</h2>
<div class="brand-card">
    <a href="/brand/blueland" class="brand-name">🧹 Blueland</a>
    <div class="brand-codes"><strong>BLUELAND15</strong> — 15% off · Tablet concentrates, forever bottles — no plastic waste</div>
</div>
<div class="brand-card">
    <a href="/brand/whogivesacrap" class="brand-name">🧻 Who Gives A Crap</a>
    <div class="brand-codes"><strong>WGAC20</strong> — 20% off first order · 100% bamboo toilet paper · 50% of profits to sanitation</div>
</div>
<div class="brand-card">
    <a href="/brand/publicgoods" class="brand-name">🏠 Public Goods</a>
    <div class="brand-codes"><strong>PUBLIC10</strong> — 10% off · Sustainable home & personal care essentials</div>
</div>

<h2>Why Switch to Eco Cleaning?</h2>
<p>🌱 <strong>Less plastic:</strong> Over 8 million tons of plastic enter oceans annually. Brands like Blueland use tablet concentrates with reusable bottles.</p>
<p>🧪 <strong>Fewer chemicals:</strong> Eco-friendly cleaners use plant-based ingredients instead of harsh chemicals like bleach and ammonia.</p>
<p>💰 <strong>Cost savings:</strong> Refills cost less than buying new bottles each time. Subscriptions save an additional 10-20%.</p>

<h2>Tips for Going Plastic-Free</h2>
<p>Start with one swap at a time — dish soap tablets, bamboo toilet paper, or all-purpose cleaner. Most brands offer subscription discounts that make eco-friendly products cheaper than conventional ones long-term.</p>
''',
    },
    'vegan-protein-snacks-coupons': {
        'title': 'Best Vegan Protein & Snack Coupons 2026: Plant-Based Fuel for Less',
        'description': 'Save on plant-based protein and snacks with verified coupon codes for Huel, Magic Spoon, No Cow, Biena, and more vegan food brands.',
        'content': '''
<h2>Plant-Powered Nutrition at the Best Price</h2>
<p>Whether you're vegan, flexitarian, or just looking for healthier snack options, these coupon codes help you save on plant-based protein, cereal, and snacks.</p>

<h2>Vegan Meal Replacements & Protein</h2>
<div class="brand-card">
    <a href="/brand/huel" class="brand-name">🥤 Huel</a>
    <div class="brand-codes"><strong>email signup</strong> — 10% off first order · <strong>free shipping</strong> — Free starter pack · All-in-one nutrition</div>
</div>
<div class="brand-card">
    <a href="/brand/no%20cow" class="brand-name">💪 No Cow</a>
    <div class="brand-codes"><strong>NOCOW20</strong> — 20% off first order · 21g plant protein bars · Dairy-free, soy-free</div>
</div>

<h2>Vegan Cereal & Crunchy Snacks</h2>
<div class="brand-card">
    <a href="/brand/magic%20spoon" class="brand-name">🥣 Magic Spoon</a>
    <div class="brand-codes"><strong>email signup</strong> — 20% off first order · <strong>subscription discount</strong> — 10% off subscription · Keto & paleo friendly</div>
</div>
<div class="brand-card">
    <a href="/brand/biena" class="brand-name">🥜 Biena</a>
    <div class="brand-codes"><strong>email signup</strong> — 20% off first order · <strong>free shipping</strong> — Free shipping $25+ · Chickpea-based snacks</div>
</div>

<h2>Why Choose Plant-Based Snacks?</h2>
<p>Plant-based snacks are better for your health and the planet. They typically have less saturated fat, more fiber, and a lower carbon footprint than animal-based alternatives. Plus, these brands make them delicious enough that you won't miss the old stuff.</p>
''',
    },
    'social-impact-guide': {
        'title': 'Best Social Impact Brands 2026: TOMS, Bombas, Allbirds & More',
        'description': 'Discover brands that give back. Verified coupon codes for TOMS, Bombas, Allbirds, Cotopaxi — every purchase supports a cause.',
        'content': '''
<h2>Shop with Purpose</h2>
<p>These brands prove that great products and social impact can go hand in hand. Every purchase supports a meaningful cause — from planting trees to donating shoes.</p>

<h2>Give-Back Shoe Brands</h2>
<div class="brand-card">
    <a href="/brand/toms" class="brand-name">👟 TOMS</a>
    <div class="brand-codes"><strong>TOMS20</strong> — 20% off first order · One for One: every purchase supports access to education</div>
</div>
<div class="brand-card">
    <a href="/brand/allbirds" class="brand-name">🐑 Allbirds</a>
    <div class="brand-codes"><strong>ALLBIRDS25</strong> — $25 off referral · Carbon neutral wool & tree fiber shoes</div>
</div>

<h2>Clothing & Accessories That Give Back</h2>
<div class="brand-card">
    <a href="/brand/bombas" class="brand-name">🧦 Bombas</a>
    <div class="brand-codes"><strong>BOMBAS20</strong> — 20% off first order · One purchased = one donated to homeless shelters</div>
</div>
<div class="brand-card">
    <a href="/brand/cotopaxi" class="brand-name">🏔️ Cotopaxi</a>
    <div class="brand-codes"><strong>COTOPAXI10</strong> — 10% off first order · Outdoor gear that funds poverty alleviation</div>
</div>
<div class="brand-card">
    <a href="/brand/united%20by%20blue" class="brand-name">🌊 United By Blue</a>
    <div class="brand-codes"><strong>UBB15</strong> — 15% off first order · Every order removes 1lb of trash from oceans</div>
</div>

<h2>Why Shop Give-Back Brands?</h2>
<p>Every dollar you spend with these brands creates positive impact beyond the product. From fighting homelessness to cleaning our oceans, your purchase makes a difference.</p>
''',
    },
    'vegan-food-savings': {
        'title': 'Best Vegan Food & Plant-Based Protein Coupons 2026',
        'description': 'Save on plant-based protein, meal replacements, and vegan snacks. Verified coupon codes for Orgain, Miyoko Creamery, Ripple Foods, and Thrive Market.',
        'content': '''
<h2>Plant-Based Nutrition for Less</h2>
<p>Eating plant-based doesn't have to break the bank. These verified coupon codes help you save on protein powders, plant milk, cheese alternatives, and more.</p>

<h2>Vegan Protein & Supplements</h2>
<div class="brand-card">
    <a href="/brand/orgain" class="brand-name">💪 Orgain</a>
    <div class="brand-codes"><strong>ORGAIN20</strong> — 20% off first order · Plant-based protein powders & shakes</div>
</div>

<h2>Plant-Based Dairy Alternatives</h2>
<div class="brand-card">
    <a href="/brand/miyokos%20creamery" class="brand-name">🧀 Miyoko's Creamery</a>
    <div class="brand-codes"><strong>MIYOKO15</strong> — 15% off first order · Artisan vegan cheese & butter</div>
</div>
<div class="brand-card">
    <a href="/brand/ripple%20foods" class="brand-name">🥛 Ripple Foods</a>
    <div class="brand-codes"><strong>RIPPLE10</strong> — 10% off first order · Pea protein milk, better for the planet</div>
</div>

<h2>Eco-Friendly Grocery</h2>
<div class="brand-card">
    <a href="/brand/thrive%20market" class="brand-name">🛒 Thrive Market</a>
    <div class="brand-codes"><strong>THRIVE20</strong> — 20% off first order · Organic & non-GMO essentials</div>
</div>
''',
    },
    'fitness-wearables-comparison': {
        'title': 'Whoop vs Oura vs Eight Sleep: Best Fitness Tracker Deals 2026',
        'description': 'Compare Whoop, Oura Ring, and Eight Sleep — which fitness wearable saves you most? Verified coupon codes and pricing comparison.',
        'content': '''
<h2>Fitness Wearables: Head-to-Head</h2>
<p>Fitness wearables have evolved far beyond step counting. We compare three top brands — Whoop, Oura, and Eight Sleep — to help you find the best deal.</p>

<h2>Brand Comparison</h2>
<table style="width:100%;border-collapse:collapse;">
<tr style="background:#f5f5f7;"><th style="padding:8px;text-align:left;">Feature</th><th style="padding:8px;text-align:left;">Whoop</th><th style="padding:8px;text-align:left;">Oura Ring</th><th style="padding:8px;text-align:left;">Eight Sleep</th></tr>
<tr><td style="padding:8px;border-top:1px solid #eee;">Best Coupon</td><td style="padding:8px;border-top:1px solid #eee;">1st month free</td><td style="padding:8px;border-top:1px solid #eee;">$20 off ring</td><td style="padding:8px;border-top:1px solid #eee;">10% off first order</td></tr>
<tr><td style="padding:8px;border-top:1px solid #eee;">Focus</td><td style="padding:8px;border-top:1px solid #eee;">Recovery & strain</td><td style="padding:8px;border-top:1px solid #eee;">Sleep tracking</td><td style="padding:8px;border-top:1px solid #eee;">Sleep temperature</td></tr>
<tr><td style="padding:8px;border-top:1px solid #eee;">Hardware Cost</td><td style="padding:8px;border-top:1px solid #eee;">Free (subscription)</td><td style="padding:8px;border-top:1px solid #eee;">$299+</td><td style="padding:8px;border-top:1px solid #eee;">$1,895+</td></tr>
<tr><td style="padding:8px;border-top:1px solid #eee;">Subscription</td><td style="padding:8px;border-top:1px solid #eee;">$30/month</td><td style="padding:8px;border-top:1px solid #eee;">$5.99/month</td><td style="padding:8px;border-top:1px solid #eee;">None</td></tr>
</table>

<h2>Which Is Best for You?</h2>
<p><strong>Choose Whoop</strong> for hardcore fitness and recovery tracking. <strong>Choose Oura</strong> for sleek sleep tracking you can wear 24/7. <strong>Choose Eight Sleep</strong> for smart temperature-controlled sleep — the ultimate luxury upgrade.</p>
<p>💰 Use our coupon codes above to save on all three.</p>
''',
    },
    'cleaning-products-comparison': {
        'title': 'Blueland vs Dropps vs Grove: Best Eco-Friendly Cleaning Products Compared',
        'description': 'Compare eco-friendly cleaning brands. Plastic-free tablets, laundry pods, and sustainable home essentials with verified coupon codes.',
        'content': '''
<h2>Clean Green, Save Green</h2>
<p>Plastic-free cleaning is better for your home and the planet. We compare three leading eco-friendly cleaning brands to help you choose.</p>

<h2>Brand Comparison</h2>
<div class="brand-card">
    <a href="/brand/blueland" class="brand-name">🧹 Blueland</a>
    <div class="brand-codes"><strong>BLUELAND15</strong> — 15% off forever bottles · Tablet concentrates, zero plastic waste</div>
</div>
<div class="brand-card">
    <a href="/brand/dropps" class="brand-name">🧺 Dropps</a>
    <div class="brand-codes"><strong>DROPS15</strong> — 15% off first order · Concentrated laundry & dishwasher pods</div>
</div>
<div class="brand-card">
    <a href="/brand/grove%20collaborative" class="brand-name">🌿 Grove Collaborative</a>
    <div class="brand-codes"><strong>GROVE20</strong> — 20% off first order · Curated sustainable home essentials</div>
</div>

<h2>Which One Is Right for You?</h2>
<p><strong>Blueland</strong> is best for all-purpose cleaners — their tablet system means you keep the bottles forever. <strong>Dropps</strong> is perfect for laundry and dishwasher pods, delivered on subscription. <strong>Grove Collaborative</strong> is a full home store with hundreds of eco-friendly brands.</p>
<p>Start with one swap — all three are better for the environment than conventional cleaners.</p>
''',
    },
    'coffee-subscription-comparison': {
        'title': 'Best Coffee Subscription: Trade vs Atlas vs Wandering Bear Compared',
        'description': 'Compare top coffee subscriptions. Personalized roasting, world coffee tours, and organic cold brew. Find the best deal for your morning cup.',
        'content': '''
<h2>Your Perfect Cup, Delivered</h2>
<p>Coffee subscriptions make mornings better. We compare three popular DTC coffee brands to help you find your perfect brew.</p>

<h2>Coffee Brand Comparison</h2>
<div class="brand-card">
    <a href="/brand/trade%20coffee" class="brand-name">☕ Trade Coffee</a>
    <div class="brand-codes"><strong>TRADE15</strong> — 15% off first order · Personalized matching from 500+ roasters</div>
</div>
<div class="brand-card">
    <a href="/brand/atlas%20coffee%20club" class="brand-name">🌍 Atlas Coffee Club</a>
    <div class="brand-codes"><strong>ATLAS20</strong> — 20% off first order · World coffee tour delivered monthly</div>
</div>
<div class="brand-card">
    <a href="/brand/wandering%20bear" class="brand-name">🐻 Wandering Bear</a>
    <div class="brand-codes"><strong>Bemail signup</strong> — 20% off first order · Organic cold brew, shelf-stable</div>
</div>

<h2>Which Subscription Is Best?</h2>
<p><strong>Trade Coffee</strong> is perfect if you love exploring — they match you with the best roasters for your taste. <strong>Atlas Coffee Club</strong> takes you on a world tour with single-origin beans from different countries each month. <strong>Wandering Bear</strong> is for cold brew lovers — organic, strong, and ready to drink.</p>
''',
    },
    'baby-gear-guide': {
        'title': 'Ultimate Baby Registry & Baby Gear Discount Guide 2026',
        'description': 'Save on baby essentials with verified coupon codes. Diapers, baby clothes, baby food, and gear from Honest Company, Burt Bees Baby, and more.',
        'content': '''
<h2>Welcome to Parenthood — Save on Everything</h2>
<p>Babies are expensive. From diapers to baby food, these verified coupon codes help you save on the essentials.</p>

<h2>Diapers & Baby Care</h2>
<div class="brand-card">
    <a href="/brand/honest%20company" class="brand-name">🍼 Honest Company</a>
    <div class="brand-codes"><strong>email signup</strong> — 20% off first order · Plant-based diapers, nontoxic wipes</div>
</div>

<h2>Baby Clothes & Gear</h2>
<div class="brand-card">
    <a href="/brand/burts%20bees%20baby" class="brand-name">👶 Burt's Bees Baby</a>
    <div class="brand-codes"><strong>email signup</strong> — 20% off · Organic cotton baby clothes</div>
</div>
<div class="brand-card">
    <a href="/brand/lalo" class="brand-name">🪑 Lalo</a>
    <div class="brand-codes">Modern eco-friendly baby gear, free shipping available</div>
</div>

<h2>Baby Food & Nutrition</h2>
<div class="brand-card">
    <a href="/brand/once%20upon%20a%20farm" class="brand-name">🥬 Once Upon a Farm</a>
    <div class="brand-codes"><strong>email signup</strong> — 20% off first order · Cold-pressed organic baby food</div>
</div>

<h2>Money-Saving Tips for New Parents</h2>
<p>📧 Sign up for email lists before buying — new parent discounts are 15-20% off first orders.</p>
<p>🔄 Set up Subscribe & Save for diapers and wipes to save 10-20% recurring.</p>
<p>📋 Create a baby registry for completion discounts (typically 10-15% off unpurchased items).</p>
''',
    },
    'candle-guide': {
        'title': 'Best Vegan Candle Brands: Boy Smells, Otherland, P.F. Candle Co & More',
        'description': 'Discover the best vegan, soy wax candles from top DTC brands. Verified coupon codes for Boy Smells, Otherland, P.F. Candle Co, Homesick, and Snif.',
        'content': '''
<h2>Set the Mood, Naturally</h2>
<p>Mass-market candles often use paraffin wax and synthetic fragrances. These DTC brands use clean, vegan ingredients for a better burn.</p>

<h2>Best Vegan Candle Brands</h2>
<div class="brand-card">
    <a href="/brand/boy%20smells" class="brand-name">🕯️ Boy Smells</a>
    <div class="brand-codes"><strong>BOY15</strong> — 15% off · Coconut wax, gender-neutral scents · BEST SELLER: Hinoki Fantome</div>
</div>
<div class="brand-card">
    <a href="/brand/otherland" class="brand-name">🎨 Otherland</a>
    <div class="brand-codes"><strong>OTHER20</strong> — 20% off · Art-inspired fragrances, soy wax blend</div>
</div>
<div class="brand-card">
    <a href="/brand/pf%20candle%20co" class="brand-name">🕯️ P.F. Candle Co</a>
    <div class="brand-codes"><strong>PFC20</strong> — 20% off · Soy wax, cotton wicks, apothecary jars</div>
</div>
<div class="brand-card">
    <a href="/brand/homesick" class="brand-name">🏠 Homesick</a>
    <div class="brand-codes"><strong>HOMESICK20</strong> — 20% off · Place-inspired scents · BEST GIFT: Subscription box</div>
</div>
<div class="brand-card">
    <a href="/brand/snif" class="brand-name">🌸 Snif</a>
    <div class="brand-codes"><strong>SNIF15</strong> — 15% off · Vegan, phthalate-free fragrances</div>
</div>

<h2>Why Choose Vegan Candles?</h2>
<p>Vegan candles use plant-based waxes (coconut, soy) instead of paraffin (petroleum byproduct). They burn cleaner, last longer, and don't release harmful chemicals into your home.</p>
''',
    },
    'travel-bags-comparison': {
        'title': 'Away vs Monos vs Paravel: Best Sustainable Luggage Compared',
        'description': 'Compare premium luggage brands. Away, Monos, and Paravel — verified coupon codes, warranty comparison, and which brand saves you most.',
        'content': '''
<h2>Premium Luggage, Better Prices</h2>
<p>DTC luggage brands offer premium quality at a fraction of traditional retail prices. We compare the top three sustainable luggage brands.</p>

<h2>Luggage Brand Comparison</h2>
<table style="width:100%;border-collapse:collapse;">
<tr style="background:#f5f5f7;"><th style="padding:8px;text-align:left;">Feature</th><th style="padding:8px;text-align:left;">Away</th><th style="padding:8px;text-align:left;">Monos</th><th style="padding:8px;text-align:left;">Paravel</th></tr>
<tr><td style="padding:8px;border-top:1px solid #eee;">Best Coupon</td><td style="padding:8px;border-top:1px solid #eee;">20% off first order</td><td style="padding:8px;border-top:1px solid #eee;">15% off first order</td><td style="padding:8px;border-top:1px solid #eee;">20% off sitewide</td></tr>
<tr><td style="padding:8px;border-top:1px solid #eee;">Eco Materials</td><td style="padding:8px;border-top:1px solid #eee;">Recycled polycarbonate</td><td style="padding:8px;border-top:1px solid #eee;">Recycled materials</td><td style="padding:8px;border-top:1px solid #eee;">Recycled & vegan</td></tr>
<tr><td style="padding:8px;border-top:1px solid #eee;">Warranty</td><td style="padding:8px;border-top:1px solid #eee;">Limited lifetime</td><td style="padding:8px;border-top:1px solid #eee;">Limited lifetime</td><td style="padding:8px;border-top:1px solid #eee;">Limited lifetime</td></tr>
<tr><td style="padding:8px;border-top:1px solid #eee;">Best For</td><td style="padding:8px;border-top:1px solid #eee;">Modern minimalists</td><td style="padding:8px;border-top:1px solid #eee;">Minimalist design</td><td style="padding:8px;border-top:1px solid #eee;">Eco-conscious travelers</td></tr>
</table>

<h2>Which Luggage Brand Wins?</h2>
<p><strong>Away</strong> is the most recognized brand with a great warranty. <strong>Monos</strong> offers sleek, minimalist design. <strong>Paravel</strong> leads on sustainability with recycled materials and carbon-neutral shipping. All three offer verified coupon codes — check the brand pages for current deals.</p>
''',
    },
    'personal-care-guide': {
        'title': 'Best Natural Personal Care Coupons: Native, Quip, Billie & More',
        'description': 'Save on natural deodorant, electric toothbrushes, razors, and custom skincare. Verified coupon codes for Native, Quip, Billie, Function of Beauty, and more.',
        'content': '''
<h2>Clean Personal Care for Less</h2>
<p>Natural personal care brands offer effective products without harsh chemicals. These DTC brands deliver better ingredients at better prices.</p>

<div class="brand-card"><a href="/brand/native" class="brand-name">🧴 Native</a><div class="brand-codes"><strong>NATIVE20</strong> — 20% off first order · Natural deodorant, aluminum-free</div></div>
<div class="brand-card"><a href="/brand/quip" class="brand-name">🪥 Quip</a><div class="brand-codes"><strong>QUIP20</strong> — 20% off first order · Electric toothbrush subscription</div></div>
<div class="brand-card"><a href="/brand/billie" class="brand-name">🪒 Billie</a><div class="brand-codes"><strong>BILLIE20</strong> — 20% off first order · Razors & body care for women</div></div>
<div class="brand-card"><a href="/brand/function%20of%20beauty" class="brand-name">🧪 Function of Beauty</a><div class="brand-codes"><strong>FOB20</strong> — 20% off first order · Custom shampoo, conditioner & skincare</div></div>
<div class="brand-card"><a href="/brand/huron" class="brand-name">🧔 Huron</a><div class="brand-codes"><strong>HURON15</strong> — 15% off first order · Natural men\'s grooming</div></div>

<h2>Why Switch to Natural Care?</h2>
<p>Natural personal care products avoid parabens, phthalates, aluminum, and synthetic fragrances. Subscribe & save for recurring discounts on your daily essentials.</p>
''',
    },
    'accessories-guide': {
        'title': 'Best Accessories & Jewelry Coupons: Mejuri, Quay, MVMT & More',
        'description': 'Save on sustainable jewelry, sunglasses, watches, and apparel. Verified coupon codes for Mejuri, Quay, MVMT, Mack Weldon, and more.',
        'content': '''
<h2>Timeless Style, Smart Savings</h2>
<p>Premium accessories at accessible prices — DTC brands deliver quality without the traditional retail markup.</p>

<div class="brand-card"><a href="/brand/mejuri" class="brand-name">💍 Mejuri</a><div class="brand-codes"><strong>MEJURI20</strong> — 20% off first order · Fine jewelry, everyday luxury</div></div>
<div class="brand-card"><a href="/brand/quay" class="brand-name">🕶️ Quay</a><div class="brand-codes"><strong>QUAY20</strong> — 20% off sitewide · Sunglasses & blue light glasses</div></div>
<div class="brand-card"><a href="/brand/mvmt" class="brand-name">⌚ MVMT</a><div class="brand-codes"><strong>MVMT20</strong> — 20% off sitewide · Minimalist watches & accessories</div></div>
<div class="brand-card"><a href="/brand/mack%20weldon" class="brand-name">👔 Mack Weldon</a><div class="brand-codes"><strong>MACK15</strong> — 15% off first order · Premium mens essentials</div></div>

<h2>Style Tips</h2>
<p>Stack email signup discounts with seasonal sales for the best deals. Referral programs earn you $20-30 credit per friend referred.</p>
''',
    },
    'mattress-buying-guide': {
        'title': 'Best Mattress Deals 2026: Casper, Tuft & Needle, Saatva, Helix & More',
        'description': 'Complete guide to buying a DTC mattress. Compare prices, trials, and warranties for Casper, Tuft & Needle, Saatva, Helix, Nectar, Purple, and more.',
        'content': '''
<h2>The Ultimate Mattress Buying Guide</h2>
<p>DTC mattresses offer premium quality at 50-70% less than traditional retail. Here\'s how to choose the right one and save big with verified coupon codes.</p>

<h2>Top Mattress Brands Compared</h2>
<div class="brand-card"><a href="/brand/casper" class="brand-name">🛏️ Casper</a><div class="brand-codes"><strong>email signup</strong> — 15% off · <strong>mattress discount</strong> — $100 off · 100-night trial · 10yr warranty</div></div>
<div class="brand-card"><a href="/brand/tuft%20&%20needle" class="brand-name">🛏️ Tuft & Needle</a><div class="brand-codes"><strong>TUFT20</strong> — 20% off · Adaptive foam · 100-night trial · 10yr warranty</div></div>
<div class="brand-card"><a href="/brand/saatva" class="brand-name">🛏️ Saatva</a><div class="brand-codes"><strong>SAATVA100</strong> — $100 off · Luxury innerspring · 365-night trial · 25yr warranty</div></div>
<div class="brand-card"><a href="/brand/helix%20sleep" class="brand-name">🛏️ Helix Sleep</a><div class="brand-codes"><strong>HELIX20</strong> — 20% off · Customized firmness · 100-night trial · 15yr warranty</div></div>
<div class="brand-card"><a href="/brand/nectar" class="brand-name">🛏️ Nectar</a><div class="brand-codes"><strong>NECTAR25</strong> — 25% off · Memory foam · 365-night trial · Forever warranty</div></div>
<div class="brand-card"><a href="/brand/purple" class="brand-name">🛏️ Purple</a><div class="brand-codes"><strong>PURPLE100</strong> — $100 off · Gel flex grid · 100-night trial · 10yr warranty</div></div>

<h2>Best Times to Buy</h2>
<p>Presidents Day (Feb), Memorial Day (May), and Black Friday (Nov) offer the deepest discounts — typically $100-300 off plus free pillows and sheets as bundle deals.</p>
''',
    },
    'fashion-guide': {
        'title': 'Best Ethical Fashion Coupons: Everlane, Marine Layer, Outerknown & More',
        'description': 'Save on sustainable fashion from top ethical brands. Verified coupon codes for Everlane, Marine Layer, Outerknown, Taylor Stitch, and more.',
        'content': '''
<h2>Fashion That Does Good</h2>
<p>Sustainable fashion proves you don\'t have to choose between style and ethics. These brands prioritize fair labor, organic materials, and environmental responsibility.</p>

<div class="brand-card"><a href="/brand/everlane" class="brand-name">👕 Everlane</a><div class="brand-codes"><strong>EVERLANE20</strong> — 20% off first order · Radical Transparency pricing</div></div>
<div class="brand-card"><a href="/brand/marine%20layer" class="brand-name">👕 Marine Layer</a><div class="brand-codes"><strong>MARINE15</strong> — 15% off first order · Ultra-soft recycled fabrics</div></div>
<div class="brand-card"><a href="/brand/outerknown" class="brand-name">🌊 Outerknown</a><div class="brand-codes"><strong>OUTER15</strong> — 15% off first order · Surf-inspired sustainable apparel</div></div>
<div class="brand-card"><a href="/brand/taylor%20stitch" class="brand-name">🧵 Taylor Stitch</a><div class="brand-codes"><strong>TAYLOR20</strong> — 20% off first order · Workshop-quality menswear</div></div>
<div class="brand-card"><a href="/brand/nisolo" class="brand-name">👞 Nisolo</a><div class="brand-codes"><strong>NISOLO20</strong> — 20% off first order · Handcrafted leather goods</div></div>

<h2>Why Ethical Fashion Matters</h2>
<p>The fashion industry produces 10% of global carbon emissions. Choosing sustainable, fair-trade brands reduces your wardrobe\'s environmental footprint.</p>
''',
    },
    'food-snacks-guide': {
        'title': 'Best Healthy Snack Coupons: GoMacro, Bobos, Partake Foods & More',
        'description': 'Save on healthy snacks, protein bars, and plant-based treats. Verified coupon codes for GoMacro, Bobo\'s, Partake Foods, and more.',
        'content': '''
<h2>Healthy Snacking on a Budget</h2>
<p>Clean eating doesn\'t have to be expensive. These DTC snack brands offer wholesome ingredients at subscription-friendly prices.</p>

<div class="brand-card"><a href="/brand/gomacro" class="brand-name">🌱 GoMacro</a><div class="brand-codes"><strong>GOMACRO20</strong> — 20% off first order · Organic plant protein bars</div></div>
<div class="brand-card"><a href="/brand/bobos" class="brand-name">🥧 Bobo\'s</a><div class="brand-codes"><strong>BOBOS20</strong> — 20% off first order · Oat bars & pastries, simple ingredients</div></div>
<div class="brand-card"><a href="/brand/partake%20foods" class="brand-name">🍪 Partake Foods</a><div class="brand-codes"><strong>PARTAKE20</strong> — 20% off first order · Allergy-friendly cookies</div></div>
<div class="brand-card"><a href="/brand/laird%20superfood" class="brand-name">🥥 Laird Superfood</a><div class="brand-codes"><strong>LAIRD15</strong> — 15% off first order · Functional mushroom & plant-based superfoods</div></div>

<h2>Smart Snacking Tips</h2>
<p>Subscribe & save for 10-20% off recurring orders. Variety packs offer the best value to try multiple flavors before committing.</p>
''',
    },
    'tech-guide': {
        'title': 'Best Tech Accessory Deals: Tile, Satechi, Mous, Skullcandy & More',
        'description': 'Save on tech accessories, cable organizers, phone cases, and wireless earbuds. Verified coupon codes for Tile, Satechi, Mous, Skullcandy, and more.',
        'content': '''
<h2>Better Tech for Less</h2>
<p>Tech accessories make daily life easier. These DTC brands offer quality alternatives to big-name electronics at better prices.</p>

<div class="brand-card"><a href="/brand/tile" class="brand-name">📍 Tile</a><div class="brand-codes"><strong>TILE20</strong> — 20% off first order · Bluetooth trackers, never lose your keys</div></div>
<div class="brand-card"><a href="/brand/satechi" class="brand-name">🔌 Satechi</a><div class="brand-codes"><strong>SATECHI15</strong> — 15% off first order · Premium USB-C hubs & accessories</div></div>
<div class="brand-card"><a href="/brand/mous" class="brand-name">📱 Mous</a><div class="brand-codes"><strong>MOUS20</strong> — 20% off first order · Limitless phone cases with magnetic accessories</div></div>
<div class="brand-card"><a href="/brand/skullcandy" class="brand-name">🎧 Skullcandy</a><div class="brand-codes"><strong>SKULL15</strong> — 15% off first order · Wireless earbuds & headphones</div></div>

<h2>Tech Shopping Tips</h2>
<p>Bundle accessories to save 10-15% on checkout. Refurbished/open-box deals can save 20-40%. Major sales: Prime Day, Black Friday, Cyber Monday.</p>
''',
    },
    'skincare-guide': {
        'title': 'Best Clean Beauty Coupons: Cocokind, Versed, Bubble, Dieux & More',
        'description': 'Save on clean, vegan skincare. Verified coupon codes for Cocokind, Versed, Bubble Skincare, Dieux, and more affordable beauty brands.',
        'content': '''
<h2>Clean Beauty for Every Budget</h2>
<p>You don\'t need $100 serums for great skin. These affordable DTC beauty brands use clean, effective ingredients at accessible prices.</p>

<div class="brand-card"><a href="/brand/cocokind" class="brand-name">🌿 Cocokind</a><div class="brand-codes"><strong>COCO20</strong> — 20% off first order · Organic skincare staples under $25</div></div>
<div class="brand-card"><a href="/brand/versed" class="brand-name">🧴 Versed</a><div class="brand-codes"><strong>VERSED20</strong> — 20% off first order · Dermatologist-developed, under $25</div></div>
<div class="brand-card"><a href="/brand/bubble%20skincare" class="brand-name">🫧 Bubble Skincare</a><div class="brand-codes"><strong>BUBBLE20</strong> — 20% off first order · Teen & young adult skincare</div></div>
<div class="brand-card"><a href="/brand/dieux" class="brand-name">🧪 Dieux</a><div class="brand-codes"><strong>DIEUX15</strong> — 15% off first order · High-performance, transparent skincare</div></div>

<h2>How to Save on Beauty</h2>
<p>Email signup = 15-20% off first order. Subscribe & save for recurring discounts. Gift sets offer the best value — typically 20-30% savings vs buying individually.</p>
''',
    },
}

# ===== 投票 & 提交 API =====
@app.route('/api/vote', methods=['POST'])
def api_vote():
    """投票：coupon有用/过期"""
    data = request.get_json()
    code = data.get('code', '')
    brand = data.get('brand', '')
    vote = data.get('vote', '')  # 'useful' or 'expired'
    if not code or not vote:
        return jsonify({'ok': False, 'msg': 'missing fields'})
    
    votes = load_votes()
    key = f'{brand}::{code}'
    if key not in votes:
        votes[key] = {'useful': 0, 'expired': 0}
    votes[key][vote] = votes[key].get(vote, 0) + 1
    save_votes(votes)
    
    return jsonify({'ok': True, 'current': votes[key]})

@app.route('/submit', methods=['GET', 'POST'])
def submit_coupon():
    return _submit('en')

@app.route('/zh/submit', methods=['GET', 'POST'])
def submit_coupon_zh():
    return _submit('zh')

def _submit(lang='en'):
    if request.method == 'GET':
        data = load_coupons()
        brands = list(set(c['brand'] for c in data['coupons']))
        return render_template('submit.html',
                             brands=sorted(brands),
                             ga_id=GA_MEASUREMENT_ID,
                             gc_domain=GOATCOUNTER_DOMAIN,
                             umami_url=UMAMI_URL,
                             umami_site_id=UMAMI_WEBSITE_ID,
                             lang=lang,
                             lang_data=LANG[lang])
    
    # POST
    brand = request.form.get('brand', '').strip()
    code = request.form.get('code', '').strip().upper()
    discount = request.form.get('discount', '').strip()
    title = request.form.get('title', '').strip()
    url = request.form.get('url', '').strip()
    
    if not brand or not code:
        return 'Brand and coupon code required', 400
    
    # 保存提交到待审核
    sub_file = os.path.join(os.path.dirname(__file__), 'data', 'submissions.json')
    subs = []
    if os.path.exists(sub_file):
        try:
            subs = json.load(open(sub_file))
        except:
            subs = []
    subs.append({
        'brand': brand, 'code': code, 'discount': discount,
        'title': title, 'url': url, 'submitted_at': TODAY,
        'ip': request.remote_addr
    })
    os.makedirs(os.path.dirname(sub_file), exist_ok=True)
    json.dump(subs, open(sub_file, 'w'), indent=2)
    return '✅ Thanks! Your coupon has been submitted for review.', 200, {'Content-Type': 'text/plain; charset=utf-8'}

# ===== 文章路有 =====
@app.route('/article/<slug>')
def article_page(slug):
    article = ARTICLES.get(slug)
    if not article:
        return 'Article not found', 404
    data = load_coupons()
    brands = set(c['brand'] for c in data['coupons'])
    
    # 文章FAQ
    art_faq = ARTICLE_FAQ.get(slug, HOMEPAGE_FAQ)
    faq_schema = generate_article_schema(article['title'], article['description'], slug, art_faq)
    faq_html = make_faq_html(art_faq)
    
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
                           total_coupons=data['total'],
                           faq_schema_json=json.dumps(faq_schema, indent=2),
                           faq_html=faq_html,
                           date_published=TODAY,
                           date_modified=TODAY)


if __name__ == '__main__':
    print('🚀 Coupon Bot Web (GEO v2) @ http://localhost:5000')
    app.run(host='0.0.0.0', port=5000, debug=False)
