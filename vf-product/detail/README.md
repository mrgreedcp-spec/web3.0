# VF 果蔬脆 · 电商详情页长图

- `detail.html`：详情页源文件，宽 750px（淘宝、天猫、京东手机端通用）。
- `export.js`：导出脚本，生成整张长图和按模块切好的切片。
- `out/detail-full.jpg`：整张长图，750 × 约 13000px。
- `out/slices/01–11.jpg`：按模块切好的切片，每张高度不超过 1500px，可以直接逐张上传到详情页编辑器。

## 模块顺序
01 首屏海报 · 02 高温/低温对比 · 03 原理（温度计） · 04 卖点：原色原味 · 05 卖点：酥脆多孔
06 六道工序 · 07 口味系列 · 08 食用场景 · 09 产品信息表 · 10 买前问答 · 11 品牌承诺

## 替换素材后重新导出
1. 打开 `detail.html`，替换所有【】占位文字。
2. 把 `<div class="ph ...">产品图</div>` 这类占位块换成实拍图，例如
   `<img src="img/xxx.jpg" style="width:100%;height:100%;object-fit:cover;border-radius:inherit">`。
3. 运行下面的命令重新导出：`node vf-product/detail/export.js`
   （需要先装好 Node 和 Playwright。如果平台要求 790px 宽，把 `detail.html` 里的 `--w` 和 `export.js` 里的 `WIDTH` 一起改掉即可。）
