# Suggested paper caption

**Query-conditioned prototype mixing and stage-wise visual prompting.** (a) The labeled source support set \(\mathcal S\) contains \(K\) real and \(K\) fake images, shared by cache construction and support-only prompt optimization. The same source cache and fitted prompts are reused for all target queries, including real images and fakes from unseen generators; query labels do not participate in adaptation, state selection, or parameter updates. The two frozen CLIP ViT-L/14 paths share pretrained weights but perform separate forward passes. The prototype path extracts the CLS after block 12, **before final LayerNorm and projection**, and applies FP32 \(L_2\) normalization: \(q=f_{12}(x)\) and \(z_{ci}=f_{12}(x_{ci})\) are 1024-dimensional unit vectors. The prompted full-depth path produces a normalized 768-dimensional feature through CLS extraction, final LayerNorm, projection, and \(L_2\) normalization. (b) The support cache stores both \(\{z_{ci}\}\) and the non-learned class prototypes \(\mu_c=\operatorname{norm}(K^{-1}\sum_i z_{ci})\), with \(c=0\) for real and \(c=1\) for fake. Query-dependent weights are normalized separately within each class; line widths illustrate weights only. The weighted aggregate \(m_c(q)\) is **not normalized before mixing** with \(\mu_c\); normalization follows their equal-weight sum. (c) Four prompt groups \(P=\{P_1,P_2,P_3,P_4\}\), each \(P_s\in\mathbb R^{2\times1024}\), are jointly optimized on the source support. At stage boundaries, updated prompt states are discarded and the next fitted pair is inserted, preserving the current CLS and image-token states. The first pair is inserted after position embeddings and input LayerNorm; only two prompt slots exist at any depth. Save/Load \(P^*\) denote the same fitted four-group state, fixed during query inference.

## Definitions and scale convention

\[
\begin{aligned}
f_{12}(x)&=\operatorname{norm}(\operatorname{CLS}_{12}(x)), &q&=f_{12}(x), &z_{ci}&=f_{12}(x_{ci}),\\
\mu_c&=\operatorname{norm}\!\left(\frac1K\sum_i z_{ci}\right), &
\alpha_{ci}(q)&=\operatorname{softmax}_i(\beta q^\top z_{ci}),\\
m_c(q)&=\sum_i\alpha_{ci}(q)z_{ci}, &
\widetilde\mu_c(q)&=\operatorname{norm}\!\left(0.5\mu_c+0.5m_c(q)\right),\\
p_P(x)&=\sigma\!\left(\gamma q^\top(\widetilde\mu_1(q)-\widetilde\mu_0(q))\right), &
p_V(x)&=\sigma\!\left(\gamma[v(x)^\top t_1-v(x)^\top t_0]\right),\\
p(x)&=\frac{p_P(x)+p_V(x)}2.&&
\end{aligned}
\]

The within-class weighting scale \(\beta=15\) and inference scoring scale \(\gamma=15\) are fixed. The symbol \(\gamma\) names the fixed factor 15 already used in the manuscript; it is not an added learned parameter. Support CE instead uses the frozen native CLIP scale \(S=\exp(\mathrm{CLIP.logit\_scale})\approx100\), with logits \(\ell_{ic}=S\,v(x_i)^\top t_c\). Multiplying the native fake-minus-real logit margin by \(\gamma/S\) gives the displayed visual inference score. This fixed scale conversion is not a claim of probability calibration. The fixed unit text anchors encode “a real photograph” and “an AI-generated image”. The probability notation \(p_P(x)\) is the manuscript’s \(p_p(q)\) evaluated at \(q=f_{12}(x)\); \(p_V(x)\) denotes the manuscript’s \(p_v(x)\). Predict fake when \(p(x)>0.5\), otherwise real, including equality.

## 中文图注与边界说明

**查询条件化原型混合与分阶段视觉提示。** 同一带标签源域支持集 \(\mathcal S\) 含 K 张真实图像和 K 张伪造图像，用于构建缓存和联合优化四组提示。缓存与训练后的固定提示在全部目标查询之间共享；未知生成器设定针对伪造查询，查询还包含真实图像。查询标签不用于适配、模型选择或参数更新。两条 CLIP ViT-L/14 路径共享预训练权重，但独立前向。原型路径在第12块后、最终 LayerNorm 与投影前提取 CLS，并在 FP32 中 L₂ 归一化，得到 1024 维的 q 和 z；提示路径的最终 CLS 依次经过最终 LayerNorm、投影和 L₂ 归一化，得到 768 维特征。

缓存中的 μ_c 是支持特征均值归一化后的静态类别方向，由支持样本计算而得，不是 CE 学到的参数，也不是新增独立静态分类分支。每张 query 仍计算自己的类内权重、m_c(q) 和混合方向；“不更新”指模型参数与已学提示不更新，不表示查询条件化读出被固定。线宽仅示意权重大小。m_c(q) 混合前不再次归一化，混合后才归一化。

P 由四组 2×1024 提示组成，共8192参数，通过同一支持集CE联合优化；P*是训练结束时的同一组参数状态。阶段边界丢弃的是经过计算后的提示状态，保留当前CLS/图像token，再插入下一组固定提示，任何深度都只有两个额外提示槽位。首次插入在位置嵌入与ln_pre之后。图中只展开一个边界，其规则适用于其他边界。

β用于类内权重、γ用于推理评分，均固定为15；支持集训练采用冻结的原生CLIP尺度S=exp(logit_scale)，视觉分数在融合前等价地按γ/S缩放。图中p_P(x)、p_V(x)统一以图像为输入；p_P(x)对应原文p_p(q(x))。p>0.5判伪造，其余判真实。具体未知生成器名单及其与源域的不重叠关系仍应由论文实验表给出，本图遵循作者本轮指定的跨生成器协议。
