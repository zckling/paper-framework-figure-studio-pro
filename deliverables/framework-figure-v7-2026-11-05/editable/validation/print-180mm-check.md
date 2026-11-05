# 180 mm 印刷尺度检查

实际 PDF 页面：180.0 × 130.5 mm；300 dpi 预览见 print-180mm-300dpi.png。

font_pt = canvas_font_px × (180 mm / 2000 canvas units) × 72 pt/in ÷ 25.4 mm/in

| 关键标签 | 画布字号 | 180 mm 时字号 |
|---|---:|---:|
| Support set S | 25.0 | 6.38 pt |
| 2K labeled
images | 26 | 6.63 pt |
| CLIP ViT-L/14 | 26 | 6.63 pt |
| blocks 1–12 | 26 | 6.63 pt |
| CLIP ViT-L/14 | 26 | 6.63 pt |
| blocks 1–24 | 26 | 6.63 pt |
| Query-conditioned
prototype mixing | 26 | 6.63 pt |
| Cosine similarity
difference | 26 | 6.63 pt |
| Probability average | 26 | 6.63 pt |
| p(x) = ½[pₚ(q) + pᵥ(x)] | 26 | 6.63 pt |
| Class-wise softmax | 26 | 6.63 pt |
| Weighted sum | 26 | 6.63 pt |
| Mix → L₂ norm | 26 | 6.63 pt |
| L₂ norm | 26 | 6.63 pt |
| L₂ norm | 26 | 6.63 pt |
| 1–6 | 26 | 6.63 pt |
| 19–24 | 26 | 6.63 pt |
| q ∈ ℝ¹⁰²⁴ | 26 | 6.63 pt |
| v(x) ∈ ℝ⁷⁶⁸ | 26 | 6.63 pt |
| pₚ(q) | 27 | 6.89 pt |
| pᵥ(x) | 27 | 6.89 pt |
| CLS
readout
project
L₂ norm | 25 | 6.38 pt |
| Backprop through frozen encoder | 25 | 6.38 pt |
| Update
prompts only | 26 | 6.63 pt |

检查结论：关键编码器、方法模块、操作、阶段号、q/v维度、概率、CLS读出和梯度标签均达到至少25画布字号（180mm时6.38pt），多数为26（6.63pt），pₚ/pᵥ为27（6.89pt）。已检查无文字/箭头碰撞；小数学下标和辅助边注保留较小字号。

辅助说明已外移到 caption.md，包括相同预训练权重、独立前向、两个P*为同一状态、训练S/推理15、四组联合优化。关键梯度链在图中直接展示为CE→cosine logits→冻结encoder→P，且仅梯度使用虚线。
