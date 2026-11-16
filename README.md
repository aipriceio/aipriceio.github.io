# aipriceio.github.io

aiprice 的官方推广页，纯静态，部署在 GitHub Pages。

## 内容

- `index.html`：落地页（主流四家最低价 / 使用流程 / 热门 12 个商品 / 常见问题）
- `404.html`：品牌化 404
- `og.png`、`favicon.svg`：社交分享图与站点图标
- `robots.txt`、`sitemap.xml`：搜索引擎入口

页面里的价格和商品列表来自 [aiprice.io](https://aiprice.io) 的公开快照，构建时写入，不在浏览器端请求接口（上游未开放跨域）。

## 更新

```bash
# 拉最新快照后重新生成
curl -s https://aiprice.io/data/radar.json -o radar.json
python3 build.py
```

`build.py` 读 `radar.json`，套 `template.html`，输出到 `site/`。改文案改 `template.html`，改结构或数据口径改 `build.py`。

## 归因

所有外链都带 `?ch=gh-aipriceio`，在 aiprice 的推广中心「来源明细」里可以看到这一组渠道带来的访问和跳转。

## 说明

本站不卖卡、不收款、不设置 Cookie，交易一律在店铺自己的网站上完成。
