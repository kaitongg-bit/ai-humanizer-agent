#!/usr/bin/env python3.11
"""
AI降重Agent Loop系统
通过组合提示词改写文章，调用检测API，根据反馈迭代优化
"""

import os
import json
import time
import requests
import pandas as pd
from datetime import datetime
from openai import OpenAI
import google.generativeai as genai

# 禁用SSL警告
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class AIHumanizerAgent:
    """AI降重Agent"""
    
    def __init__(self):
        """初始化"""
        # API Keys
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.gemini_api_key = "AIzaSyBdlSXdd63zlkM2pAZRm1WuKqc7g9oesk0"
        
        # 初始化LLM客户端
        self.openai_client = OpenAI()
        genai.configure(api_key=self.gemini_api_key)
        
        # 检测API配置
        self.zerogpt_config = {
            "url": "https://api.zerogpt.com/api/detect/detectText",
            "headers": {
                "ApiKey": "d486bb7f-7dee-4f5e-880f-6b442c4544f5",
                "Content-Type": "application/json"
            }
        }
        
        self.gptzero_config = {
            "url": "https://api.gptzero.me/v2/predict/text",
            "headers": {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "x-api-key": "e455f57763ce4fb69be5350a677fc0c0"
            }
        }
        
        # 提示词库
        self.prompts = self._load_prompts()
        
        # 结果记录
        self.results = []
        
    def _load_prompts(self):
        """加载提示词库"""
        return {
            "avoids_mechanization": {
                "zh": "重组文本的论证结构与信息呈现顺序，在保持核心观点一致的前提下，通过改变句式组合与段落衔接方式形成差异化表达，避免语言模式的机械重复",
                "en": "Reorganize the argument structure and information presentation sequence of the text. While maintaining consistency in core viewpoints, create differentiated expression by altering sentence combinations and paragraph transitions to avoid mechanical repetition of language patterns"
            },
            "simplify": {
                "zh": "所有内容必须基于可验证的事实依据，不添加未经验证的信息，对不确定内容明确标注；除规范引用的内容外，均需使用个人语言重新组织。采用半正式学术文体确保句结构完整，优先使用简洁句式；将专业术语转换为日常用语，使用基础连接词，采用直接明了的表达方式，避免生僻词汇，保证行文逻辑顺畅。",
                "en": "Use a semi-formal academic style to ensure complete sentence structures, giving priority to concise sentence patterns; convert specialized terms into everyday language, use basic conjunctions, adopt a straightforward and clear expression, avoid rare vocabulary, and ensure smooth logical flow in the writing."
            },
            "add_details": {
                "zh": "对关键论点进行适度扩展，根据需要补充实际案例、具体数据或详细详说明，避免空泛描述，通过具象化描写提升内容的真实感与可信度，使文本更具阅读价值。扩写后的字数和源文本相差幅度在30%以内，比如源文本100字，扩写后的带细节的版本是130字。",
                "en": "Properly expand on key arguments, supplement with actual cases, specific data, or detailed explanations as needed, avoid vague descriptions, enhance the authenticity and credibility of the content through concrete depictions, and make the text more valuable for reading. The difference in word count between the expanded version and the original text should be within 30%. For example, if the original text is 100 words, the expanded version with details should be 130 words."
            },
            "advanced_rewrite": {
                "zh": "避免使用机械化的连接词(如\"首先\"\"其次\"\"然后\")，改用更具连性的自然过渡；通过使用多样化句式，混合简单句、复合句和括入语使表达更富有层次感，同时避免连续短句或过于整齐的句式。在叙述数据或结论时，补充背景信息或个人研究观察，使内容更加具体并贴近实际研究场景，并通过问题引导或归纳总结的方式实现段落之间的自然过渡，避免生硬切换，从而提升整体阅读的流畅性和逻辑性。最后输出语言为英语。",
                "en": "Avoid using mechanical connectors such as \"first, next, then\", instead, adopt more cohesive and natural transitions. By using diverse sentence structures, mixing simple sentences, compound sentences, and parenthetical expressions, the expression can be made more layered, while avoiding consecutive short sentences or overly neat sentence patterns. When presenting data or conclusions, supplementing with background information or personal research observations makes the content more specific and closer to the actual research scenario. Additionally, achieving natural transitions between paragraphs through question guidance or summarization avoids abrupt shifts, thereby enhancing the overall readability and logical flow of the text. The final output language is English."
            },
            "prevent_hallucinations": {
                "zh": "请记住，你的回答一切基于事实不能编造。不知道就回答不知道。并且不能照搬别人的话，需要用自己的语言重新描述一遍。(除了引用，引用要遵循MLA格式)写作风格介于正式学术写作和口语描述之间。保证所有的句子都要有主语，不要用复杂长句，尽量使用短句输出。替换掉所有非日常词汇。将所有的句子过度词和连接词换为最基础、最常用的词语。尽量使用简单、直接的表达方式，避免使用复杂或生僻的词汇。确保句子之间的逻辑关系清晰。",
                "en": "Please remember that all your answers must be based on facts and must not be made up. If you don't know, answer that you don't know. Also, you must not copy others' words. You need to rephrase them in your own words. (Except for quotations, which should follow the MLA format.) The writing style should be between formal academic writing and spoken description. Make sure every sentence has a subject. Do not use complex long sentences; try to use short sentences. Replace all non-everyday words. Replace all sentence transition words and conjunctions with the most basic and commonly used ones. Try to use simple and direct expressions, and avoid using complex or uncommon words. Ensure that the logical relationship between sentences is clear."
            },
            "basic_rewrite": {
                "zh": "保持核心信息不变，将段落中的复合句拆分为2-3个短句，每句控制在20词以内，替换\"因此\"\"此外\"等高频连接词。将文本中堆叠的被动语调整为主动与被动交替的形式，删减过度使用的逻辑连接词。",
                "en": "Keep the core information unchanged. Split compound sentences in the paragraph into 2-3 short sentences. Each sentence should be within 20 words. Replace high-frequency conjunctions such as \"therefore\" and \"in addition\". Adjust the stacked passive voices in the text to an alternating form of active and passive voices. Delete overused logical conjunctions."
            },
            "autofix": {
                "zh": "你是一个非母语的留学生，用半学术化的风格改写，去掉\"-\"\"first\"等任何模版化和机械感的连接和分隔词汇，拒绝小标题和分行，拒绝星号破折号等符号，需要连贯的成几个段落地输出，段落有长有短词汇数有差异。词汇除了术语外保持雅思六级的水平，无复杂高级词汇。句子长度要提高随机性，尽量短句输出。全文意思保持一致但可以插入一些语法错误以模拟真人。",
                "en": "You are an international student whose first language is not English. Rewrite in a semi-academic style. Remove any template-like and mechanical connecting or separating words such as \"-\" and \"first\". Refuse subheadings and line breaks, and reject symbols like asterisks and dashes. Output in several coherent paragraphs, with paragraphs varying in length and number of words. Use vocabulary at the IELTS Band 6 level except for technical terms, without complex and advanced words. Increase the randomness of sentence lengths, and try to use short sentences. Keep the overall meaning consistent, but you can insert some grammatical errors to simulate a real person."
            },
            "cross_trans": {
                "zh": "先把内容翻译为中文，然后再逐字翻译为英文（很傻的高中生翻译），中文和英文翻译结果都给我看",
                "en": "First translate the content into Chinese, then translate it word by word into English (a silly high school student's translation). Show me both the Chinese and English translation results."
            },
            "personalize": {
                "zh": "你是一个幽默活泼的非母语者，你在用正式语气写论文，但是每10句话你总有一句用个人色彩很重的话来重新表达一下，把下面的文章选中一些句子调整语气。",
                "en": "You are a humorous and lively non-native speaker. You are writing a thesis in a formal tone, but every 10 sentences, you always rephrase one with a very personal touch. Please select some sentences from the following article and adjust their tone."
            },
            "depersonalize": {
                "zh": "稍微少一些个人色彩：我只要你把特别幼儿化和不正式的个人色彩语句找出来并删改，其他的个人色彩语句不动，特别幼儿化的例子：我的祖母会懂的；我太开心啦；妈妈夸我；真棒；我的天啊",
                "en": "Reduce personal elements a bit: I only want you to identify and revise the sentences with particularly childish and informal personal elements; leave other personal elements unchanged. Examples of particularly childish expressions: \"My grandmother would understand\"; \"I'm so happy\"; \"Mom praised me\"; \"Great\"; \"Oh my god\""
            }
        }
    
    def detect_zerogpt(self, text):
        """使用ZeroGPT检测"""
        try:
            data = {"input_text": text}
            response = requests.post(
                self.zerogpt_config["url"],
                headers=self.zerogpt_config["headers"],
                json=data,
                timeout=30,
                verify=False
            )
            result = response.json()
            
            if result.get("success") and "data" in result:
                return {
                    "score": result["data"].get("fakePercentage", 0),
                    "feedback": result["data"].get("feedback", ""),
                    "raw": result
                }
        except Exception as e:
            print(f"ZeroGPT检测失败: {e}")
        
        return {"score": None, "feedback": "检测失败", "raw": None}
    
    def detect_gptzero(self, text):
        """使用GPTZero检测"""
        try:
            data = {"document": text, "multilingual": False}
            response = requests.post(
                self.gptzero_config["url"],
                headers=self.gptzero_config["headers"],
                json=data,
                timeout=30
            )
            result = response.json()
            
            if "documents" in result and len(result["documents"]) > 0:
                doc = result["documents"][0]
                return {
                    "score": doc.get("completely_generated_prob", 0) * 100,
                    "predicted_class": doc.get("predicted_class", ""),
                    "confidence": doc.get("confidence_score", 0),
                    "raw": result
                }
        except Exception as e:
            print(f"GPTZero检测失败: {e}")
        
        return {"score": None, "predicted_class": "检测失败", "confidence": 0, "raw": None}
    
    def rewrite_with_gpt(self, text, prompt, model="gpt-4.1-mini"):
        """使用GPT改写"""
        try:
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful writing assistant."},
                    {"role": "user", "content": f"{prompt}\n\nText to rewrite:\n{text}"}
                ],
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"GPT改写失败: {e}")
            return None
    
    def rewrite_with_gemini(self, text, prompt, model="gemini-2.5-flash"):
        """使用Gemini改写"""
        try:
            model_obj = genai.GenerativeModel(model)
            response = model_obj.generate_content(f"{prompt}\n\nText to rewrite:\n{text}")
            return response.text
        except Exception as e:
            print(f"Gemini改写失败: {e}")
            return None
    
    def run_pipeline(self, text, pipeline_steps, article_id="test"):
        """运行改写流水线
        
        Args:
            text: 原始文本
            pipeline_steps: 流水线步骤列表，每个步骤是一个字典:
                {
                    "prompt_name": "autofix",
                    "llm": "gpt",  # "gpt" or "gemini"
                    "model": "gpt-4.1-mini"  # 具体模型名称
                }
            article_id: 文章ID
        
        Returns:
            结果列表，每个步骤的结果
        """
        current_text = text
        pipeline_results = []
        
        print(f"\n{'='*80}")
        print(f"开始处理文章: {article_id}")
        print(f"流水线步骤数: {len(pipeline_steps)}")
        print(f"{'='*80}\n")
        
        # 检测原文
        print(f"[步骤 0] 检测原文")
        zerogpt_result = self.detect_zerogpt(current_text)
        gptzero_result = self.detect_gptzero(current_text)
        
        step_result = {
            "article_id": article_id,
            "step": 0,
            "step_name": "原文",
            "prompt_name": None,
            "llm": None,
            "model": None,
            "input_text": current_text,
            "output_text": current_text,
            "zerogpt_score": zerogpt_result["score"],
            "gptzero_score": gptzero_result["score"],
            "gptzero_class": gptzero_result.get("predicted_class"),
            "timestamp": datetime.now().isoformat()
        }
        pipeline_results.append(step_result)
        
        print(f"  ZeroGPT: {zerogpt_result['score']}%")
        print(f"  GPTZero: {gptzero_result['score']:.2f}% ({gptzero_result.get('predicted_class')})")
        print()
        
        # 执行流水线步骤
        for i, step in enumerate(pipeline_steps, 1):
            prompt_name = step["prompt_name"]
            llm = step["llm"]
            model = step["model"]
            
            print(f"[步骤 {i}] {prompt_name} (使用 {llm} - {model})")
            
            # 获取提示词
            if prompt_name not in self.prompts:
                print(f"  ⚠️ 提示词不存在: {prompt_name}")
                continue
            
            prompt = self.prompts[prompt_name]["en"]
            
            # 改写
            if llm == "gpt":
                rewritten_text = self.rewrite_with_gpt(current_text, prompt, model)
            elif llm == "gemini":
                rewritten_text = self.rewrite_with_gemini(current_text, prompt, model)
            else:
                print(f"  ⚠️ 不支持的LLM: {llm}")
                continue
            
            if not rewritten_text:
                print(f"  ⚠️ 改写失败")
                continue
            
            # 检测改写后的文本
            time.sleep(1)  # 避免API限流
            zerogpt_result = self.detect_zerogpt(rewritten_text)
            gptzero_result = self.detect_gptzero(rewritten_text)
            
            step_result = {
                "article_id": article_id,
                "step": i,
                "step_name": prompt_name,
                "prompt_name": prompt_name,
                "llm": llm,
                "model": model,
                "input_text": current_text,
                "output_text": rewritten_text,
                "zerogpt_score": zerogpt_result["score"],
                "gptzero_score": gptzero_result["score"],
                "gptzero_class": gptzero_result.get("predicted_class"),
                "timestamp": datetime.now().isoformat()
            }
            pipeline_results.append(step_result)
            
            print(f"  ZeroGPT: {zerogpt_result['score']}%")
            print(f"  GPTZero: {gptzero_result['score']:.2f}% ({gptzero_result.get('predicted_class')})")
            print()
            
            # 更新当前文本
            current_text = rewritten_text
        
        print(f"{'='*80}")
        print(f"流水线完成！")
        print(f"{'='*80}\n")
        
        return pipeline_results
    
    def save_results(self, results, output_path):
        """保存结果到CSV"""
        df = pd.DataFrame(results)
        df.to_csv(output_path, index=False, encoding='utf-8')
        print(f"✅ 结果已保存到: {output_path}")
        return df


if __name__ == "__main__":
    # 测试
    agent = AIHumanizerAgent()
    
    # 定义测试流水线（组合拳1）
    pipeline = [
        {"prompt_name": "autofix", "llm": "gemini", "model": "gemini-2.5-flash"},
        {"prompt_name": "cross_trans", "llm": "gemini", "model": "gemini-2.5-flash"},
        {"prompt_name": "personalize", "llm": "gemini", "model": "gemini-2.5-flash"},
        {"prompt_name": "depersonalize", "llm": "gemini", "model": "gemini-2.5-flash"},
        {"prompt_name": "cross_trans", "llm": "gemini", "model": "gemini-2.5-flash"},
    ]
    
    # 测试文本
    test_text = """Solid-state batteries (SSBs) are widely regarded as a next-generation energy storage technology with the potential to surpass conventional lithium-ion batteries in terms of safety, energy density, and lifespan. Unlike conventional batteries that use liquid electrolytes, SSBs employ solid electrolytes, which significantly reduce the risk of leakage and thermal runaway."""
    
    # 运行流水线
    results = agent.run_pipeline(test_text, pipeline, "test_article")
    
    # 保存结果
    agent.save_results(results, "test_results.csv")
