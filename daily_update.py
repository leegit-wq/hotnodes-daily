import json, asyncio, aiohttp, base64, re
from datetime import datetime

# 📥 节点源列表（支持 base64 或明文）
SOURCE_URLS = [
    "https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/sub/splitted/vmess",
    "https://raw.githubusercontent.com/Leon406/SubCrawler/main/sub/ProxyNode_Subscribe_1.txt",
    "https://raw.githubusercontent.com/yebekhe/TelegramV2rayCollector/master/sub/normal/v2ray",
    "https://raw.githubusercontent.com/ermaozi/get_subscribe/main/subscribe/v2ray.txt",
    "https://raw.githubusercontent.com/freefq/free/master/v2"
]

GPT_TEST_URL = "https://api.openai.com/v1/models"

# 解码 vmess base64 内容
def decode_base64(data):
    data += '=' * (4 - len(data) % 4)
    return base64.b64decode(data).decode('utf-8', errors='ignore')

# 提取 vmess:// 链接
def extract_vmess_links(text):
    return re.findall(r'vmess://[a-zA-Z0-9+/=]+', text)

# 自动识别 Base64 或明文格式
def smart_decode_links(text):
    try:
        decoded = decode_base64(text)
        return extract_vmess_links(decoded)
    except:
        return extract_vmess_links(text)

# 测试 GPT 接口可达性（使用代理）
async def test_gpt_access(proxy_url):
    try:
        conn = aiohttp.ProxyConnector.from_url(proxy_url)
        async with aiohttp.ClientSession(connector=conn) as session:
            async with session.get(GPT_TEST_URL, timeout=8) as resp:
                return resp.status in [200, 401]
    except:
        return False

# 主流程
async def main():
    all_nodes = []
    print("📥 开始抓取节点源")
    async with aiohttp.ClientSession() as session:
        for url in SOURCE_URLS:
            try:
                async with session.get(url, timeout=10) as resp:
                    text = await resp.text()
                    links = smart_decode_links(text)
                    print(f"✅ 从 {url} 抓取 {len(links)} 条链接")
                    all_nodes.extend(links)
            except Exception as e:
                print(f"⚠️ 抓取失败：{url}，原因：{e}")

    print(f"🧪 总共待测试节点数：{len(all_nodes)}")
    results = []
    tested = set()

    for link in all_nodes:
        try:
            raw = decode_base64(link.replace("vmess://", ""))
            node = json.loads(raw)
            addr = node['add']
            port = node['port']
            if (addr, port) in tested:
                continue
            tested.add((addr, port))
            proxy = f"http://{addr}:{port}"

            ok = await test_gpt_access(proxy)
            if ok:
                print(f"✅ {addr}:{port} 可访问 GPT")
                results.append({
                    "name": node.get("ps", f"{addr}:{port}"),
                    "protocol": "vmess",
                    "link": link,
                    "gpt_accessible": True,
                    "latency_ms": -1,
                    "last_tested": datetime.utcnow().isoformat() + "Z"
                })
            else:
                print(f"❌ {addr}:{port} 无法访问 GPT")

            if len(results) >= 10:
                break
        except Exception:
            continue

    if results:
        with open("nodes.json", "w") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"✅ 写入 {len(results)} 条可用节点到 nodes.json")
    else:
        print("⚠️ 没有测试通过的节点，未生成 nodes.json")

# 异步运行
asyncio.run(main())