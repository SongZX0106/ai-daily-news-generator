import requests
import json
from PyQt5.QtCore import QSettings

MODEL_NAME = "qwen-plus"

def get_api_key():
    settings = QSettings("daily_report_tool", "config")
    return settings.value("api_key", "")

def call_qwen(prompt):
    system_prompt = "你是一名专业的产品开发人员，请根据以下 Git 提交记录中的标题和描述信息，帮我生成一份简洁明了的开发日报。要求如下：1.使用中文编写；2.分点列出每个提交的主要改动；3.总结今日工作成果；4.控制在 200~300 字以内；"
    try:
        api_key = get_api_key()
        response = requests.post(
            "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
            json={
                "model": MODEL_NAME,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "stream": True
            },
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            timeout=60,
            stream=True
        )
        for line in response.iter_lines(decode_unicode=True):
            if not line or not line.startswith("data: "):
                continue
            line = line[len("data: "):].strip()
            if line == "[DONE]":
                break
            try:
                data = json.loads(line)
                choices = data.get("choices", [])
                if choices and "delta" in choices[0]:
                    content = choices[0]["delta"].get("content", "")
                    if content:
                        yield content
            except Exception:
                continue
    except Exception as e:
        yield f"调用失败: {str(e)}"