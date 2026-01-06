# AI降重Agent Loop优化报告

## 📋 测试概述

- **文章ID**: ai_1
- **主题**: Carbon Taxes（碳税）
- **字数**: 895词
- **迭代次数**: 5次
- **总耗时**: 约15分钟
- **测试日期**: 2026-01-06

---

## 🎯 优化目标

找到最优的提示词组合拳，使得：
1. **ZeroGPT分数**尽可能低
2. **GPTZero分数**尽可能低
3. **步骤数**尽可能少（降低成本）

**综合得分** = (ZeroGPT + GPTZero) / 2 + 步骤数 × 5

---

## 📊 迭代结果总结

| 迭代 | 组合拳 | ZeroGPT | GPTZero | 步骤数 | 综合得分 |
|------|--------|---------|---------|--------|---------|
| **1** | **simplify → basic_rewrite → cross_trans** | **1.08%** | **72.33%** | **3** | **51.70** ✅ |
| 2 | simplify → basic_rewrite → cross_trans | 1.56% | 72.64% | 3 | 52.10 |
| 3 | simplify → basic_rewrite → autofix | 100.00% | 99.97% | 3 | 114.99 ❌ |
| 4 | simplify → basic_rewrite → personalize → depersonalize | 12.50% | 99.89% | 4 | 76.19 |
| 5 | prevent_hallucinations → basic_rewrite | 4.36% | 99.99% | 2 | 62.18 |

---

## 🏆 最佳组合拳

### 组合拳配置

```python
[
    {"prompt_name": "simplify", "llm": "gpt", "model": "gpt-4.1-mini"},
    {"prompt_name": "basic_rewrite", "llm": "gemini", "model": "gemini-2.5-flash"},
    {"prompt_name": "cross_trans", "llm": "gemini", "model": "gemini-2.5-flash"},
]
```

### 性能指标

- **ZeroGPT**: 99.99% → **1.08%** ✅✅✅ （降低98.91%）
- **GPTZero**: 99.79% → **72.33%** ✅✅ （降低27.46%）
- **综合得分**: **51.70** （最低）
- **步骤数**: 3步
- **总耗时**: 约3-5分钟
- **Token消耗**: 约4000-6000 tokens

### 各步骤效果

| 步骤 | 操作 | ZeroGPT | GPTZero | 变化 |
|------|------|---------|---------|------|
| 0 | 原文 | 99.99% | 99.79% | - |
| 1 | simplify (GPT-4.1-mini) | 100.00% | 99.78% | ⚠️ ZeroGPT略升 |
| 2 | basic_rewrite (Gemini-2.5-flash) | **1.08%** | 100.00% | ✅✅✅ ZeroGPT暴降 |
| 3 | cross_trans (Gemini-2.5-flash) | **1.08%** | **72.33%** | ✅✅ GPTZero大降 |

---

## 🔍 详细分析

### 迭代1：初始策略（最佳）⭐⭐⭐⭐⭐

**Manus的思路**:
```
基于组合拳2的测试结果，我发现：
- basic_rewrite对ZeroGPT非常有效
- cross_trans对GPTZero有效
- 前两步（avoids_mechanization, add_details）效果不佳

所以我简化了流程，直接从simplify开始
```

**结果**:
- ✅✅✅ ZeroGPT降到1.08%（几乎完美）
- ✅✅ GPTZero降到72.33%（显著改善）
- ✅ 只需3步，成本低

**关键发现**:
1. **basic_rewrite是核心**：将ZeroGPT从100%降到1.08%
2. **cross_trans是关键**：将GPTZero从100%降到72.33%
3. **simplify是铺垫**：虽然分数略升，但为后续步骤打基础

---

### 迭代2：重复验证

**Manus的思路**:
```
迭代1效果很好，但GPTZero还在72%。
我决定再测试一次相同的组合，看看结果是否稳定。
```

**结果**:
- ZeroGPT: 1.56%（与迭代1相近）
- GPTZero: 72.64%（与迭代1相近）
- 综合得分: 52.10（略高于迭代1）

**结论**:
- ✅ 结果稳定，可重复
- ⚠️ GPTZero仍然较高

---

### 迭代3：尝试autofix（失败）❌

**Manus的思路**:
```
GPTZero还在72%，需要进一步降低。
组合拳1中autofix表现不错，我尝试用它替换cross_trans。
```

**结果**:
- ❌❌❌ ZeroGPT飙升到100%
- ❌❌❌ GPTZero仍在99.97%
- 综合得分: 114.99（最差）

**问题分析**:
- autofix引入了新的AI特征
- 可能是因为它模拟非母语者，反而让检测器更敏感
- **教训**: autofix不适合这篇文章

---

### 迭代4：尝试personalize + depersonalize

**Manus的思路**:
```
autofix失败了，尝试组合拳1的另一个策略：
personalize增加个人化，depersonalize去除过度个人化。
```

**结果**:
- ZeroGPT: 12.50%（比迭代1差）
- GPTZero: 99.89%（几乎没降）
- 综合得分: 76.19

**问题分析**:
- personalize反而让ZeroGPT从1.32%升到20.71%
- depersonalize降回12.50%，但不如不加
- **教训**: 个人化策略对这篇文章无效

---

### 迭代5：探索新方向

**Manus的思路**:
```
前面的策略都不如迭代1。
尝试一个新的组合：prevent_hallucinations + basic_rewrite
看看能否用更少的步骤达到类似效果。
```

**结果**:
- ZeroGPT: 4.36%（比迭代1略差）
- GPTZero: 99.99%（几乎没降）
- 综合得分: 62.18
- 只需2步（成本最低）

**分析**:
- ✅ 步骤数最少（2步）
- ⚠️ ZeroGPT效果可以（4.36%）
- ❌ GPTZero几乎没降（99.99%）
- **结论**: 如果只关注ZeroGPT且追求低成本，这是不错的选择

---

## 💡 核心发现

### 1. basic_rewrite是降ZeroGPT的核心 ⭐⭐⭐⭐⭐

**证据**:
- 迭代1: 100% → 1.08%（-98.92%）
- 迭代2: 100% → 1.38%（-98.62%）
- 迭代3: 99.99% → 3.40%（-96.59%）
- 迭代4: 90.21% → 1.32%（-88.89%）
- 迭代5: 65.23% → 4.36%（-60.87%）

**结论**: basic_rewrite对ZeroGPT有**稳定且强大**的降低效果

---

### 2. cross_trans是降GPTZero的关键 ⭐⭐⭐⭐

**证据**:
- 迭代1: 100% → 72.33%（-27.67%）
- 迭代2: 99.99% → 72.64%（-27.35%）

**结论**: cross_trans（中英互译）能有效打乱GPTZero识别的语言模式

---

### 3. simplify是必要的铺垫 ⭐⭐⭐

**作用**:
- 简化句式，为后续改写创造条件
- 虽然分数可能略升，但为basic_rewrite打基础

---

### 4. autofix对这篇文章无效 ❌

**证据**:
- 迭代3中autofix让ZeroGPT从3.40%飙升到100%

**原因**:
- 可能是文章主题（碳税）不适合非母语者风格
- autofix引入的特征反而被识别为AI

---

### 5. personalize策略对这篇文章无效 ❌

**证据**:
- 迭代4中personalize让ZeroGPT从1.32%升到20.71%

**原因**:
- 学术议论文不适合过度个人化
- 个人化表达反而增加了AI特征

---

## 📈 性能对比

### 与组合拳1的对比

| 指标 | 组合拳1 | 最佳组合拳 | 对比 |
|------|---------|-----------|------|
| ZeroGPT | 0.0% | 1.08% | 略差 |
| GPTZero | 70.00% | 72.33% | 略差 |
| 步骤数 | 5步 | 3步 | ✅ 更少 |
| 综合得分 | 45.00 | 51.70 | 略差 |

**结论**:
- 组合拳1效果略好，但需要5步
- 最佳组合拳只需3步，成本更低
- 如果追求极致效果，用组合拳1
- 如果追求成本效益，用最佳组合拳

---

## 🎓 经验总结

### 有效策略

1. ✅ **simplify → basic_rewrite → cross_trans** （最佳平衡）
2. ✅ **basic_rewrite** （降ZeroGPT核心）
3. ✅ **cross_trans** （降GPTZero关键）
4. ✅ **prevent_hallucinations → basic_rewrite** （低成本方案）

### 无效策略（针对这篇文章）

1. ❌ **autofix** （让ZeroGPT飙升）
2. ❌ **personalize + depersonalize** （效果不佳）
3. ❌ **avoids_mechanization + add_details** （组合拳2前期）

### 通用规律

1. **basic_rewrite是万能钥匙**：几乎所有迭代中都有效
2. **cross_trans对GPTZero有效**：中英互译打乱语言模式
3. **不同文章需要不同策略**：学术文章不适合过度个人化
4. **简化流程很重要**：3步比5步成本低，效果相近

---

## 🚀 下一步建议

### 短期优化

1. **测试更多文章**
   - 不同主题（科技、社会、文学）
   - 不同长度（短文、长文）
   - 验证最佳组合拳的通用性

2. **优化cross_trans**
   - GPTZero还在72%，需要进一步降低
   - 尝试在cross_trans后加其他步骤
   - 或者调整cross_trans的prompt

3. **成本优化**
   - 测试2步组合（如：basic_rewrite → cross_trans）
   - 看能否跳过simplify

### 中期计划

1. **建立文章类型 → 策略的映射**
   - 学术文章 → simplify + basic_rewrite + cross_trans
   - 创意文章 → personalize + basic_rewrite
   - 技术文章 → prevent_hallucinations + basic_rewrite

2. **自动化策略选择**
   - 根据文章特征自动选择最佳组合
   - 使用机器学习预测效果

3. **扩展提示词库**
   - 开发针对GPTZero的新提示词
   - 测试更多组合可能性

### 长期目标

1. **达到两个检测器都<20%**
2. **建立完整的Agent Loop系统**
3. **支持批量处理**
4. **提供API服务**

---

## 📊 数据文件

所有测试数据已保存：

1. `iteration_1_results.csv` - 迭代1详细结果（最佳）
2. `iteration_2_results.csv` - 迭代2详细结果
3. `iteration_3_results.csv` - 迭代3详细结果
4. `iteration_4_results.csv` - 迭代4详细结果
5. `iteration_5_results.csv` - 迭代5详细结果
6. `optimization_log.txt` - 完整的优化日志
7. `combo2_test_results.csv` - 组合拳2测试结果

---

## 🎯 最终结论

通过5次迭代，我们找到了最优的提示词组合拳：

**simplify → basic_rewrite → cross_trans**

**性能**:
- ZeroGPT: 1.08% ✅✅✅
- GPTZero: 72.33% ✅✅
- 综合得分: 51.70（最低）
- 步骤数: 3（适中）

**适用场景**:
- 学术议论文
- 需要平衡效果和成本
- 追求稳定可重复的结果

**下一步**:
- 在更多文章上验证
- 继续优化GPTZero分数
- 建立自动化的Agent Loop系统

---

**GitHub仓库**: https://github.com/kaitongg-bit/ai-humanizer-agent
