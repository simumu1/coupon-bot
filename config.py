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
            'Supergoop', 'Saie', 'Jones Road Beauty',
            'True Botanicals', 'OSEA',
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
            'Ethique', 'Dropps', 'Stasher', 'Hydro Flask',
        ],
        'reddit_subs': ['ZeroWaste', 'EcoFriendly'],
    },
    'personal_care': {
        'name': '个人护理',
        'desc': 'Save on natural personal care and grooming. Verified coupon codes for Native, Quip, Billie, Huron, Function of Beauty — clean ingredients, sustainable packaging.',
        'brands': [
            'Native', 'Quip', 'Billie', 'Huron',
            'Function of Beauty', 'Cora', 'LOLA',
        ],
        'reddit_subs': ['SkincareAddiction', 'HaircareScience'],
    },
    'accessories': {
        'name': '配饰鞋包',
        'desc': 'Save on accessories and lifestyle brands. Verified coupon codes for Mejuri, Quay, MVMT, Mack Weldon — sustainable fashion and timeless accessories.',
        'brands': [
            'Mejuri', 'Quay', 'MVMT', 'Mack Weldon',
        ],
        'reddit_subs': ['ethicalfashion', 'BuyItForLife'],
    },
    'social_impact': {
        'name': '公益品牌',
        'desc': 'Save with purpose. Verified coupon codes for brands that give back — TOMS, Bombas, Allbirds, Cotopaxi, and more. Every purchase supports a cause.',
        'brands': [
            'TOMS', 'Bombas', 'Allbirds', 'Cotopaxi',
            'United By Blue', 'Pura Vida',
        ],
        'reddit_subs': ['BuyItForLife', 'ethicalfashion'],
    },
    'vegan_food': {
        'name': '素食食品',
        'desc': 'Save on plant-based food and drinks. Verified coupon codes for Orgain, Miyoko Creamery, Ripple Foods, and more vegan-friendly brands.',
        'brands': [
            'Orgain', "Miyoko's Creamery", 'Ripple Foods',
            'Thrive Market', 'Veestro',
        ],
        'reddit_subs': ['vegan', 'PlantBasedDiet'],
    },
    # 以下是从PA补齐的品类（避免覆盖丢失）
    'food_beverage': {
        'name': '食品饮料',
        'desc': 'Find verified coupon codes for plant-based food and beverage brands. Save on vegan cereal, oat milk, healthy snacks, and meal replacements from DTC brands.',
        'brands': [
            'Magic Spoon', 'Huel', 'Oatly', 'Califia Farms',
            'Biena', 'No Cow',
        ],
        'reddit_subs': ['vegan', 'PlantBasedDiet'],
    },
    'tech_gadgets': {
        'name': '科技配件',
        'desc': 'Save on sustainable tech accessories and gadgets. Coupon codes for compostable phone cases, wireless earbuds, chargers, and smart devices.',
        'brands': [
            'Pela', 'Casetify', 'Nomad', 'Anker', 'Nothing',
        ],
        'reddit_subs': ['techaccessories', 'gadgets'],
    },
    'travel': {
        'name': '旅行箱包',
        'desc': 'Premium luggage and travel accessories at discounted prices. Verified coupon codes for Away, Monos, Paravel, Roam, and more sustainable travel brands.',
        'brands': [
            'Away', 'Monos', 'Paravel', 'Roam', 'Béis',
        ],
        'reddit_subs': ['travel', 'onebag'],
    },
    'baby_kids': {
        'name': '母婴用品',
        'desc': 'Save on baby essentials with verified coupon codes. Vegan diapers, organic baby clothes, and plant-based baby food from trusted DTC brands.',
        'brands': [
            'Honest Company', "Burt's Bees Baby", 'Once Upon a Farm',
            'Happy Family', 'Lalo',
        ],
        'reddit_subs': ['BabyBumps', 'Parenting'],
    },
    'intimates': {
        'name': '内衣家居',
        'desc': 'Premium bras, underwear, and loungewear at discount prices. Inclusive sizing, sustainable materials, and verified coupon codes from top DTC intimates brands.',
        'brands': [
            'ThirdLove', 'CUUP', 'Parade', 'MeUndies', 'Lively',
        ],
        'reddit_subs': ['ABraThatFits', 'ethicalfashion'],
    },
    'candles_fragrance': {
        'name': '香氛蜡烛',
        'desc': 'Find verified coupon codes for artisanal candles and home fragrances. Vegan soy candles, unique scents from top DTC fragrance brands.',
        'brands': [
            'Boy Smells', 'Otherland', 'P.F. Candle Co',
            'Homesick', 'Snif', 'Brooklyn Candle Studio',
        ],
        'reddit_subs': ['candles', 'fragrance'],
    },
    'coffee_tea': {
        'name': '咖啡茶叶',
        'desc': 'Save on specialty coffee and premium tea subscriptions. Verified coupon codes for single-origin roasts, cold brew, and loose leaf tea from top DTC brands.',
        'brands': [
            'Trade Coffee', 'Atlas Coffee Club', 'Wandering Bear',
            'Art of Tea', 'Four Sigmatic', 'MUDWTR', 'Laird Superfood',
        ],
        'reddit_subs': ['Coffee', 'tea'],
    },
    'mattresses': {
        'name': '床垫睡眠',
        'desc': 'Save on premium DTC mattresses and sleep accessories. Verified coupon codes for Casper, Tuft & Needle, Saatva, Helix, Nectar, Purple, and more — with risk-free trials.',
        'brands': [
            'Casper', 'Tuft & Needle', 'Saatva', 'Helix Sleep',
            'Nectar', 'Purple', 'Buffy', 'Bearaby',
        ],
        'reddit_subs': ['Mattress', 'sleep'],
    },
    'fitness_expanded': {
        'name': '健身运动',
        'desc': 'Save on home gym equipment, fitness trackers, and smart wellness devices. Verified coupon codes for Peloton, Mirror, FightCamp, Aviron, and more.',
        'brands': [
            'Peloton', 'Tonal', 'Whoop', 'Oura', 'EightSleep',
            'Hydrow', 'NordicTrack', 'Echelon',
            'FightCamp', 'Aviron', 'Mirror',
        ],
        'reddit_subs': ['fitness', 'weightlifting'],
    },
    'fashion_expanded': {
        'name': '时尚品牌',
        'desc': 'Sustainable and ethical fashion from top DTC brands. Vegan sneakers, organic cotton, recycled materials — Everlane, Marine Layer, Outerknown, Patagonia and more.',
        'brands': [
            'Cariuma', 'Rothy', 'Tentree', 'Pact',
            'Everlane', 'Marine Layer', 'Outerknown',
            'Taylor Stitch', 'Nisolo', 'Saola',
        ],
        'reddit_subs': ['ethicalfashion', 'BuyItForLife'],
    },
    'food_snacks': {
        'name': '零食饮品',
        'desc': 'Save on healthy snacks, protein bars, and functional beverages. Verified coupon codes for GoMacro, Bobos, Partake Foods, Laird Superfood, and more.',
        'brands': [
            'Magic Spoon', 'Huel', 'Oatly', 'Califia Farms',
            'Biena', 'No Cow', 'GoMacro', "Bobo's",
            'Partake Foods', 'Laird Superfood',
        ],
        'reddit_subs': ['vegan', 'PlantBasedDiet'],
    },
    'tech_expanded': {
        'name': '科技数码',
        'desc': 'Save on sustainable tech accessories and gadgets. Verified coupon codes for phone cases, cables, wireless earbuds, trackers, and smart home devices.',
        'brands': [
            'Pela', 'Casetify', 'Nomad', 'Anker', 'Nothing',
            'Tile', 'Satechi', 'Mous', 'Skullcandy',
        ],
        'reddit_subs': ['techaccessories', 'gadgets'],
    },
    'beauty_expanded': {
        'name': '纯素美妆',
        'desc': 'Clean, vegan, cruelty-free beauty brands. Verified coupon codes for skincare, makeup, and sunscreen from Glow Recipe, Cocokind, Versed, Bubble, and more.',
        'brands': [
            'YouthToThePeople', 'Tower28', 'Biossance', 'Kosas',
            'Supergoop', 'Saie', 'Jones Road Beauty',
            'True Botanicals', 'OSEA',
            'Cocokind', 'Versed', 'Bubble Skincare', 'Dieux',
        ],
        'reddit_subs': ['SkincareAddiction', 'asianbeauty'],
    },
}

# ===== 网站统计 =====
UMAMI_URL = 'https://cloud.umami.is'
UMAMI_WEBSITE_ID = '071f352a-eb36-4007-997a-4fe8afa40add'
GOATCOUNTER_DOMAIN = ''
GA_MEASUREMENT_ID = ''

# 联盟平台（需手动注册）
AFFILIATE_NETWORKS = {
    'Awin': 'https://www.awin.com/gb/publisher',
    'ShareASale': 'https://www.shareasale.com/shareasale.cfm',
    'Impact': 'https://impact.com/',
    'Partnerize': 'https://partnerize.com/',
}
