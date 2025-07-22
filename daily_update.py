import requests, re, base64, json, subprocess
from datetime import datetime
from urllib.parse import unquote
from pathlib import Path

# 要抓取的 Telegram 频道（网页版）
TELEGRAM_CHANNELS = [
    "https://t.me/s/GPT_v2ray_daily",
    "https://t.me/s/free4gpt_node",
    "https://t.me/s/v2ray_top1",
    "https://t.me/s/GPTfree4u",
]

# 判断节点是否可访问 GPT 接口
def test_node(node_str: str) -> bool:
    try:
        result = subprocess.run(
            ["./v2ray-test", node_str, "https://api.openai.com/v1/models", "5"],
            capture_output=True, text=True, timeout=30
        )
        return "GPT_ACCESSIBLE" in result.stdout
    except Exception:
        return False

# 提取所有节点链接（支持明文或 Base64 编码）
def extract_links(html: str):
    links = set()
    raw_links = re.findall(r'(vmess|vless|trojan)://[^\s<]+', html, re.IGNORECASE)
    links.update(raw_links)

    # 查找 Base64 块（可能包含多个链接）
    base64_blocks = re.findall(r'([A-Za-z0-9+/=]{100,})', html)
    for b64 in base64_blocks:
        try:
            decoded = base64.b64decode(b64 + "===").decode(errors="ignore")
            for l in re.findall(r'(vmess|vless|trojan)://[^\s<]+', decoded, re.IGNORECASE):
                links.add(l.strip())
        except Exception:
            continue
    return list(links)

def fetch_all_links():
    all_links = []
    for url in TELEGRAM_CHANNELS:
        try:
            print(f"📥 抓取频道：{url}")
            resp = requests.get(url, timeout=15)
            resp.encoding = 'utf-8'
            links = extract_links(resp.text)
            print(f"✅ 抓取成功，共找到 {len(links)} 条链接")
            all_links.extend(links)
        except Exception as e:
            print(f"❌ 抓取失败：{url} -> {e}")
    return list(set(all_links))

# 生成最终 JSON 并保存
def save_nodes_json(nodes: list):
    timestamp = datetime.utcnow().isoformat()
    node_objs = [{"url": node, "checked_at": timestamp} for node in nodes]
    with open("nodes.json", "w", encoding="utf-8") as f:
        json.dump(node_objs, f, ensure_ascii=False, indent=2)
    print(f"✅ 已保存 nodes.json，共 {len(nodes)} 条")

# 主执行逻辑
def main():
    all_links = fetch_all_links()
    print(f"🧪 开始测试 {len(all_links)} 条节点的 GPT 可达性")
    valid_nodes = []

    for i, node in enumerate(all_links):
        print(f"🔹 测试第 {i+1}/{len(all_links)} 条")
        if test_node(node):
            print("✅ 可访问 GPT")
            valid_nodes.append(node)
        else:
            print("❌ 无法访问 GPT")

    if valid_nodes:
        save_nodes_json(valid_nodes)
    else:
        print("⚠️ 本次未发现可用节点，未生成 JSON 文件")

if __name__ == "__main__":
    main()