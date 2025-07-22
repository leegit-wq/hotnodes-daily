import json, asyncio, aiohttp, time, base64, re
from datetime import datetime

SOURCE_URLS = [
    "https://raw.githubusercontent.com/ermaozi/get_subscribe/main/subscribe/v2ray.txt",
    "https://raw.githubusercontent.com/freefq/free/master/v2",
]

GPT_TEST_URL = "https://api.openai.com/v1/models"

async def test_gpt_access(proxy_url):
    try:
        conn = aiohttp.ProxyConnector.from_url(proxy_url)
        async with aiohttp.ClientSession(connector=conn) as session:
            async with session.get(GPT_TEST_URL, timeout=8) as resp:
                return resp.status == 200 or resp.status == 401
    except:
        return False

def decode_base64(data):
    data += '=' * (4 - len(data) % 4)
    return base64.b64decode(data).decode('utf-8', errors='ignore')

def extract_vmess_links(text):
    return re.findall(r'vmess://[a-zA-Z0-9+/=]+', text)

async def main():
    all_nodes = []
    for url in SOURCE_URLS:
        try:
            raw = await aiohttp.ClientSession().get(url)
            text = await raw.text()
            all_nodes += extract_vmess_links(text)
        except:
            continue

    results = []
    tested = set()
    for link in all_nodes:
        try:
            raw = decode_base64(link.replace("vmess://", ""))
            node = json.loads(raw)
            addr, port = node['add'], node['port']
            proxy = f"http://{addr}:{port}"
            if (addr, port) in tested:
                continue
            tested.add((addr, port))
            ok = await test_gpt_access(proxy)
            if ok:
                results.append({
                    "name": node.get("ps", f"{addr}:{port}"),
                    "protocol": "vmess",
                    "link": link,
                    "gpt_accessible": True,
                    "latency_ms": -1,
                    "last_tested": datetime.utcnow().isoformat() + "Z"
                })
            if len(results) >= 10:
                break
        except:
            continue

    with open("nodes.json", "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

asyncio.run(main())
