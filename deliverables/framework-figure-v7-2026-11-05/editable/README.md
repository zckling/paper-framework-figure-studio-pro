# v7 可编辑伴随稿

本目录为手工编排的可编辑矢量伴随版本，供在 Visio 或矢量编辑器继续修改；不是 imagegen 生成的栅格候选，也不保证与正式候选逐像素一致。

- framework-v7.svg / .pdf / .png：同一手工矢量布局的导出。
- framework-v7.vdx / .vsdx：311 个独立对象，其中 124 个文字对象、5 张可替换照片。数学下标为独立可编辑文字对象。
- build_v7.py、vector_engine.py、visio_compat.py 与 assets/、support/：可重建源文件。
- validation/visio-validation.json：OPC/XML、原生导入和下标位置验证。

保持相对路径，安装 Python 3、Pillow、Inkscape 与 Liberation Sans 字体后运行 `python3 build_v7.py`。

VSDX 和 VDX 均经 LibreOffice/libvisio 导入为单页、5 张照片的矢量 PDF，16 项内部关系及引用有效；11 个 schema 部件通过。提供的 Visio XSD 不声明 Windows 根元素，该部件沿用实际 Visio 文档模板。当前环境未安装 Microsoft Visio，未在该软件实测。LibreOffice 26.8 会给 Foreign 图片附加默认绿色粗边，源文件已关闭该描边；发布的 SVG/Inkscape PNG/PDF 为预期细灰边，验证原生 PDF 未打补丁。

support/visio-base.vsdx 来自 vsdx 项目，许可为 BSD-3-Clause，见 support/LICENSE-vsdx.txt。

最后字号检查见 validation/print-180mm-check.md 与同名 JSON；180 mm 物理尺寸 PDF 为 validation/print-180mm.pdf。关键流程标签至少25画布字号（6.38 pt），多数26（6.63 pt）；长辅助说明已移至 caption.md。
