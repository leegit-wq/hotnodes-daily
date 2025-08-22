# AI-Driven Event Collection & Video Pipeline (Template)

**目的**：一个可直接上传到 GitHub 的仓库模板，实现：
- 根据自然语言（时间/地点/关键词）由 AI 生成事件素材（非直接爬站）
- 生成标准化 JSON（title, link, summary, date, relevance, priority）
- 生成视频草稿脚本（基于 ffmpeg 的示例）
- Agent 自动提交 PR，人工在手机端审阅并合并
- 合并后通过 Actions 部署到 Oracle VPS（deploy.sh）

**注意**：模板使用占位环境变量与 secrets，请在 GitHub Secrets 中配置（参见 `docs/secrets-example.md`）。
