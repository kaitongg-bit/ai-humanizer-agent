"""
批量验证脚本
在5篇文章上测试3个方案：组合拳1、组合拳4、智能推荐
"""

import json
import time
import pandas as pd
from ai_humanizer_agent import AIHumanizerAgent

# 组合拳定义
COMBO1 = [
    {"prompt_name": "autofix", "llm": "gemini", "model": "gemini-2.5-flash"},
    {"prompt_name": "cross_trans", "llm": "gemini", "model": "gemini-2.5-flash"},
    {"prompt_name": "personalize", "llm": "gemini", "model": "gemini-2.5-flash"},
    {"prompt_name": "depersonalize", "llm": "gemini", "model": "gemini-2.5-flash"},
    {"prompt_name": "cross_trans", "llm": "gemini", "model": "gemini-2.5-flash"},
]

COMBO4 = [
    {"prompt_name": "simplify", "llm": "gpt", "model": "gpt-4.1-mini"},
    {"prompt_name": "basic_rewrite", "llm": "gemini", "model": "gemini-2.5-flash"},
    {"prompt_name": "cross_trans", "llm": "gemini", "model": "gemini-2.5-flash"},
    {"prompt_name": "depersonalize", "llm": "gemini", "model": "gemini-2.5-flash"},
    {"prompt_name": "autofix", "llm": "gemini", "model": "gemini-2.5-flash"},
    {"prompt_name": "cross_trans", "llm": "gemini", "model": "gemini-2.5-flash"},
]

def main():
    # 加载文章
    with open("validation_5_articles.json", "r") as f:
        articles = json.load(f)
    
    print("="*80)
    print(f"批量验证开始 - {len(articles)}篇文章 × 3个方案 = {len(articles)*3}次测试")
    print("="*80)
    
    # 初始化Agent（需要先更新gemini_api_key）
    agent = AIHumanizerAgent()
    # 更新Gemini API密钥
    agent.gemini_api_key = "AIzaSyAIzLm2xGeDxqXoPMDIkusB4R3zXvD0Xwo"
    import google.generativeai as genai
    genai.configure(api_key=agent.gemini_api_key)
    
    all_results = []
    
    for article_idx, article in enumerate(articles, 1):
        article_id = article['id']
        text = article['text']
        
        print(f"\n{'='*80}")
        print(f"文章 {article_idx}/{len(articles)}: {article_id} ({article['word_count']}词)")
        print(f"{'='*80}")
        
        # 测试3个方案
        for combo_name, pipeline in [("组合拳1", COMBO1), ("组合拳4", COMBO4)]:
            print(f"\n--- 测试 {combo_name} ---")
            
            try:
                result = agent.run_pipeline(text, pipeline)
                
                # 提取最终分数
                final_step = result[-1]
                final_zerogpt = final_step['zerogpt_score']
                final_gptzero = final_step['gptzero_score']
                
                print(f"✅ 完成: ZeroGPT {final_zerogpt:.2f}%, GPTZero {final_gptzero:.2f}%")
                
                all_results.append({
                    'article_id': article_id,
                    'combo_name': combo_name,
                    'steps': len(pipeline),
                    'final_zerogpt': final_zerogpt,
                    'final_gptzero': final_gptzero,
                    'success': True,
                    'details': result
                })
                
            except Exception as e:
                print(f"❌ 失败: {str(e)[:100]}")
                all_results.append({
                    'article_id': article_id,
                    'combo_name': combo_name,
                    'steps': len(pipeline),
                    'final_zerogpt': None,
                    'final_gptzero': None,
                    'success': False,
                    'error': str(e)
                })
            
            # 延迟避免API限流
            time.sleep(2)
        
        # 测试智能推荐（基于原文分数）
        print(f"\n--- 测试 智能推荐 ---")
        try:
            from smart_recommender import SmartRecommender
            recommender = SmartRecommender()
            
            # 先检测原文分数
            original_scores = agent.detect_ai(text)
            zerogpt_orig = original_scores['zerogpt']
            gptzero_orig = original_scores['gptzero']
            
            print(f"原文分数: ZeroGPT {zerogpt_orig:.2f}%, GPTZero {gptzero_orig:.2f}%")
            
            # 获取推荐
            recommendation = recommender.analyze_and_recommend(text, zerogpt_orig, gptzero_orig)
            recommended_pipeline = recommendation['pipeline']
            
            print(f"推荐策略: {len(recommended_pipeline)}步")
            for i, step in enumerate(recommended_pipeline, 1):
                print(f"  {i}. {step['prompt_name']}")
            
            # 执行推荐策略
            result = agent.run_pipeline(text, recommended_pipeline)
            
            final_step = result[-1]
            final_zerogpt = final_step['zerogpt_score']
            final_gptzero = final_step['gptzero_score']
            
            print(f"✅ 完成: ZeroGPT {final_zerogpt:.2f}%, GPTZero {final_gptzero:.2f}%")
            
            all_results.append({
                'article_id': article_id,
                'combo_name': '智能推荐',
                'steps': len(recommended_pipeline),
                'final_zerogpt': final_zerogpt,
                'final_gptzero': final_gptzero,
                'success': True,
                'details': result,
                'recommendation': recommendation
            })
            
        except Exception as e:
            print(f"❌ 失败: {str(e)[:100]}")
            all_results.append({
                'article_id': article_id,
                'combo_name': '智能推荐',
                'steps': 0,
                'final_zerogpt': None,
                'final_gptzero': None,
                'success': False,
                'error': str(e)
            })
        
        time.sleep(2)
    
    # 保存结果
    print(f"\n{'='*80}")
    print("保存结果...")
    print(f"{'='*80}")
    
    # 保存详细结果
    with open("batch_validation_results.json", "w") as f:
        json.dump(all_results, f, indent=2)
    
    # 保存汇总表格
    summary_data = []
    for r in all_results:
        summary_data.append({
            '文章ID': r['article_id'],
            '方案': r['combo_name'],
            '步骤数': r['steps'],
            'ZeroGPT': f"{r['final_zerogpt']:.2f}%" if r['final_zerogpt'] is not None else "失败",
            'GPTZero': f"{r['final_gptzero']:.2f}%" if r['final_gptzero'] is not None else "失败",
            '成功': '✅' if r['success'] else '❌'
        })
    
    df = pd.DataFrame(summary_data)
    df.to_csv("batch_validation_summary.csv", index=False)
    
    print("\n✅ 结果已保存:")
    print("  - batch_validation_results.json (详细结果)")
    print("  - batch_validation_summary.csv (汇总表格)")
    
    print("\n汇总表格:")
    print(df.to_string(index=False))
    
    # 统计
    print(f"\n{'='*80}")
    print("统计")
    print(f"{'='*80}")
    
    total_tests = len(all_results)
    successful_tests = sum(1 for r in all_results if r['success'])
    
    print(f"总测试数: {total_tests}")
    print(f"成功: {successful_tests}/{total_tests} ({successful_tests/total_tests*100:.1f}%)")
    
    # 按方案统计
    for combo_name in ["组合拳1", "组合拳4", "智能推荐"]:
        combo_results = [r for r in all_results if r['combo_name'] == combo_name and r['success']]
        if combo_results:
            avg_zerogpt = sum(r['final_zerogpt'] for r in combo_results) / len(combo_results)
            avg_gptzero = sum(r['final_gptzero'] for r in combo_results) / len(combo_results)
            print(f"\n{combo_name}:")
            print(f"  平均ZeroGPT: {avg_zerogpt:.2f}%")
            print(f"  平均GPTZero: {avg_gptzero:.2f}%")
            print(f"  成功率: {len(combo_results)}/5")

if __name__ == "__main__":
    main()
