"""Coupon Bot 配置"""
import os

BASE = os.path.dirname(os.path.abspath(__file__))

# 爬虫频率 (小时)
SCRAPE_INTERVAL = 6

# 缓存文件
COUPON_FILE = os.path.join(BASE, 'data', 'coupons.json')

# 目标品类 - 先做DTC家居/工具品牌，壁垒低、巨头少
TARGET_NICHES = {
    'home_garden': {
        'name': '家居花园',
        'brands': [
            'Article', 'Burrow', 'Brooklinen', 'Parachute',
            'West Elm', 'Rove Concepts',
            'Sabai', 'Avocado',
        ],
        'reddit_subs': ['homeowners', 'DesignMyRoom'],
    },
    'pet_supplies': {
        'name': '宠物用品',
        'brands': [
            'Furbo', 'LitterRobot',
            'V-Dog', 'Wild Earth',
        ],
        'reddit_subs': ['puppy101', 'CatAdvice'],
    },
    'fitness_wellness': {
        'name': '健身健康',
        'brands': [
            'Peloton', 'Tonal', 'Whoop', 'Oura', 'EightSleep',
            'Hydrow', 'NordicTrack', 'Echelon',
        ],
        'reddit_subs': ['fitness', 'weightlifting'],
    },
}

# ===== 网站统计 =====
# Umami (推荐!) — 填你的 Umami Cloud 链接和网站ID即可
# 注册: https://cloud.umami.is (邮箱注册，无需翻墙)
# 支持自定义事件追踪（优惠券点击量）
UMAMI_URL = ''      # 例: 'https://cloud.umami.is'
UMAMI_WEBSITE_ID = ''  # 例: 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'

# GoatCounter 备选 — 无需翻墙，但只能看访问量
GOATCOUNTER_DOMAIN = ''  # 例: 'couponbot'

# Google Analytics (GA4) - 需翻墙
GA_MEASUREMENT_ID = ''  # 例: 'G-XXXXXXXXXX'

# 联盟平台（需手动注册）
AFFILIATE_NETWORKS = {
    'Awin': 'https://www.awin.com/gb/publisher',
    'ShareASale': 'https://www.shareasale.com/shareasale.cfm',
    'Impact': 'https://impact.com/',
    'Partnerize': 'https://partnerize.com/',
}
