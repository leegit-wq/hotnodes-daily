# ai_scraper.py
# 该模块不直接爬取站点，而是根据时间/地点/关键词调用 LLM 生成事件素材
import os, json
from typing import Dict, Any, List

LLM_API_KEY = os.getenv('LLM_API_KEY', '<your-llm_key>')

def build_prompt(date: str=None, location: str=None, keywords: str=None, limit:int=10) -> str:
    prompt = [
        "你是一个新闻事件摘要生成器。",
        "根据给定的时间（YYYY-MM-DD 或 YYYY）和地点（城市/省/国家），列出最多 {} 条在该时空范围内对普通大众有广泛关注的事件。".format(limit),
        "每条以 JSON 对象返回：title, link(若无可用则填 null), summary(一句话), date, relevance(1-10), priority(low/medium/high)。",
        "要求：summary 一句话完整概括事件要点；不要返回模糊描述；如无法确认真实链接，可返回 null 并在 summary 中说明来源为 AI 生成。"
    ]
    if date:
        prompt.append(f"时间范围/日期：{date}")
    if location:
        prompt.append(f"地点：{location}")
    if keywords:
        prompt.append(f"关键词：{keywords}")
    return "\\n".join(prompt)

def call_llm_and_parse(prompt: str):
    # TODO: 用真实 LLM API 替换下面示例返回
    sample = [
        {
            "title": "示例：某地示范事件",
            "link": None,
            "summary": "AI 生成的示例事件摘要。",
            "date": "2024-01-01",
            "relevance": 8,
            "priority": "high"
        }
    ]
    return sample

def generate_events(date=None, location=None, keywords=None, limit=5):
    prompt = build_prompt(date, location, keywords, limit)
    events = call_llm_and_parse(prompt)
    return events

if __name__ == '__main__':
    ev = generate_events(date='2024', location='China', limit=3)
    print(json.dumps(ev, ensure_ascii=False, indent=2))
