"""Coupon Bot 配置"""
import os

BASE = os.path.dirname(os.path.abspath(__file__))

# 爬虫频率 (小时)
SCRAPE_INTERVAL = 6

# 缓存文件
COUPON_FILE = os.path.join(BASE, 'data', 'coupons.json')

# 目标品类
TARGET_NICHES = {
    'home_garden': {
        'name': '家居花园',
        'desc': 'Find verified coupon codes for top DTC furniture and home decor brands. Save on sofas, beds, mattresses, and home essentials from sustainable and vegan-friendly brands.',
        'brands': [
            'Article', 'Burrow', 'Brooklinen', 'Parachute',
            'West Elm', 'Rove Concepts',
            'Sabai', 'Avocado',
        ],
        'reddit_subs': ['homeowners', 'DesignMyRoom'],
    },
    'pet_supplies': {
        'name': '宠物用品',
        'desc': 'Find coupons for plant-based pet food and smart pet gadgets. Vegan-friendly dog food, eco-friendly litter boxes, and pet cameras — all cruelty-free.',
        'brands': [
            'Furbo', 'LitterRobot',
            'V-Dog', 'Wild Earth',
        ],
        'reddit_subs': ['puppy101', 'CatAdvice'],
    },
    'fitness_wellness': {
        'name': '健身健康',
        'desc': 'Save on home gym equipment, fitness trackers, and smart wellness devices. Coupons for Peloton, NordicTrack, Whoop, Oura, and more — hardware only, no supplements.',
        'brands': [
            'Peloton', 'Tonal', 'Whoop', 'Oura', 'EightSleep',
            'Hydrow', 'NordicTrack', 'Echelon',
        ],
        'reddit_subs': ['fitness', 'weightlifting'],
    },
    'beauty_skincare': {
        'name': '个护美妆',
        'desc': 'Discover clean, vegan, and cruelty-free beauty brands with verified coupon codes. Skincare and makeup from Youth to the People, Tower 28, Biossance, and Kosas — no animal testing, no harsh alcohol.',
        'brands': [
            'YouthToThePeople', 'Tower28', 'Biossance', 'Kosas',
        ],
        'reddit_subs': ['SkincareAddiction', 'asianbeauty'],
    },
    'fashion': {
        'name': '时尚穿搭',
        'desc': 'Sustainable and ethical fashion coupon codes. Vegan sneakers, recycled material shoes, organic cotton apparel from Cariuma, Rothy\'s, Tentree, and Pact — fashion that\'s kind to animals and the planet.',
        'brands': [
            'Cariuma', 'Rothy', 'Tentree', 'Pact',
        ],
        'reddit_subs': ['ethicalfashion', 'BuyItForLife'],
    },
    'eco_living': {
        'name': '可持续生活',
        'desc': 'Eco-friendly home essentials coupon codes. Plastic-free cleaning products, sustainable household goods, and bamboo toilet paper from Blueland, Public Goods, and Who Gives A Crap — better for your home and the Earth.',
        'brands': [
            'Blueland', 'PublicGoods', 'WhoGivesACrap',
        ],
        'reddit_subs': ['ZeroWaste', 'EcoFriendly'],
    },
}

# ===== 网站统计 =====
UMAMI_URL = ''
UMAMI_WEBSITE_ID = ''
GOATCOUNTER_DOMAIN = ''
GA_MEASUREMENT_ID = ''

# 联盟平台（需手动注册）
AFFILIATE_NETWORKS = {
    'Awin': 'https://www.awin.com/gb/publisher',
    'ShareASale': 'https://www.shareasale.com/shareasale.cfm',
    'Impact': 'https://impact.com/',
    'Partnerize': 'https://partnerize.com/',
}
