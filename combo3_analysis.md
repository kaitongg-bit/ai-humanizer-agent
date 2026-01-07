# 组合拳3设计 - 学习组合拳1的成功经验

## 组合拳1的成功分析

### 组合拳1的7步策略
1. **autofix** - 模拟非母语者，插入语法错误
2. **cross_trans** - 中英互译
3. **personalize** - 添加个人色彩
4. **depersonalize** - 减少过度个人化
5. **cross_trans** - 再次中英互译
6. **苹果翻译** - 中→英（外部工具）
7. **谷歌翻译** - 中→英→中（外部工具）

### 成功的关键

#### 1. 多次cross_trans ⭐⭐⭐⭐⭐
- 步骤2和步骤5都用了cross_trans
- **作用**: 每次中英互译都会打乱语言模式
- **效果**: GPTZero从100%降到23.6%

#### 2. personalize + depersonalize的平衡 ⭐⭐⭐⭐
- 先加个人色彩，再去除过度的
- **作用**: 增加自然度，但保持正式性
- **效果**: 避免AI的机械感，同时保持学术性

#### 3. autofix的语法错误 ⭐⭐⭐
- 模拟非母语者，插入语法错误
- **作用**: 打破AI的完美语法
- **效果**: 增加真实感

#### 4. 外部翻译工具的加持 ⭐⭐⭐⭐⭐
- 苹果翻译和谷歌翻译
- **作用**: 进一步打乱AI模式
- **效果**: 从20%降到10%

---

## 我之前的问题

### 组合拳2（迭代1-5）的不足

1. ❌ **步骤太少**：只有3步
2. ❌ **缺少多次cross_trans**：只用了1次
3. ❌ **没有personalize + depersonalize**：缺少个人化平衡
4. ❌ **没有autofix**：没有语法错误模拟
5. ❌ **GPTZero还在72%**：远高于目标30%

---

## 组合拳3设计

### 设计思路

**核心策略**: 结合组合拳1的成功经验 + 我发现的basic_rewrite优势

**目标**:
- ZeroGPT < 5%
- GPTZero < 30%

### 新组合拳（7步）

| 步骤 | 提示词 | LLM | 模型 | 目的 |
|------|--------|-----|------|------|
| 1 | simplify | GPT | gpt-4.1-mini | 简化句式，为后续打基础 |
| 2 | basic_rewrite | Gemini | gemini-2.5-flash | 降ZeroGPT（核心步骤） |
| 3 | cross_trans | Gemini | gemini-2.5-flash | 第1次中英互译，打乱语言模式 |
| 4 | personalize | GPT | gpt-4.1-mini | 添加个人色彩，增加自然度 |
| 5 | depersonalize | Gemini | gemini-2.5-flash | 去除过度个人化，保持正式性 |
| 6 | cross_trans | Gemini | gemini-2.5-flash | 第2次中英互译，进一步打乱 |
| 7 | autofix | Gemini | gemini-2.5-flash | 模拟非母语者，插入语法错误 |

### 为什么这样设计？

#### 1. 保留成功的basic_rewrite
- **证据**: 所有迭代中basic_rewrite都能降ZeroGPT 85-98%
- **位置**: 放在第2步，早期降低ZeroGPT

#### 2. 两次cross_trans（学习组合拳1）
- **证据**: 组合拳1用了2次cross_trans，GPTZero降到23.6%
- **位置**: 第3步和第6步，分别在personalize前后

#### 3. personalize + depersonalize（学习组合拳1）
- **证据**: 组合拳1用这个组合平衡个人化
- **位置**: 第4-5步，在两次cross_trans之间

#### 4. autofix放在最后（学习组合拳1）
- **证据**: 组合拳1的autofix在前期，但我迭代3发现autofix让ZeroGPT飙升
- **策略**: 放在最后，在ZeroGPT已经很低的情况下，用autofix增加真实感

#### 5. simplify作为铺垫
- **证据**: 我的测试中simplify为basic_rewrite打基础
- **位置**: 第1步

---

## 预期效果

### 各步骤预期

| 步骤 | ZeroGPT | GPTZero | 分析 |
|------|---------|---------|------|
| 0. 原文 | 99.99% | 99.79% | - |
| 1. simplify | ~100% | ~99.8% | 略微变化 |
| 2. basic_rewrite | **~1-5%** | ~100% | ✅ ZeroGPT暴降 |
| 3. cross_trans | ~2-8% | **~70-80%** | ✅ GPTZero开始降 |
| 4. personalize | ~10-20% | ~65-75% | ⚠️ ZeroGPT可能略升 |
| 5. depersonalize | ~5-15% | ~60-70% | ✅ 平衡个人化 |
| 6. cross_trans | ~5-15% | **~30-50%** | ✅✅ GPTZero继续降 |
| 7. autofix | **~3-10%** | **~25-40%** | ✅ 增加真实感 |

### 最终目标

- **ZeroGPT**: < 10%
- **GPTZero**: < 40%（理想<30%）
- **综合得分**: < 35（比迭代1的51.70好很多）

---

## Manus的30字分析

**为什么选择这个组合？**

"学习组合拳1的成功经验：两次cross_trans打乱语言模式，personalize+depersonalize平衡自然度，basic_rewrite降ZeroGPT，autofix增加真实感。7步策略，目标两项都<30%。"

---

## 与组合拳1的对比

| 维度 | 组合拳1 | 组合拳3 | 说明 |
|------|---------|---------|------|
| 步骤数 | 7步（5步prompt + 2步外部翻译） | 7步（全prompt） | 相同长度 |
| cross_trans | 2次 | 2次 | ✅ 学习 |
| personalize+depersonalize | ✅ | ✅ | ✅ 学习 |
| autofix | 第1步 | 第7步 | ⚠️ 调整位置 |
| basic_rewrite | ❌ | ✅ | ✅ 我的发现 |
| 外部翻译 | ✅ | ❌ | 暂不使用 |

---

## 风险和备选方案

### 风险1: autofix可能让ZeroGPT飙升
- **证据**: 迭代3中autofix让ZeroGPT从3.40%升到100%
- **缓解**: 放在最后，此时ZeroGPT已经很低
- **备选**: 如果失败，去掉autofix

### 风险2: personalize可能让ZeroGPT升高
- **证据**: 迭代4中personalize让ZeroGPT从1.32%升到20.71%
- **缓解**: 紧接着用depersonalize平衡
- **备选**: 如果失败，调整personalize的强度

### 风险3: 7步可能太长，成本高
- **缓解**: 如果效果好，可以后续简化
- **备选**: 找到最有效的步骤，去掉冗余

---

## 下一步

立即执行组合拳3测试！
