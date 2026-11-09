"""毎日のストーリーズ自動投稿(5枚ローテーション・画像のみ)。

rotation/1.jpg〜5.jpg を、日付ベースで1日1枚ずつ順番に投稿する(5日で一周)。
曜日別の投稿(post_story.py)とは別枠。
必要な環境変数は post_story.py と同じ(IG_USER_ID / IG_ACCESS_TOKEN / IMAGE_BASE_URL)。
"""
import os
import sys
import time
from datetime import datetime
from zoneinfo import ZoneInfo

import requests

GRAPH = "https://graph.instagram.com/v21.0"
COUNT = 5


def main() -> int:
    user_id = os.environ["IG_USER_ID"]
    token = os.environ["IG_ACCESS_TOKEN"]
    base = os.environ["IMAGE_BASE_URL"].rstrip("/")

    now = datetime.now(ZoneInfo("Asia/Tokyo"))
    n = now.date().toordinal() % COUNT + 1  # 1〜5
    image_url = f"{base}/rotation/{n}.jpg"
    print(f"{now:%Y-%m-%d %H:%M} JST -> rotation/{n}.jpg を投稿します")

    r = requests.post(
        f"{GRAPH}/{user_id}/media",
        data={"image_url": image_url, "media_type": "STORIES", "access_token": token},
        timeout=60,
    )
    if not r.ok:
        print("コンテナ作成に失敗:", r.status_code, r.text.replace(token, "***"))
        return 1
    creation_id = r.json()["id"]

    for _ in range(10):
        s = requests.get(
            f"{GRAPH}/{creation_id}",
            params={"fields": "status_code", "access_token": token},
            timeout=60,
        )
        status = s.json().get("status_code") if s.ok else None
        if status in (None, "FINISHED"):
            break
        if status == "ERROR":
            print("画像の処理でエラー:", s.text.replace(token, "***"))
            return 1
        time.sleep(3)

    p = requests.post(
        f"{GRAPH}/{user_id}/media_publish",
        data={"creation_id": creation_id, "access_token": token},
        timeout=60,
    )
    if not p.ok:
        print("公開に失敗:", p.status_code, p.text.replace(token, "***"))
        return 1
    print("投稿完了:", p.json().get("id"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
