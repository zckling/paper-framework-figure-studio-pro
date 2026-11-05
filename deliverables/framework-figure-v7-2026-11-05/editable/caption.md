# Suggested paper caption

**Query-conditioned prototype mixing and stage-wise visual prompting.** (a) The same support set, containing K real and K fake labeled images (2K in total), supplies the support cache and prompt adaptation. Both query paths start from the same pretrained CLIP ViT-L/14 weights but use **separate forward passes**. Prompt fitting backpropagates through the cosine logits and frozen image encoder to update only the four prompt groups, jointly. Support-set cross-entropy uses the frozen native scale S = exp(logit_scale); inference uses a fixed scale of 15. The two P* ports denote the same fitted parameter state, loaded without query-time updates. The prototype path reads the normalized 1024-dimensional representation at block 12. The prompted path uses all 24 blocks, followed by CLS readout, projection and normalization to a 768-dimensional vector. (b) Query-conditioned weights are normalized within each class. The weighted aggregate m_c(q) is **not normalized before mixing**: μ̃_c(q) = norm(0.5 μ_c + 0.5 m_c(q)). (c) Each stage preserves CLS and image tokens, discards the updated output prompt states, and inserts the next fitted pair. The first pair is inserted after position embedding and ln_pre. Four pairs of 1024-dimensional tokens give 4×2×1024 = 8,192 jointly optimized parameters. The frozen text anchors are “a real photograph” and “an AI-generated image”.

Inference scores are pₚ(q) = σ(15qᵀ(μ̃₁(q)−μ̃₀(q))) and pᵥ(x) = σ(15v(x)ᵀ(t₁−t₀)); the final probability is p(x) = [pₚ(q)+pᵥ(x)]/2, with p(x)>0.5 predicting fake.

## 从图中外移的辅助信息

相同预训练权重、独立前向、两个 P* 端口指同一状态、训练原生 S 与推理15、四组联合优化以及固定文本内容，统一在论文图注中解释；图中保留闭环、梯度方向、关键机制与得分数据流。
