# 180 mm 版面字号检查

物理PDF：180.0 × 127.8 mm。

主要标签43组：8.164–9.057 pt；辅助标签62组：最小7.143 pt。

主要标签≥8pt：True；辅助基字号≥7pt：True。

数学下标保留自然缩小，未把下标字号当作独立辅助正文。所有普通文字基字号均纳入检查。

| 标签 | 类型 | 180 mm 字号 | 结果 |
|---|---|---:|---|
| (a) Overview | main | 9.057 pt | PASS |
| Support-set adaptation | main | 8.674 pt | PASS |
| Once per support set | auxiliary | 7.143 pt | PASS |
| Labeled source<br>support 𝒮 | main | 8.164 pt | PASS |
| 2K images | main | 8.164 pt | PASS |
| K real | auxiliary | 7.143 pt | PASS |
| … | auxiliary | 7.654 pt | PASS |
| K fake | auxiliary | 7.143 pt | PASS |
| … | auxiliary | 7.654 pt | PASS |
| Trainable<br>P | main | 8.164 pt | PASS |
| Four prompt groups<br>2 tokens per stage | auxiliary | 7.143 pt | PASS |
| CLIP ViT-L/14 | main | 8.164 pt | PASS |
| blocks 1–24 | main | 8.164 pt | PASS |
| image feature | auxiliary | 7.143 pt | PASS |
| Cosine logits | main | 8.164 pt | PASS |
| Native scale S | auxiliary | 7.143 pt | PASS |
| Fixed t₀, t₁ | auxiliary | 7.143 pt | PASS |
| CE | main | 8.674 pt | PASS |
| y | auxiliary | 8.674 pt | PASS |
| Gradients through frozen backbone; update P only | auxiliary | 7.143 pt | PASS |
| Save P* | main | 8.164 pt | PASS |
| 8,192 parameters<br>optimized on support | auxiliary | 7.654 pt | PASS |
| CLIP ViT-L/14 | main | 8.164 pt | PASS |
| blocks 1–12 | main | 8.164 pt | PASS |
| CLS<br>L₂ norm | main | 8.164 pt | PASS |
| Support cache | main | 8.61 pt | PASS |
| Support features | auxiliary | 7.143 pt | PASS |
| Class prototypes | auxiliary | 7.143 pt | PASS |
| Query inference · no parameter updates | main | 8.674 pt | PASS |
| Query x | main | 8.674 pt | PASS |
| Real + fakes from<br>unseen generators | auxiliary | 7.143 pt | PASS |
| CLIP ViT-L/14 | main | 8.164 pt | PASS |
| blocks 1–12 | main | 8.164 pt | PASS |
| CLIP ViT-L/14 | main | 8.164 pt | PASS |
| blocks 1–24 | main | 8.164 pt | PASS |
| CLS<br>L₂ norm | main | 8.164 pt | PASS |
| q ∈ ℝ¹⁰²⁴ | main | 8.164 pt | PASS |
| Query-conditioned<br>prototype mixing | main | 8.164 pt | PASS |
| (b) | auxiliary | 7.143 pt | PASS |
| Fixed P* | main | 8.164 pt | PASS |
| Load P* | main | 8.164 pt | PASS |
| (c) | auxiliary | 7.143 pt | PASS |
| v(x) ∈ ℝ⁷⁶⁸ | main | 8.164 pt | PASS |
| Cosine difference | main | 8.164 pt | PASS |
| vᵀt₁ − vᵀt₀ | auxiliary | 8.164 pt | PASS |
| Fixed t₀, t₁ | auxiliary | 7.143 pt | PASS |
| ×γ → σ | auxiliary | 7.143 pt | PASS |
| Probability<br>average | main | 8.164 pt | PASS |
| p(x) > 0.5: Fake | main | 8.164 pt | PASS |
| (b) Prototype mixing | main | 8.674 pt | PASS |
| q=f₁₂(x), ‖q‖₂=1 | auxiliary | 7.143 pt | PASS |
| Within-class<br>weighting | main | 8.164 pt | PASS |
| Weighted sum | main | 8.164 pt | PASS |
| Mix → L₂ norm | main | 8.164 pt | PASS |
| q | auxiliary | 8.164 pt | PASS |
| Real | auxiliary | 7.143 pt | PASS |
| Σ | auxiliary | 8.164 pt | PASS |
| m₀(q) | auxiliary | 7.654 pt | PASS |
| 0.5 | auxiliary | 7.143 pt | PASS |
| μ₀ | auxiliary | 7.654 pt | PASS |
| 0.5 | auxiliary | 7.143 pt | PASS |
| + | auxiliary | 8.164 pt | PASS |
| L₂ norm | main | 8.164 pt | PASS |
| μ̃₀(q) | auxiliary | 7.654 pt | PASS |
| Fake | auxiliary | 7.143 pt | PASS |
| Σ | auxiliary | 8.164 pt | PASS |
| m₁(q) | auxiliary | 7.654 pt | PASS |
| 0.5 | auxiliary | 7.143 pt | PASS |
| μ₁ | auxiliary | 7.654 pt | PASS |
| 0.5 | auxiliary | 7.143 pt | PASS |
| + | auxiliary | 8.164 pt | PASS |
| L₂ norm | main | 8.164 pt | PASS |
| μ̃₁(q) | auxiliary | 7.654 pt | PASS |
| (c) Stage-wise prompt replacement | main | 8.674 pt | PASS |
| Frozen CLIP backbone | auxiliary | 7.143 pt | PASS |
| P₁* | auxiliary | 7.143 pt | PASS |
| 1–6 | main | 8.164 pt | PASS |
| P₂* | auxiliary | 7.143 pt | PASS |
| 7–12 | main | 8.164 pt | PASS |
| P₃* | auxiliary | 7.143 pt | PASS |
| 13–18 | main | 8.164 pt | PASS |
| P₄* | auxiliary | 7.143 pt | PASS |
| 19–24 | main | 8.164 pt | PASS |
| CLIP CLS readout<br>768-D · normalized | main | 8.164 pt | PASS |
| CLS + image tokens continue | auxiliary | 7.143 pt | PASS |
| Output tokens | auxiliary | 7.143 pt | PASS |
| Drop prompt states | auxiliary | 7.143 pt | PASS |
| Insert Pₛ₊₁* | auxiliary | 7.143 pt | PASS |
| CLS · state · image | auxiliary | 7.143 pt | PASS |
| Keep CLS + image | auxiliary | 7.143 pt | PASS |
| Next-stage input | auxiliary | 7.143 pt | PASS |
| Real | auxiliary | 7.654 pt | PASS |
| Fake | auxiliary | 7.654 pt | PASS |
| Prompts | auxiliary | 7.654 pt | PASS |
| Frozen | auxiliary | 7.654 pt | PASS |
| {zci} | auxiliary | 7.654 pt | PASS |
| μc | auxiliary | 8.164 pt | PASS |
| pP(x) | main | 8.674 pt | PASS |
| pV(x) | main | 8.674 pt | PASS |
| p(x) = ½(pP+pV) | auxiliary | 7.143 pt | PASS |
| αci(q) | auxiliary | 7.143 pt | PASS |
| αci(q) | auxiliary | 7.143 pt | PASS |
| αci(q)=softmaxi(β qᵀzci) | auxiliary | 7.143 pt | PASS |
| mc(q) is not normalized before mixing. | auxiliary | 7.143 pt | PASS |
| pP(x)=σ(γ qᵀ(μ̃₁(q)−μ̃₀(q))) | auxiliary | 7.654 pt | PASS |
