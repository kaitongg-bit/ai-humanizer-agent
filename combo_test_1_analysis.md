# 组合拳测试 1 - Manus分析

## 文章信息
- **ID**: ai_1
- **主题**: Carbon Taxes（碳税）
- **字数**: 895词
- **类型**: 学术议论文

## 初步观察（未检测前的分析）

### 文章特征分析
通过阅读文章，我发现以下可能被判定为AI的特征：

1. **段落结构过于工整**
   - 每段都是"Firstly", "Moreover", "However", "Additionally", "Furthermore"等连接词开头
   - 这种机械化的段落过渡是典型的AI特征

2. **句式过于规范**
   - 句子长度相对均匀，缺乏变化
   - 大量使用"This shows that...", "Therefore...", "For example..."等模板句式

3. **论证方式固定**
   - 每段都是：观点 → 例子 → 总结
   - 缺乏个人化的表达和思考

4. **模糊表达较多**
   - "may limit", "might not", "can be", "could be seen"等不确定表达
   - AI倾向于使用这些词来避免过于绝对的判断

## Manus的思考（30字分析）

**为什么这篇文章可能被判为AI？**

"文章使用大量机械化连接词（Firstly, Moreover, However）和模板句式（This shows that, Therefore），段落结构过于工整，缺乏个人化表达，句式变化少。"

## 新组合拳设计

基于以上分析，我设计了一个**与组合拳1完全不同**的新策略：

### 组合拳2：结构打散 + 简化 + 细节增强

**策略思路**：
1. 先打散机械化的结构（去除Firstly, Moreover等）
2. 简化复杂句式，增加句子长度变化
3. 添加具体细节和数据，减少模糊表达
4. 用基础改写去除学术腔

**具体步骤**：

| 步骤 | 提示词 | LLM | 模型 | 目的 |
|------|--------|-----|------|------|
| 1 | avoids_mechanization | GPT | gpt-4.1-mini | 去除机械化连接词和段落结构 |
| 2 | add_details | Gemini | gemini-2.5-flash | 增加具体细节，减少空泛描述 |
| 3 | simplify | GPT | gpt-4.1-mini | 简化句式，增加长度变化 |
| 4 | basic_rewrite | Gemini | gemini-2.5-flash | 拆分长句，替换高频词 |

### 为什么选择这个组合？

1. **与组合拳1的区别**：
   - 组合拳1：autofix → cross_trans → personalize → depersonalize → cross_trans
   - 组合拳2：avoids_mechanization → add_details → simplify → basic_rewrite
   - 完全不同的策略方向！

2. **策略逻辑**：
   - 组合拳1侧重"翻译+个人化"来打乱AI模式
   - 组合拳2侧重"结构重组+细节增强"来改善内容质量

3. **预期效果**：
   - avoids_mechanization会打散机械化结构，可能初期分数会上升
   - add_details会增加具体性，降低AI的空泛感
   - simplify会改善句式，增加自然度
   - basic_rewrite会进一步优化，最终降低分数

4. **模型选择理由**：
   - 结构性任务（avoids_mechanization, simplify）用GPT-4.1-mini（逻辑性强）
   - 创造性任务（add_details, basic_rewrite）用Gemini-2.5-flash（生成能力强）

## 预测

- **ZeroGPT**: 预计从初始的60-80%降到20-30%
- **GPTZero**: 预计从初始的80-95%降到40-60%
- **关键步骤**: add_details和simplify应该会有明显效果

让我们开始测试！
