# 🏷️ CouponBot — 跨境优惠券联盟佣金站

## 做什么
自动爬取+展示跨境DTC品牌优惠码，靠联盟佣金赚钱。

## 怎么赚钱
- 用户搜 "XX coupon code" → 进你的站 → 点联盟链接去品牌下单 → 你拿 **5~20%** 佣金
- 这叫 **Last-click attribution**（最后一次点击归因）
- 不需要写内容、做品牌，只需要拦截用户结账前最后一搜

## 项目结构
```
coupon-bot/
├── scraper.py       # 爬虫（种子20个码 + Reddit补充）
├── app.py           # Flask Web前台（localhost:5000）
├── config.py        # 配置：品牌列表、品类、Reddit子版块
├── templates/
│   └── index.html   # 前台页面（点码自动复制, SEO友好）
├── data/
│   └── coupons.json  # 缓存数据（当前20个码）
└── README.md
```

## 当前状态 (2026-06-10)
- ✅ 代码完整可用
- ✅ 20个种子优惠码（家居/宠物/健身品类）
- ✅ Web前台正常运行
- ⏳ 未注册联盟平台（需师兄亲自操作）
- ⏳ 未部署到公网

## 继续搞的步骤
1. 注册联盟平台: Awin / ShareASale / Impact
2. 获取品牌联盟链接 → 告诉我，我接进输出
3. 部署到 Vercel / Cloudflare Pages 当独立站
4. 加 Google Analytics 看搜索词
5. 优化爬虫：爬Reddit帖子正文+评论提更多码

## 启动
```bash
cd C:\Users\86130\Vibe-Trading\coupon-bot
python scraper.py   # 爬取更新
python app.py       # 启动Web
# 浏览器打开 http://localhost:5000
```
