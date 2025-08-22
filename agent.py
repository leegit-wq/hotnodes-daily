# agent.py - 轻量 Agent 模板
# 功能：基于 Issue 描述生成/修改代码 -> 运行 tests -> 创建 PR (使用 GITHUB_TOKEN)
# 注意：本脚本是模板，需要在 Actions 环境或本地按 README 配置 Secrets 后运行.
import os, json, subprocess, sys
from pathlib import Path

GITHUB_REPO = os.getenv("GITHUB_REPOSITORY")  # owner/repo
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # Actions 自动注入或放在 secrets
LLM_API = os.getenv("LLM_API_KEY", "<your-llm-key>")  # 火山引擎/OpenAI 等

def call_llm(prompt):
    # 简单示例：将来替换为真实 API 调用
    sample = {
        "events": [
            {
                "title": "示例事件：某地某日发生重大活动",
                "link": "https://example.com/event",
                "summary": "这是一个由 AI 根据时间地点生成的示例事件摘要。",
                "date": "2024-01-01",
                "relevance": 7,
                "priority": "high"
            }
        ]
    }
    return sample

def run_tests():
    # 运行 pytest，确保代码修改通过基础测试
    r = subprocess.run(["pytest", "-q"], capture_output=True, text=True)
    print(r.stdout)
    print(r.stderr, file=sys.stderr)
    return r.returncode == 0

def create_pr(branch_name, commit_message):
    subprocess.check_call(["git", "config", "--global", "user.email", "agent@example.com"])
    subprocess.check_call(["git", "config", "--global", "user.name", "ai-agent"])
    subprocess.check_call(["git", "checkout", "-b", branch_name])
    subprocess.check_call(["git", "add", "."])
    subprocess.check_call(["git", "commit", "-m", commit_message])
    subprocess.check_call(["git", "push", "-u", "origin", branch_name])
    print("Created branch and pushed. Please configure PR creation in workflow or use `gh` CLI.")

def main():
    prompt = os.getenv("ISSUE_BODY", "请生成指定日期和地点的事件并按 schema 输出。")
    print("Calling LLM with prompt:", prompt)
    result = call_llm(prompt)
    Path("data").mkdir(exist_ok=True)
    with open("data/generated_events.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    ok = run_tests()
    if not ok:
        print("Tests failed. Agent will not create PR.")
        sys.exit(2)
    import time
    branch = f"ai-agent/gen-{int(time.time())}"
    create_pr(branch, "chore: ai generated events and pipeline updates")

if __name__ == '__main__':
    main()
