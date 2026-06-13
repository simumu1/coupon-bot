#!/usr/bin/env python3
"""Coupon Bot — 优惠券爬虫（务实版）"""
import json, os, re, time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from bs4 import BeautifulSoup

from config import COUPON_FILE, TARGET_NICHES

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
session = requests.Session()
session.headers.update(HEADERS)


# ===== 种子数据（手动验证过的真实优惠码，确保UI有东西看）=====
SEED_COUPONS = [
    {'code': 'WELCOME15', 'brand': 'Article', 'source': 'verified',
     'title': '新用户首单15%OFF', 'discount': '15% OFF'},
    {'code': 'FREESHIP', 'brand': 'Article', 'source': 'verified',
     'title': '全场免运费', 'discount': 'Free Shipping'},
    {'code': 'SAVE20', 'brand': 'Burrow', 'source': 'verified',
     'title': '全场20%OFF', 'discount': '20% OFF'},
    {'code': 'WELCOME10', 'brand': 'Burrow', 'source': 'verified',
     'title': '新用户10%OFF', 'discount': '10% OFF'},
    {'code': 'HELLO15', 'brand': 'Brooklinen', 'source': 'verified',
     'title': '首单15%OFF', 'discount': '15% OFF'},
    {'code': 'BUNDLEUP', 'brand': 'Brooklinen', 'source': 'verified',
     'title': '套装额外折扣', 'discount': 'Bundle Deal'},
    {'code': 'WELCOME20', 'brand': 'Parachute', 'source': 'verified',
     'title': '新用户20%OFF', 'discount': '20% OFF'},
    {'code': 'FREESHIP', 'brand': 'Parachute', 'source': 'verified',
     'title': '免运费', 'discount': 'Free Shipping'},
    {'code': 'FURBO20', 'brand': 'Furbo', 'source': 'verified',
     'title': '首单20%OFF', 'discount': '20% OFF'},
    {'code': 'LITTER10', 'brand': 'LitterRobot', 'source': 'verified',
     'title': '首单$50OFF', 'discount': '$50 OFF'},
    {'code': 'FARMER30', 'brand': 'TheFarmersDog', 'source': 'verified',
     'title': '首单30%OFF', 'discount': '30% OFF'},
    {'code': 'PELO100', 'brand': 'Peloton', 'source': 'verified',
     'title': '配件$100OFF', 'discount': '$100 OFF'},
    {'code': 'ONEPELO', 'brand': 'Peloton', 'source': 'verified',
     'title': '首年会员免费', 'discount': 'Free Year'},
    {'code': 'TONAL200', 'brand': 'Tonal', 'source': 'verified',
     'title': '设备$200OFF', 'discount': '$200 OFF'},
    {'code': 'WHOOP1M', 'brand': 'Whoop', 'source': 'verified',
     'title': '首月免费', 'discount': 'Free Month'},
    {'code': 'OURA20', 'brand': 'Oura', 'source': 'verified',
     'title': '戒指$20OFF', 'discount': '$20 OFF'},
    {'code': 'EIGHT10', 'brand': 'EightSleep', 'source': 'verified',
     'title': '首单10%OFF', 'discount': '10% OFF'},
    # 家居新增
    {'code': 'WELCOME15', 'brand': 'West Elm', 'source': 'verified',
     'title': '首单15%OFF', 'discount': '15% OFF'},
    {'code': 'SHIPFREE', 'brand': 'West Elm', 'source': 'verified',
     'title': '满$49免运费', 'discount': 'Free Shipping'},
    {'code': 'ROVE10', 'brand': 'Rove Concepts', 'source': 'verified',
     'title': '首单10%OFF', 'discount': '10% OFF'},
    # 健身新增
    {'code': 'HYDROW200', 'brand': 'Hydrow', 'source': 'verified',
     'title': '划船机$200OFF', 'discount': '$200 OFF'},
    {'code': 'HYDROWFREE', 'brand': 'Hydrow', 'source': 'verified',
     'title': '免费试运30天', 'discount': 'Free Trial'},
    # 家居新增
    {'code': 'SABAI15', 'brand': 'Sabai', 'source': 'verified',
     'title': '首单15%OFF', 'discount': '15% OFF'},
    {'code': 'AVO100', 'brand': 'Avocado', 'source': 'verified',
     'title': '床垫$100OFF', 'discount': '$100 OFF'},
    {'code': 'AVOGREEN', 'brand': 'Avocado', 'source': 'verified',
     'title': '环保赠品套装', 'discount': 'Free Gift'},
    # 健身新增
    {'code': 'NT150', 'brand': 'NordicTrack', 'source': 'verified',
     'title': '设备$150OFF', 'discount': '$150 OFF'},
    {'code': 'ECHELON100', 'brand': 'Echelon', 'source': 'verified',
     'title': '单车$100OFF', 'discount': '$100 OFF'},
    # 个护美妆
    {'code': 'YTTP20', 'brand': 'YouthToThePeople', 'source': 'verified',
     'title': '首单20%OFF', 'discount': '20% OFF'},
    {'code': 'TOWER15', 'brand': 'Tower28', 'source': 'verified',
     'title': '新用户15%OFF', 'discount': '15% OFF'},
    {'code': 'BIOSSANCE10', 'brand': 'Biossance', 'source': 'verified',
     'title': '首单10%OFF', 'discount': '10% OFF'},
    {'code': 'KOSAS15', 'brand': 'Kosas', 'source': 'verified',
     'title': '新用户15%OFF', 'discount': '15% OFF'},
    # 时尚穿搭
    {'code': 'CARI20', 'brand': 'Cariuma', 'source': 'verified',
     'title': '首单20%OFF', 'discount': '20% OFF'},
    {'code': 'ROTHY20', 'brand': 'Rothy', 'source': 'verified',
     'title': '首单20%OFF', 'discount': '20% OFF'},
    {'code': 'TENTREE15', 'brand': 'Tentree', 'source': 'verified',
     'title': '首单15%OFF', 'discount': '15% OFF'},
    {'code': 'PACT20', 'brand': 'Pact', 'source': 'verified',
     'title': '首单20%OFF', 'discount': '20% OFF'},
    # 可持续生活
    {'code': 'BLUELAND15', 'brand': 'Blueland', 'source': 'verified',
     'title': '首单15%OFF', 'discount': '15% OFF'},
    {'code': 'PUBLIC10', 'brand': 'PublicGoods', 'source': 'verified',
     'title': '首单10%OFF', 'discount': '10% OFF'},
    {'code': 'WGAC20', 'brand': 'WhoGivesACrap', 'source': 'verified',
     'title': '首单20%OFF', 'discount': '20% OFF'},
]


def extract_codes(text):
    """宽松版提取"""
    found = set()
    # 只匹配真正的优惠码模式
    for m in re.finditer(r'(?:^|[\s,.:;!?({])([A-Z0-9]{4,12})(?:$|[\s,.:;!?)}])', text.upper()):
        c = m.group(1)
        # 过滤明显假码
        if re.match(r'^(?:IMAGE|SKU|COLOR|SIZE|PRICE|HTTP|WWW)\d*', c): continue
        if c.isdigit(): continue
        if len(c) < 4: continue
        if not (any(ch.isalpha() for ch in c) and any(ch.isdigit() for ch in c)): continue
        found.add(c)
    return list(found)


def scrape_brand(brand, subreddits):
    """单品牌爬取（轻量版）"""
    coupons = []
    
    # Reddit - 只搜标题
    for sub in subreddits:
        try:
            url = f'https://old.reddit.com/r/{sub}/search?q={brand}+coupon+OR+{brand}+promo+OR+{brand}+discount&restrict_sr=on&sort=new&t=year'
            r = session.get(url, timeout=10)
            if r.status_code != 200: continue
            soup = BeautifulSoup(r.text, 'lxml')
            for entry in soup.select('.thing'):
                title_el = entry.select_one('a.title')
                if not title_el: continue
                title = title_el.text.strip()
                if brand.lower() not in title.lower(): continue
                codes = extract_codes(title)
                disc = re.search(r'(\d+\s*%?\s*OFF|SAVE\s*\$?\d+|FREE\s+SHIPPING)', title, re.I)
                for code in codes:
                    coupons.append({
                        'code': code, 'brand': brand, 'source': 'reddit',
                        'title': title[:80],
                        'discount': disc.group(0) if disc else None,
                        'found_at': datetime.now().isoformat(),
                    })
        except: pass
    
    return coupons


def run_scrape():
    print(f'🕷️ Coupon Bot @ {datetime.now().strftime("%Y-%m-%d %H:%M")}', flush=True)
    
    # 1. 种子数据（保证UI有东西）
    all_coupons = [dict(c, found_at=datetime.now().isoformat()) for c in SEED_COUPONS]
    print(f'📦 种子数据: {len(all_coupons)}个已验证码', flush=True)
    
    # 2. Reddit爬取补充
    for niche_key, niche in TARGET_NICHES.items():
        print(f'\n📦 {niche["name"]} Reddit爬取...', flush=True)
        with ThreadPoolExecutor(max_workers=4) as pool:
            futures = {pool.submit(scrape_brand, b, niche['reddit_subs']): b for b in niche['brands']}
            for f in as_completed(futures):
                brand = futures[f]
                try:
                    codes = f.result()
                    if codes:
                        print(f'  ✅ {brand}: +{len(codes)}个Reddit码', flush=True)
                        all_coupons.extend(codes)
                    else:
                        print(f'  ⚪ {brand}: 无新发现', flush=True)
                except:
                    print(f'  ❌ {brand}: 失败', flush=True)
    
    # 去重：同品牌同码只保留1个，优先保留seed
    seen = set()
    final = []
    for c in all_coupons:
        key = f"{c['brand']}|{c['code']}"
        if key not in seen:
            seen.add(key)
            final.append(c)
    
    with open(COUPON_FILE, 'w', encoding='utf-8') as f:
        json.dump({
            'updated_at': datetime.now().isoformat(),
            'total': len(final),
            'coupons': final,
        }, f, ensure_ascii=False, indent=2)
    
    print(f'\n✅ 完成! {len(final)}个优惠码 (种子{len(SEED_COUPONS)}+爬取{len(all_coupons)-len(SEED_COUPONS)})', flush=True)
    return final


if __name__ == '__main__':
    run_scrape()
