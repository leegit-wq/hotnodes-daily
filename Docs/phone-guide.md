# 手机端快速操作指南（精简）
1. Fork 仓库后在 GitHub Settings -> Secrets 中配置：LLM_API_KEY, ORACLE_HOST, ORACLE_USER, ORACLE_SSH_KEY.
2. 在仓库 Issues 中新建 Issue, 使用模板填写：日期、地点、关键词、是否需要视频草稿.
3. 在 GitHub App 上打开该 Issue，点击右侧的 `Run workflow` 或直接 label 为 `autogen'.
4. 等待 Actions 完成（可通过 GitHub App 查看 workflow 日志或在 PR 中查看 artifact）。
5. 审阅生成的 PR（包含 data/generated_events.json），如符合要求则合并，合并触发 deploy。
