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
