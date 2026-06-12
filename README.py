#!/usr/bin/env python3
"""
Coupon Bot 使用指南

📦 项目结构
  coupon-bot/
    ├── config.py       # 配置：品牌列表、品类
    ├── scraper.py      # 爬虫：自动抓取Reddit+官网优惠码
    ├── app.py          # Web：Flask前台展示
    ├── templates/
    │   └── index.html  # 网页模板（SEO友好）
    └── data/
        └── coupons.json # 缓存数据

🚀 启动步骤
  1. 爬取优惠码:    python scraper.py
  2. 启动Web:       python app.py
  3. 浏览器打开:    http://localhost:5000

📋 需要手动注册的联盟平台
  - Awin:       https://www.awin.com/gb/publisher
  - ShareASale: https://www.shareasale.com/shareasale.cfm
  - Impact:     https://impact.com/
  注册后获取每个品牌的联盟链接，替换scraper里的输出链接

🔄 定时更新 (cron)
  hermes cron create \
    --prompt "运行coupon-bot爬虫更新优惠码并启动web" \
    --schedule "0 */6 * * *" \
    --enabled-toolsets terminal

🎯 扩展品类
  编辑 config.py 中的 TARGET_NICHES
  添加新品牌+对应的Reddit子版块
"""
print("📖 使用说明已加载，请查看源代码注释")
