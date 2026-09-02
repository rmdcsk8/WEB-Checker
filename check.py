import os
import requests
from bs4 import BeautifulSoup

# 監視対象のURLリスト（トップページと専門医試験ページ）
TARGETS = [
    {
        "name": "日本在宅医療連合学会（トップページお知らせ）",
        "url": "https://www.jahcm.org/",
        "file": "last_top.txt"
    },
    {
        "name": "専門医試験受験情報",
        "url": "https://www.jahcm.org/exam_info.html",
        "file": "last_exam.txt"
    }
]

SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL")

def get_page_text(url):
    try:
        res = requests.get(url, timeout=15)
        res.encoding = res.apparent_encoding
        soup = BeautifulSoup(res.text, "html.parser")
        # スクリプトやスタイルシートを除外してテキストのみ抽出
        for script in soup(["script", "style"]):
            script.extract()
        return soup.get_text().strip()
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def main():
    for target in TARGETS:
        current_text = get_page_text(target["url"])
        if not current_text:
            continue

        last_text = ""
        if os.path.exists(target["file"]):
            with open(target["file"], "r", encoding="utf-8") as f:
                last_text = f.read()

        # 前回の保存データがあり、内容が変わっていたらSlackへ通知
        if last_text and current_text != last_text:
            payload = {
                "text": f"📢 *【更新検知】{target['name']}*\nページ内でテキストの変更が検出されました。\n<{target['url']}|Webサイトを確認する>"
            }
            requests.post(SLACK_WEBHOOK_URL, json=payload)

        # 最新のテキストをファイルに保存
        with open(target["file"], "w", encoding="utf-8") as f:
            f.write(current_text)

if __name__ == "__main__":
    main()
