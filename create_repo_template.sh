#!/usr/bin/env bash
set -e
ROOT="ai-agent-template"
rm -rf "$ROOT"
mkdir -p "$ROOT"

echo "Creating files in $ROOT ..."

# README.md
cat > "$ROOT/README.md" <<'README'
# AI-Driven Event Collection & Video Pipeline (Template)

**目的**：一个可直接上传到 GitHub 的仓库模板，实现：
- 根据自然语言（时间/地点/关键词）由 AI 生成事件素材（非直接爬站）
- 生成标准化 JSON（title, link, summary, date, relevance, priority）
- 生成视频草稿脚本（基于 ffmpeg 的示例）
- Agent 自动提交 PR，人工在手机端审阅并合并
- 合并后通过 Actions 部署到 Oracle VPS（deploy.sh）

**注意**：模板使用占位环境变量与 secrets，请在 GitHub Secrets 中配置（参见 `docs/secrets-example.md`）。
README

# .gitignore
cat > "$ROOT/.gitignore" <<'GITIGNORE'
__pycache__/
.env
.venv
*.pyc
*.log
artifacts/
data/
GITIGNORE

# agent.py
cat > "$ROOT/agent.py" <<'AGENT'
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
AGENT

# scrapers/ai_scraper.py
mkdir -p "$ROOT/scrapers"
cat > "$ROOT/scrapers/ai_scraper.py" <<'AISCRAPER'
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
AISCRAPER

# pipeline/video_pipeline.py
mkdir -p "$ROOT/pipeline"
cat > "$ROOT/pipeline/video_pipeline.py" <<'VIDPIPE'
# video_pipeline.py - 简单示例：把 JSON 中的事件生成旁白脚本并输出 ffmpeg 调用示例
import json
from pathlib import Path

def load_events(path='data/generated_events.json'):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f).get('events', [])

def build_tts_text(event):
    return f"{event.get('title')}。{event.get('summary')} 发生于 {event.get('date')}。"

def generate_video_stub(output_dir='artifacts'):
    events = load_events()
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    for i, e in enumerate(events):
        txt = build_tts_text(e)
        out_txt = Path(output_dir)/f"scene_{i+1}.txt"
        out_txt.write_text(txt, encoding='utf-8')
    print('Generated video stub texts in', output_dir)

if __name__ == '__main__':
    generate_video_stub()
VIDPIPE

# tests/test_schema.py
mkdir -p "$ROOT/tests"
cat > "$ROOT/tests/test_schema.py" <<'TESTS'
import json
def test_generated_schema():
    with open('data/generated_events.json','r',encoding='utf-8') as f:
        data = json.load(f)
    assert 'events' in data
    for e in data['events']:
        assert 'title' in e and isinstance(e['title'], str)
        assert 'summary' in e and isinstance(e['summary'], str)
        assert 'date' in e
        assert 'relevance' in e
TESTS

# workflows
mkdir -p "$ROOT/.github/workflows"
cat > "$ROOT/.github/workflows/agent.yml" <<'AGENTWF'
name: AI Agent - generate events
on:
  workflow_dispatch:
  issues:
    types: [opened, labeled]
jobs:
  run-agent:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install deps
        run: |
          python -m pip install --upgrade pip
          pip install pytest requests
      - name: Run agent.py
        env:
          ISSUE_BODY: ${{ github.event.issue.body || '' }}
          GITHUB_REPOSITORY: ${{ github.repository }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          LLM_API_KEY: ${{ secrets.LLM_API_KEY }}
        run: |
          python agent.py
      - name: Upload generated artifacts
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: generated-events
          path: data/generated_events.json
AGENTWF

cat > "$ROOT/.github/workflows/deploy.yml" <<'DEPLOYWF'
name: Deploy to Oracle
on:
  push:
    branches:
      - main
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to Oracle via SSH
        uses: appleboy/ssh-action@v0.1.6
        with:
          host: ${{ secrets.ORACLE_HOST }}
          username: ${{ secrets.ORACLE_USER }}
          key: ${{ secrets.ORACLE_SSH_KEY }}
          port: ${{ secrets.ORACLE_SSH_PORT || '22' }}
          script: |
            set -e
            cd ~/ai_agent_deploy || mkdir -p ~/ai_agent_deploy && cd ~/ai_agent_deploy
            git init || true
            git remote remove origin || true
            git remote add origin https://github.com/${{ github.repository }}
            git fetch --depth=1 origin main
            git checkout -f main
            ./deploy/deploy.sh || true
DEPLOYWF

# deploy script
mkdir -p "$ROOT/deploy"
cat > "$ROOT/deploy/deploy.sh" <<'DEPLOYSH'
#!/usr/bin/env bash
set -e
echo "Starting deploy script..."
python3 -m venv venv
. venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt || true
# Register cron job: daily 02:00 run agent
(crontab -l 2>/dev/null; echo "0 2 * * * cd $(pwd) && /usr/bin/python3 $(pwd)/agent.py >> $(pwd)/agent.log 2>&1") | crontab -
echo "Deploy finished."
DEPLOYSH
chmod +x "$ROOT/deploy/deploy.sh"

# requirements.txt
cat > "$ROOT/requirements.txt" <<'REQ'
requests
pytest
REQ

# docs
mkdir -p "$ROOT/docs"
cat > "$ROOT/docs/phone-guide.md" <<'PHONEDOC'
# 手机端快速操作指南（精简）
1. Fork 仓库后在 GitHub Settings -> Secrets 中配置：LLM_API_KEY, ORACLE_HOST, ORACLE_USER, ORACLE_SSH_KEY.
2. 在仓库 Issues 中新建 Issue, 使用模板填写：日期、地点、关键词、是否需要视频草稿.
3. 在 GitHub App 上打开该 Issue，点击右侧的 `Run workflow` 或直接 label 为 `autogen'.
4. 等待 Actions 完成（可通过 GitHub App 查看 workflow 日志或在 PR 中查看 artifact）。
5. 审阅生成的 PR（包含 data/generated_events.json），如符合要求则合并，合并触发 deploy。
PHONEDOC

cat > "$ROOT/docs/secrets-example.md" <<'SECRETSDOC'
# Secrets 列表（示例）
- LLM_API_KEY : LLM 服务密钥（火山引擎 / OpenAI）
- ORACLE_HOST : Oracle VPS IP 或域名
- ORACLE_USER : Oracle VPS 登录用户名（例如 opc 或 ubuntu）
- ORACLE_SSH_KEY : 私钥（PEM 格式），用于 Actions SSH Action
- ORACLE_SSH_PORT : (可选) SSH 端口，默认 22
- GITHUB_TOKEN : Actions 自动注入，通常不需手动设置
SECRETSDOC

# Create zip
ZIP="ai-agent-template.zip"
rm -f "$ZIP"
zip -r "$ZIP" "$ROOT" >/dev/null
echo "Created $ZIP in $(pwd)"
echo "Done."
