# 可在 Visio 中修改的框架图

**优先下载 `framework-editable.vsdx`，在桌面版 Visio 中用“文件 → 打开”打开。**

- [Visio 原生文件](framework-editable.vsdx)
- [全部文件 ZIP](framework-editable-package.zip)
- [SVG 矢量备份](framework-editable.svg)
- [PNG 预览](framework-editable-preview.png)

![矢量重建版预览](framework-editable-preview.png)

## 可以修改什么

这是对 v4 草稿的对象级重建。原生 Visio 文件包含 **220 个独立对象，其中 70 个文字对象、47 个线条/连接对象和 7 张嵌入照片**。两个 Encoder 和四个阶段模块均为圆角矩形；雪花、提示 token、特征符号、框线及箭头为矢量几何对象。

- 文字和公式可以直接编辑；公式以文本形式保留。
- 各个框、照片、符号和连线可以分别选择、移动、调整尺寸及样式，无需先取消整图组合。
- 照片保留为独立位图，可以移动、缩放或替换；放大照片不会增加原始像素细节。
- 连线具有独立的形状对象和端点依赖记录。移动模块后请检查折线路径，复杂折线可能仍需手动调整。
- 页面分为 Background panels、Method shapes、Editable text、Connectors、Photographs、Vector symbols 六个层，可在 Visio 的图层属性中管理。
- SVG 中也保留了可编辑文字与几何对象。不同软件导入 SVG 的方式不同，使用 Visio 时优先打开 VSDX。

## 方法内容

只包含 **Query-Conditioned Prototype Mixing（查询条件化原型混合）**和 **Stage-wise Visual Prompting（分阶段视觉提示）**两个方法分支。

同一批支持图像和标签用于两分支：上分支保存支持特征并在 query 到来时按类加权、与全局类中心混合；下分支仅用支持集训练四组阶段提示，每阶段两枚提示，阶段切换时替换，共 8,192 个参数。query 分别进入两条推断路径；最后固定等权平均两路概率。

下分支公式使用等价记法 `Δᵥ = vᵀ(t₁ − t₀)`、`pᵥ = σ(15Δᵥ)`，与 v4 的概率表达一致。没有加入独立静态原型分支。

## 验证与范围

VSDX 已通过 ZIP/XML、关系引用与对象数量检查，并由 LibreOffice 的 Visio 导入器成功加载和导出 PDF；确认文字仍可读取，保留 7 张照片及矢量绘制记录。SVG 已用 Inkscape 渲染检查。

当前环境未运行 Microsoft Visio。请在自己的桌面版 Visio 中检查最终字体与连线路径；独立导入器可能为照片添加自己的默认边框。PNG 预览来自 SVG，展示了预期的中性照片边框。

本文件是方便人工修改的矢量重建稿，不是逐像素追踪，也未进行最终发表验收。原始 v4 PNG 保存在上一级目录。

## 文件与重建

- `framework-editable.vsdx`：Visio 2013 及以后桌面版的原生绘图文件。
- `framework-editable.svg`：自包含 SVG，照片已嵌入，不依赖外部路径。
- `framework-editable-preview.png`：3072 像素宽的渲染预览。
- `assets/`：七张照片，来自 v4 PNG 的局部裁切。
- `framework-editable.scene.json`：对象、样式、文字及布局记录。
- `build_editable.py`：重建 SVG/VSDX 的源脚本；依赖 Python 和 Pillow，字体度量默认使用 Linux 的 Liberation Sans。
- `editability-report.json`：对象统计和验证范围。

运行 `python3 build_editable.py` 可重新生成 SVG、VSDX 与对象记录；PNG 预览可用 Inkscape 从 SVG 导出。日常修改直接在 Visio 中完成即可。
