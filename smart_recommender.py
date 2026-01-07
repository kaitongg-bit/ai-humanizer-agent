"""
智能提示词推荐系统
根据文章特征和当前AI检测分数，推荐最适合的提示词组合
"""

import re
from typing import Dict, List, Tuple


class SmartRecommender:
    def __init__(self):
        # 提示词效果数据库（基于测试结果）
        self.prompt_effects = {
            "basic_rewrite": {
                "zerogpt_change": -90,  # 平均降低90%
                "gptzero_change": 0,
                "reliability": 0.95,  # 可靠性
                "适用文章类型": ["academic_argument", "technical", "creative_narrative", "informal"],
            },
            "cross_trans": {
                "zerogpt_change": -2,
                "gptzero_change": -28,  # 第1次平均降低28%
                "reliability": 0.90,
                "适用文章类型": ["academic_argument", "technical", "creative_narrative", "informal"],
            },
            "simplify": {
                "zerogpt_change": 0,
                "gptzero_change": 0,
                "reliability": 1.0,
                "适用文章类型": ["academic_argument", "technical"],
                "作用": "铺垫，为后续步骤创造条件",
            },
            "personalize": {
                "zerogpt_change": 80,  # 危险！会让ZeroGPT飙升
                "gptzero_change": 5,
                "reliability": 0.1,
                "适用文章类型": [],  # 对学术文章有害
                "警告": "对学术议论文有害，会让ZeroGPT飙升80%+",
            },
            "depersonalize": {
                "zerogpt_change": 0,
                "gptzero_change": -20,  # 在personalize之后有效
                "reliability": 0.5,
                "适用文章类型": [],
                "警告": "单独使用可能让GPTZero升高，需要personalize配合",
            },
            "autofix": {
                "zerogpt_change": 0,
                "gptzero_change": 0,
                "reliability": 0.3,
                "适用文章类型": [],
                "警告": "效果不稳定，可能让分数飙升",
            },
            "prevent_hallucinations": {
                "zerogpt_change": 0,
                "gptzero_change": 0,
                "reliability": 0.6,
                "适用文章类型": ["technical"],
            },
            "avoids_mechanization": {
                "zerogpt_change": 0,
                "gptzero_change": 0,
                "reliability": 0.5,
                "适用文章类型": ["academic_argument"],
            },
            "add_details": {
                "zerogpt_change": 0,
                "gptzero_change": 0,
                "reliability": 0.5,
                "适用文章类型": ["creative_narrative"],
            },
        }
    
    def analyze_article_features(self, text: str) -> Dict:
        """分析文章特征"""
        # 基本统计
        words = text.split()
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        word_count = len(words)
        sentence_count = len(sentences)
        avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
        
        # 正式度分析（简单版本）
        formal_words = ['however', 'therefore', 'furthermore', 'moreover', 'consequently', 
                       'nevertheless', 'thus', 'hence', 'whereas', 'thereby']
        informal_words = ['gonna', 'wanna', 'yeah', 'ok', 'cool', 'stuff', 'things', 'like']
        
        formal_count = sum(1 for word in words if word.lower() in formal_words)
        informal_count = sum(1 for word in words if word.lower() in informal_words)
        
        formality_score = min(10, (formal_count / word_count * 1000) if word_count > 0 else 0)
        
        # 专业术语密度（简单版本：长词比例）
        long_words = [w for w in words if len(w) > 10]
        technical_term_ratio = len(long_words) / word_count if word_count > 0 else 0
        
        # 论证性分析
        argument_words = ['argue', 'claim', 'evidence', 'prove', 'demonstrate', 'show',
                         'indicate', 'suggest', 'support', 'conclude', 'reason', 'because']
        argument_count = sum(1 for word in words if word.lower() in argument_words)
        argument_score = min(10, (argument_count / word_count * 500) if word_count > 0 else 0)
        
        # 叙事性分析
        narrative_words = ['story', 'once', 'then', 'suddenly', 'finally', 'character',
                          'happened', 'remember', 'felt', 'thought', 'said']
        narrative_count = sum(1 for word in words if word.lower() in narrative_words)
        narrative_score = min(10, (narrative_count / word_count * 500) if word_count > 0 else 0)
        
        return {
            "word_count": word_count,
            "sentence_count": sentence_count,
            "avg_sentence_length": avg_sentence_length,
            "formality_score": formality_score,
            "technical_term_ratio": technical_term_ratio,
            "argument_score": argument_score,
            "narrative_score": narrative_score,
        }
    
    def classify_article_type(self, features: Dict) -> str:
        """分类文章类型"""
        if features["formality_score"] > 3 and features["argument_score"] > 3:
            return "academic_argument"  # 学术议论文
        elif features["narrative_score"] > 5:
            return "creative_narrative"  # 创意叙事
        elif features["technical_term_ratio"] > 0.05:
            return "technical"  # 技术文章
        else:
            return "informal"  # 非正式文章
    
    def recommend_pipeline(
        self, 
        article_type: str, 
        zerogpt_score: float, 
        gptzero_score: float
    ) -> Tuple[List[Dict], str]:
        """
        推荐提示词组合
        
        Returns:
            (pipeline, reasoning)
        """
        pipeline = []
        reasoning = []
        
        # 基于文章类型和分数推荐
        if article_type == "academic_argument":
            reasoning.append(f"文章类型: 学术议论文")
            reasoning.append(f"当前分数: ZeroGPT {zerogpt_score:.1f}%, GPTZero {gptzero_score:.1f}%")
            
            # 第1步：simplify（铺垫）
            if zerogpt_score > 10 or gptzero_score > 10:
                pipeline.append({
                    "prompt_name": "simplify",
                    "llm": "gpt",
                    "model": "gpt-4.1-mini",
                    "reason": "简化句式，为后续步骤创造条件"
                })
                reasoning.append("步骤1: simplify - 简化句式（铺垫）")
            
            # 第2步：basic_rewrite（降ZeroGPT）
            if zerogpt_score > 5:
                pipeline.append({
                    "prompt_name": "basic_rewrite",
                    "llm": "gemini",
                    "model": "gemini-2.5-flash",
                    "reason": f"降低ZeroGPT（预期从{zerogpt_score:.1f}%降至1-3%）"
                })
                reasoning.append(f"步骤{len(pipeline)}: basic_rewrite - 降低ZeroGPT（预期-90%）")
                zerogpt_score = max(1, zerogpt_score - 90)  # 模拟效果
            
            # 第3-4步：cross_trans（降GPTZero）
            if gptzero_score > 30:
                pipeline.append({
                    "prompt_name": "cross_trans",
                    "llm": "gemini",
                    "model": "gemini-2.5-flash",
                    "reason": f"降低GPTZero（预期从{gptzero_score:.1f}%降至{gptzero_score-28:.1f}%）"
                })
                reasoning.append(f"步骤{len(pipeline)}: cross_trans - 第1次中英互译（预期-28%）")
                gptzero_score = max(30, gptzero_score - 28)
                
                if gptzero_score > 30:
                    pipeline.append({
                        "prompt_name": "cross_trans",
                        "llm": "gemini",
                        "model": "gemini-2.5-flash",
                        "reason": f"进一步降低GPTZero（预期从{gptzero_score:.1f}%降至{gptzero_score-30:.1f}%）"
                    })
                    reasoning.append(f"步骤{len(pipeline)}: cross_trans - 第2次中英互译（预期-30%）")
            
            # 警告
            reasoning.append("\n⚠️ 避免使用:")
            reasoning.append("  - personalize: 会让ZeroGPT飙升80%+")
            reasoning.append("  - autofix: 效果不稳定")
            reasoning.append("  - depersonalize: 单独使用可能有害")
            
        elif article_type == "creative_narrative":
            reasoning.append(f"文章类型: 创意叙事")
            reasoning.append("⚠️ 警告: 此类型未充分测试，推荐策略可能不准确")
            
            # 保守策略
            if zerogpt_score > 10:
                pipeline.append({
                    "prompt_name": "simplify",
                    "llm": "gpt",
                    "model": "gpt-4.1-mini",
                    "reason": "简化句式"
                })
                pipeline.append({
                    "prompt_name": "basic_rewrite",
                    "llm": "gemini",
                    "model": "gemini-2.5-flash",
                    "reason": "降低ZeroGPT"
                })
            
            if gptzero_score > 30:
                pipeline.append({
                    "prompt_name": "cross_trans",
                    "llm": "gemini",
                    "model": "gemini-2.5-flash",
                    "reason": "降低GPTZero"
                })
        
        elif article_type == "technical":
            reasoning.append(f"文章类型: 技术文章")
            reasoning.append("⚠️ 警告: 此类型未充分测试")
            
            # 技术文章策略
            if zerogpt_score > 10:
                pipeline.append({
                    "prompt_name": "prevent_hallucinations",
                    "llm": "gemini",
                    "model": "gemini-2.5-flash",
                    "reason": "防止幻觉，保持技术准确性"
                })
                pipeline.append({
                    "prompt_name": "basic_rewrite",
                    "llm": "gemini",
                    "model": "gemini-2.5-flash",
                    "reason": "降低ZeroGPT"
                })
            
            if gptzero_score > 30:
                pipeline.append({
                    "prompt_name": "cross_trans",
                    "llm": "gemini",
                    "model": "gemini-2.5-flash",
                    "reason": "降低GPTZero"
                })
                pipeline.append({
                    "prompt_name": "cross_trans",
                    "llm": "gemini",
                    "model": "gemini-2.5-flash",
                    "reason": "进一步降低GPTZero"
                })
        
        else:  # informal
            reasoning.append(f"文章类型: 非正式文章")
            reasoning.append("⚠️ 警告: 此类型未充分测试")
            
            # 简单策略
            if zerogpt_score > 10:
                pipeline.append({
                    "prompt_name": "basic_rewrite",
                    "llm": "gemini",
                    "model": "gemini-2.5-flash",
                    "reason": "降低ZeroGPT"
                })
            
            if gptzero_score > 30:
                pipeline.append({
                    "prompt_name": "cross_trans",
                    "llm": "gemini",
                    "model": "gemini-2.5-flash",
                    "reason": "降低GPTZero"
                })
        
        return pipeline, "\n".join(reasoning)
    
    def suggest_next_step(
        self,
        current_pipeline: List[Dict],
        current_scores: Dict[str, float],
        article_type: str
    ) -> str:
        """建议下一步操作"""
        zerogpt = current_scores.get("zerogpt", 100)
        gptzero = current_scores.get("gptzero", 100)
        
        # 已达标
        if zerogpt < 5 and gptzero < 30:
            return "✅ 完成！分数已达标\n  ZeroGPT < 5% ✅\n  GPTZero < 30% ✅"
        
        # 需要继续优化
        suggestions = []
        
        if zerogpt >= 5:
            suggestions.append(f"⚠️ ZeroGPT还有{zerogpt:.1f}%，建议:")
            if not any(step["prompt_name"] == "basic_rewrite" for step in current_pipeline):
                suggestions.append("  - 使用 basic_rewrite（预期降低90%）")
            else:
                suggestions.append("  - 已使用basic_rewrite但效果不佳，可能需要检查文章")
        
        if gptzero >= 30:
            suggestions.append(f"⚠️ GPTZero还有{gptzero:.1f}%，建议:")
            cross_trans_count = sum(1 for step in current_pipeline if step["prompt_name"] == "cross_trans")
            if cross_trans_count == 0:
                suggestions.append("  - 使用 cross_trans（预期降低28%）")
            elif cross_trans_count == 1:
                suggestions.append("  - 再次使用 cross_trans（预期降低30%）")
            else:
                suggestions.append("  - 已使用2次cross_trans，可能需要其他策略")
        
        if not suggestions:
            suggestions.append("✅ 分数接近目标，可以继续优化或停止")
        
        return "\n".join(suggestions)
    
    def analyze_and_recommend(
        self,
        text: str,
        zerogpt_score: float,
        gptzero_score: float
    ) -> Dict:
        """
        完整的分析和推荐流程
        
        Args:
            text: 文章内容
            zerogpt_score: 当前ZeroGPT分数
            gptzero_score: 当前GPTZero分数
        
        Returns:
            {
                "features": 文章特征,
                "article_type": 文章类型,
                "pipeline": 推荐的提示词组合,
                "reasoning": 推荐理由,
                "warnings": 警告信息,
            }
        """
        # 分析文章特征
        features = self.analyze_article_features(text)
        
        # 分类文章类型
        article_type = self.classify_article_type(features)
        
        # 推荐策略
        pipeline, reasoning = self.recommend_pipeline(
            article_type, zerogpt_score, gptzero_score
        )
        
        # 生成警告
        warnings = []
        if article_type == "academic_argument":
            warnings.append("⚠️ 学术议论文不要使用: personalize, autofix, depersonalize")
        elif article_type in ["creative_narrative", "technical", "informal"]:
            warnings.append(f"⚠️ {article_type}类型文章的策略未充分测试，效果可能不准确")
        
        return {
            "features": features,
            "article_type": article_type,
            "pipeline": pipeline,
            "reasoning": reasoning,
            "warnings": warnings,
        }


# 测试代码
if __name__ == "__main__":
    recommender = SmartRecommender()
    
    # 读取样本文章
    with open("sample_article.txt", "r", encoding="utf-8") as f:
        text = f.read()
    
    # 分析和推荐
    result = recommender.analyze_and_recommend(text, 99.99, 99.78)
    
    print("="*80)
    print("智能推荐系统测试")
    print("="*80)
    
    print("\n文章特征:")
    for key, value in result["features"].items():
        print(f"  {key}: {value}")
    
    print(f"\n文章类型: {result['article_type']}")
    
    print("\n推荐策略:")
    print(result["reasoning"])
    
    print(f"\n推荐的提示词组合（{len(result['pipeline'])}步）:")
    for i, step in enumerate(result["pipeline"], 1):
        print(f"  {i}. {step['prompt_name']} ({step['llm']} - {step['model']})")
        print(f"     理由: {step['reason']}")
    
    if result["warnings"]:
        print("\n警告:")
        for warning in result["warnings"]:
            print(f"  {warning}")
