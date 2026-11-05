# v8 可编辑主图

本轮保留总览与两个机制面板，补齐查询 CLS/L₂归一化、源域支持/未知生成器查询/无参数更新协议、支持特征与类别原型、四组提示与固定状态，并删去重复提示替换解释。

- [查看全图](framework-v8.png)
- [SVG](framework-v8.svg) · [矢量 PDF](framework-v8.pdf)
- [VDX](framework-v8.vdx) · [VSDX](framework-v8.vsdx)
- [英文图注、公式定义与中文说明](caption.md)
- [180 mm 字号检查](validation/print-180mm-check.md)
- [Visio 格式结构及导入检查](validation/visio-validation.json)

这是按已确认规格单独编排的可编辑矢量主稿，不是对 image_gen 栅格预览的逐像素矢量化。框、连线、符号和文字均可分别修改，5 张照片保留为可替换位图。公式下标使用独立小文字对象，以稳定跨软件位置。

当前环境没有 Microsoft Visio，未在其本机实测。VSDX 使用完整的 Visio 文档骨架，另外提供 VDX 和 SVG；建议先尝试 VDX，成功后另存 VSDX。原生导入用 LibreOffice/libvisio 验证，不等同于 Microsoft Visio 兼容性保证。LibreOffice26.8的图像导入器会给照片附加默认绿色边框，源文件已明确关闭该描边；发布的SVG/Inkscape PDF/PNG保留预期细灰边，验证PDF不作修图。

使用 Python3、Pillow、Inkscape 和 Liberation Sans 字体，保持 assets/、support/ 相对位置后运行 `python3 build_v8.py` 可重建。检查脚本在validation/，需要lxml、PyMuPDF以及Visio/OPC schema文件。native schema文件不声明Windows根，故该部件的schema验证属于覆盖限制，保留模板并检查XML/引用。

support/visio-base.vsdx 许可为BSD-3-Clause，见support/LICENSE-vsdx.txt。
