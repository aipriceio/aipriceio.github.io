#!/usr/bin/env python3
"""Build the aipriceio.github.io landing page from a live radar snapshot."""
import json, html, os, hashlib
from datetime import datetime, timezone, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "site")
REF = "gh-aipriceio"
SITE = "https://aiprice.io"

d = json.load(open(os.path.join(HERE, "radar.json")))
products = d["products"]
bz = timezone(timedelta(hours=8))
gen = datetime.fromisoformat(d["generated_at"].replace("Z", "+00:00")).astimezone(bz)
gen_label = gen.strftime("%Y-%m-%d %H:%M")

offers_total = sum(p["offers_total"] for p in products)
instock_total = sum(p["in_stock"] for p in products)
stores = set()
for p in products:
    for o in p.get("offers") or []:
        stores.add(o["store"])
store_n = len(stores)

FLAGSHIP = ["chatgpt-plus-recharge", "claude-pro-month", "gemini-pro-recharge", "super-grok"]
by_slug = {p["slug"]: p for p in products}
cards = []
for slug in FLAGSHIP:
    p = by_slug.get(slug)
    if not p:
        continue
    short = p["name"][len(p["platform"]):].strip() or p["name"]
    cards.append(
        f'''      <a class="card plat" href="{SITE}/stock/{p["slug"]}/?ch={REF}" rel="noopener">
        <div class="row"><span class="tag">{html.escape(p["platform"])}</span><span class="t-sm muted">在售 {p["in_stock"]:,} 条</span></div>
        <div class="t-xl semi name">{html.escape(short)}</div>
        <div class="price"><span class="t-3xl semi">¥{p["lowest"]:,.2f}</span><span class="t-sm muted">起</span></div>
        <div class="t-sm muted">{html.escape(p["type"])} · 共 {p["offers_total"]:,} 条报价</div>
      </a>'''
    )

top = sorted([p for p in products if p["in_stock"] > 0], key=lambda p: (-p["in_stock"], p["lowest"]))[:12]
rows = []
for p in top:
    rows.append(
        f'''        <tr onclick="location.href='{SITE}/stock/{p["slug"]}/?ch={REF}'" tabindex="0" role="link">
          <td data-label="商品"><span class="pname">{html.escape(p["name"])}</span><span class="t-xs muted sub">{html.escape(p["platform"])} · {html.escape(p["type"])}</span></td>
          <td data-label="最低价" class="num">¥{p["lowest"]:,.2f}</td>
          <td data-label="在售" class="num">{p["in_stock"]:,}</td>
          <td data-label="报价总数" class="num muted">{p["offers_total"]:,}</td>
        </tr>'''
    )

FAQ = [
    ("aiprice 自己卖卡吗？",
     "不卖。它只把各家店铺的在售报价汇总到一张表里，交易、发货和售后都发生在店铺自己的网站上。"),
    ("价格多久更新一次？",
     "上游每 5 分钟生成一版快照，本站每 1 小时同步一次，页面顶部会标明本次数据的生成时间。"),
    ("同一款会员为什么差价能超过一倍？",
     "渠道不同。官方卡充、共享成员位、成品号、区域卡的成本结构不一样，能给出的质保条款也不一样，这些差异在商品页里分开列出。"),
    ("最便宜的那条报价就是最好的吗？",
     "不一定。极低价格通常伴随限量、限区或者限账号状态，下单前先看报价标题里的规格说明和质保范围。"),
    ("「在售」的数量是什么意思？",
     "该报价当前标注的可售条数，用来判断这条货源深不深，不是库存承诺，最终以店铺页面显示的为准。"),
    ("需要注册才能查价吗？",
     "不需要。查价、看报价分布、点去店铺都可以直接进行。注册的作用是保存关注的商品和查看价格历史。"),
    ("支持哪些语言？",
     "简体中文、繁体中文、英文、日文四种界面，商品名在英文和日文页保留原文，避免翻译后对不上店铺。"),
    ("页面上看到的价格，和我下单时不一样？",
     "店铺价格随时会变，这里展示的是快照。下单前请以店铺页面显示的价格和规格为准。"),
]
faq_html = "\n".join(
    f'''        <details class="qa">
          <summary><span>{html.escape(q)}</span><svg class="chev" width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M4 6.5L8 10.5L12 6.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg></summary>
          <p class="t-base muted">{html.escape(a)}</p>
        </details>'''
    for q, a in FAQ
)
faq_ld = json.dumps(
    {"@context": "https://schema.org", "@type": "FAQPage",
     "mainEntity": [{"@type": "Question", "name": q,
                     "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]},
    ensure_ascii=False, indent=2)

LD = json.dumps({
    "@context": "https://schema.org", "@type": "WebSite",
    "name": "aiprice", "alternateName": "AI 订阅实时比价",
    "url": "https://aipriceio.github.io/",
    "description": "ChatGPT、Claude、Gemini、Grok 全网卡密店铺在售报价实时比价。",
    "inLanguage": ["zh-CN", "zh-TW", "en", "ja"],
    "sameAs": [SITE],
}, ensure_ascii=False, indent=2)

TAGLINE = "同一个会员，不同店铺之间的差价，常常超过一倍。"
words = "".join(
    f'<span class="w">{html.escape(ch)}</span>' if ch not in "，。" else f'<span class="w p">{html.escape(ch)}</span>'
    for ch in TAGLINE
)

TPL = open(os.path.join(HERE, "template.html"), encoding="utf-8").read()
replacements = {
    "@@CARDS@@": "\n".join(cards),
    "@@ROWS@@": "\n".join(rows),
    "@@FAQ@@": faq_html,
    "@@FAQ_LD@@": faq_ld,
    "@@LD@@": LD,
    "@@TAGLINE@@": words,
    "@@OFFERS@@": f"{offers_total:,}",
    "@@INSTOCK@@": f"{instock_total:,}",
    "@@STORES@@": f"{store_n}",
    "@@PRODUCTS@@": f"{len(products)}",
    "@@GEN@@": gen_label,
    "@@REF@@": REF,
    "@@SITE@@": SITE,
}
page = TPL
for k, v in replacements.items():
    page = page.replace(k, v)

os.makedirs(OUT, exist_ok=True)
open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(page)

nf = open(os.path.join(HERE, "404.html"), encoding="utf-8").read()
open(os.path.join(OUT, "404.html"), "w", encoding="utf-8").write(nf)

open(os.path.join(OUT, "robots.txt"), "w").write(
    "User-agent: *\nAllow: /\nSitemap: https://aipriceio.github.io/sitemap.xml\n")
open(os.path.join(OUT, "sitemap.xml"), "w").write(
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    f'  <url><loc>https://aipriceio.github.io/</loc><lastmod>{gen.strftime("%Y-%m-%d")}</lastmod>'
    '<changefreq>daily</changefreq><priority>1.0</priority></url>\n'
    '</urlset>\n')
open(os.path.join(OUT, ".nojekyll"), "w").write("")

print("built", os.path.join(OUT, "index.html"), len(page), "bytes")
print(f"offers={offers_total} instock={instock_total} stores={store_n} products={len(products)} gen={gen_label}")
