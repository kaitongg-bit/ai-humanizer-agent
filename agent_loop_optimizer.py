#!/usr/bin/env python3.11
"""
Agent Loop迭代优化系统
自动分析结果并生成新的组合拳策略
"""

import json
import pandas as pd
from datetime import datetime
from ai_humanizer_agent import AIHumanizerAgent


class AgentLoopOptimizer:
    """Agent Loop优化器"""
    
    def __init__(self):
        self.agent = AIHumanizerAgent()
        self.iteration_history = []
        self.best_combo = None
        self.best_score = float('inf')  # 综合分数（越低越好）
        
    def calculate_combo_score(self, results):
        """计算组合拳的综合得分
        
        得分 = 最终ZeroGPT分数 + 最终GPTZero分数 + 步骤数惩罚
        """
        final_result = results[-1]
        zerogpt = final_result['zerogpt_score'] or 100
        gptzero = final_result['gptzero_score'] or 100
        steps = len(results) - 1  # 减去原文
        
        # 综合得分：两个检测器的平均分 + 步骤数惩罚（每步+5分）
        score = (zerogpt + gptzero) / 2 + steps * 5
        
        return {
            'score': score,
            'zerogpt': zerogpt,
            'gptzero': gptzero,
            'steps': steps
        }
    
    def analyze_and_suggest(self, results, iteration):
        """分析结果并生成新的组合拳建议"""
        
        scores = self.calculate_combo_score(results)
        
        print(f"\n{'='*80}")
        print(f"迭代 {iteration} 分析")
        print(f"{'='*80}")
        print(f"综合得分: {scores['score']:.2f}")
        print(f"  - ZeroGPT: {scores['zerogpt']:.2f}%")
        print(f"  - GPTZero: {scores['gptzero']:.2f}%")
        print(f"  - 步骤数: {scores['steps']}")
        
        # 分析每一步的效果
        print(f"\n各步骤效果:")
        for i in range(1, len(results)):
            prev = results[i-1]
            curr = results[i]
            
            zerogpt_change = (curr['zerogpt_score'] or 0) - (prev['zerogpt_score'] or 0)
            gptzero_change = (curr['gptzero_score'] or 0) - (prev['gptzero_score'] or 0)
            
            print(f"  步骤{i} ({curr['step_name']}): "
                  f"ZeroGPT {zerogpt_change:+.2f}%, "
                  f"GPTZero {gptzero_change:+.2f}%")
        
        # 生成建议
        suggestion = self._generate_suggestion(results, scores, iteration)
        
        print(f"\n{'='*80}")
        print(f"Manus的思考和建议")
        print(f"{'='*80}")
        print(suggestion['analysis'])
        print(f"\n新组合拳:")
        for i, step in enumerate(suggestion['new_combo'], 1):
            print(f"  {i}. {step['prompt_name']} ({step['llm']} - {step['model']})")
        print(f"\n理由: {suggestion['reason']}")
        
        return suggestion
    
    def _generate_suggestion(self, results, scores, iteration):
        """生成新组合拳建议"""
        
        # 迭代1的结果分析
        if iteration == 1:
            # 组合拳2: avoids_mechanization → add_details → simplify → basic_rewrite
            # 结果: ZeroGPT 11.37%, GPTZero 99.99%
            
            analysis = """
迭代1结果分析:
- ZeroGPT降到11.37%，效果很好！
- GPTZero仍在99.99%，几乎没降
- basic_rewrite对ZeroGPT非常有效（96.76% → 11.37%）
- simplify对GPTZero有效（99.99% → 92.98%），但被basic_rewrite抵消了

问题: GPTZero识别出basic_rewrite后的文本仍是AI

可能原因: basic_rewrite虽然拆分了句子，但整体语言模式仍然机械

策略: 在basic_rewrite后加入"打乱语言模式"的步骤
"""
            
            reason = """
GPTZero对语言模式很敏感，需要用cross_trans或personalize打乱。
我选择cross_trans（中英互译），因为它能彻底改变表达方式。
"""
            
            new_combo = [
                {"prompt_name": "simplify", "llm": "gpt", "model": "gpt-4.1-mini"},
                {"prompt_name": "basic_rewrite", "llm": "gemini", "model": "gemini-2.5-flash"},
                {"prompt_name": "cross_trans", "llm": "gemini", "model": "gemini-2.5-flash"},
            ]
            
        elif iteration == 2:
            # 根据迭代2的实际结果动态生成
            final_zerogpt = scores['zerogpt']
            final_gptzero = scores['gptzero']
            
            if final_gptzero < 50:
                # GPTZero降下来了
                analysis = f"""
迭代2结果分析:
- ZeroGPT: {final_zerogpt:.2f}%
- GPTZero: {final_gptzero:.2f}%
- cross_trans成功降低了GPTZero！

策略: 继续优化，尝试personalize增加自然度
"""
                reason = "cross_trans有效，加入personalize增加个人化表达，进一步降低AI特征"
                
                new_combo = [
                    {"prompt_name": "simplify", "llm": "gpt", "model": "gpt-4.1-mini"},
                    {"prompt_name": "basic_rewrite", "llm": "gemini", "model": "gemini-2.5-flash"},
                    {"prompt_name": "cross_trans", "llm": "gemini", "model": "gemini-2.5-flash"},
                    {"prompt_name": "personalize", "llm": "gpt", "model": "gpt-4.1-mini"},
                ]
            else:
                # GPTZero还是很高
                analysis = f"""
迭代2结果分析:
- ZeroGPT: {final_zerogpt:.2f}%
- GPTZero: {final_gptzero:.2f}%
- cross_trans效果不理想

策略: 尝试autofix，它在组合拳1中表现不错
"""
                reason = "cross_trans不够，尝试autofix模拟非母语者写作风格"
                
                new_combo = [
                    {"prompt_name": "simplify", "llm": "gpt", "model": "gpt-4.1-mini"},
                    {"prompt_name": "basic_rewrite", "llm": "gemini", "model": "gemini-2.5-flash"},
                    {"prompt_name": "autofix", "llm": "gemini", "model": "gemini-2.5-flash"},
                ]
        
        elif iteration == 3:
            final_zerogpt = scores['zerogpt']
            final_gptzero = scores['gptzero']
            
            if final_zerogpt < 20 and final_gptzero < 50:
                # 两个都降下来了
                analysis = f"""
迭代3结果分析:
- ZeroGPT: {final_zerogpt:.2f}%
- GPTZero: {final_gptzero:.2f}%
- 效果很好！两个检测器都降低了

策略: 尝试简化流程，去掉不必要的步骤
"""
                reason = "效果已经很好，尝试减少步骤降低成本"
                
                new_combo = [
                    {"prompt_name": "basic_rewrite", "llm": "gemini", "model": "gemini-2.5-flash"},
                    {"prompt_name": "autofix", "llm": "gemini", "model": "gemini-2.5-flash"},
                ]
            else:
                # 还需要优化
                analysis = f"""
迭代3结果分析:
- ZeroGPT: {final_zerogpt:.2f}%
- GPTZero: {final_gptzero:.2f}%
- 还需要进一步优化

策略: 尝试组合拳1的后半段（personalize + depersonalize）
"""
                reason = "前面的步骤已经降低了分数，现在需要平衡个人化程度"
                
                new_combo = [
                    {"prompt_name": "simplify", "llm": "gpt", "model": "gpt-4.1-mini"},
                    {"prompt_name": "basic_rewrite", "llm": "gemini", "model": "gemini-2.5-flash"},
                    {"prompt_name": "personalize", "llm": "gpt", "model": "gpt-4.1-mini"},
                    {"prompt_name": "depersonalize", "llm": "gemini", "model": "gemini-2.5-flash"},
                ]
        
        else:
            # 迭代4+：根据历史最佳结果生成
            analysis = f"""
迭代{iteration}结果分析:
- 当前得分: {scores['score']:.2f}
- 历史最佳: {self.best_score:.2f}

策略: 尝试新的组合
"""
            reason = "探索新的可能性"
            
            # 随机尝试不同的组合
            new_combo = [
                {"prompt_name": "prevent_hallucinations", "llm": "gpt", "model": "gpt-4.1-mini"},
                {"prompt_name": "basic_rewrite", "llm": "gemini", "model": "gemini-2.5-flash"},
            ]
        
        return {
            'analysis': analysis,
            'reason': reason,
            'new_combo': new_combo
        }
    
    def run_iteration(self, text, pipeline, iteration, article_id):
        """运行一次迭代"""
        
        print(f"\n{'#'*80}")
        print(f"# 迭代 {iteration}")
        print(f"{'#'*80}")
        
        # 执行测试
        results = self.agent.run_pipeline(text, pipeline, f"{article_id}_iter{iteration}")
        
        # 保存结果
        output_file = f"iteration_{iteration}_results.csv"
        self.agent.save_results(results, output_file)
        
        # 计算得分
        scores = self.calculate_combo_score(results)
        
        # 更新最佳结果
        if scores['score'] < self.best_score:
            self.best_score = scores['score']
            self.best_combo = {
                'iteration': iteration,
                'pipeline': pipeline,
                'scores': scores,
                'results': results
            }
            print(f"\n🎉 新的最佳组合！得分: {self.best_score:.2f}")
        
        # 记录历史
        self.iteration_history.append({
            'iteration': iteration,
            'pipeline': pipeline,
            'scores': scores,
            'timestamp': datetime.now().isoformat()
        })
        
        return results, scores
    
    def optimize(self, text, initial_pipeline, article_id, max_iterations=5, target_score=50):
        """自动优化流程
        
        Args:
            text: 原始文本
            initial_pipeline: 初始组合拳
            article_id: 文章ID
            max_iterations: 最大迭代次数
            target_score: 目标得分（达到后停止）
        """
        
        current_pipeline = initial_pipeline
        
        for i in range(1, max_iterations + 1):
            # 运行迭代
            results, scores = self.run_iteration(text, current_pipeline, i, article_id)
            
            # 检查是否达到目标
            if scores['score'] <= target_score:
                print(f"\n🎉 达到目标得分！当前: {scores['score']:.2f}, 目标: {target_score}")
                break
            
            # 分析并生成新建议
            if i < max_iterations:
                suggestion = self.analyze_and_suggest(results, i)
                current_pipeline = suggestion['new_combo']
            else:
                print(f"\n达到最大迭代次数 ({max_iterations})")
        
        # 输出最终总结
        self.print_summary()
        
        return self.best_combo
    
    def print_summary(self):
        """打印优化总结"""
        
        print(f"\n{'='*80}")
        print(f"优化总结")
        print(f"{'='*80}")
        
        print(f"\n迭代历史:")
        for record in self.iteration_history:
            scores = record['scores']
            print(f"  迭代{record['iteration']}: "
                  f"得分={scores['score']:.2f}, "
                  f"ZeroGPT={scores['zerogpt']:.2f}%, "
                  f"GPTZero={scores['gptzero']:.2f}%, "
                  f"步骤={scores['steps']}")
        
        if self.best_combo:
            print(f"\n🏆 最佳组合:")
            print(f"  迭代: {self.best_combo['iteration']}")
            print(f"  得分: {self.best_combo['scores']['score']:.2f}")
            print(f"  ZeroGPT: {self.best_combo['scores']['zerogpt']:.2f}%")
            print(f"  GPTZero: {self.best_combo['scores']['gptzero']:.2f}%")
            print(f"  步骤数: {self.best_combo['scores']['steps']}")
            print(f"\n  组合:")
            for j, step in enumerate(self.best_combo['pipeline'], 1):
                print(f"    {j}. {step['prompt_name']} ({step['llm']} - {step['model']})")


if __name__ == "__main__":
    # 读取样本文章
    with open("sample_article.txt", "r", encoding="utf-8") as f:
        text = f.read()
    
    # 初始化优化器
    optimizer = AgentLoopOptimizer()
    
    # 初始组合拳（基于迭代1的结果）
    initial_pipeline = [
        {"prompt_name": "simplify", "llm": "gpt", "model": "gpt-4.1-mini"},
        {"prompt_name": "basic_rewrite", "llm": "gemini", "model": "gemini-2.5-flash"},
        {"prompt_name": "cross_trans", "llm": "gemini", "model": "gemini-2.5-flash"},
    ]
    
    # 开始优化（最多5次迭代，目标得分50）
    best_combo = optimizer.optimize(
        text=text,
        initial_pipeline=initial_pipeline,
        article_id="ai_1",
        max_iterations=5,
        target_score=50
    )
