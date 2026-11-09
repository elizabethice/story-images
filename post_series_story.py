"""期間限定の連続ストーリー投稿(画像のみ)。

series17/01.jpg〜17.jpg を、START_DATE(JST)から1日1枚ずつ順番に投稿する。
期間外(開始前・17日を過ぎた後)に動いた場合は何も投稿せず正常終了する。
必要な環境変数は post_story.py と同じ(IG_USER_ID / IG_ACCESS_TOKEN / IMAGE_BASE_URL)。
"""
import os
import sys
import time
from datetime import date, datetime
from zoneinfo import ZoneInfo

import requests

GRAPH = "https://graph.instagram.com/v21.0"
START_DATE = date(2026, 11, 11)
COUNT = 17


def main() -> int:
    now = datetime.now(ZoneInfo("Asia/Tokyo"))
    n = (now.date() - START_DATE).days + 1  # 開始日が1
    if not 1 <= n <= COUNT:
        print(f"{now:%Y-%m-%d} JST は投稿期間外です(n={n})。何もしません")
        return 0

    user_id = os.environ["IG_USER_ID"]
    token = os.environ["IG_ACCESS_TOKEN"]
    base = os.environ["IMAGE_BASE_URL"].rstrip("/")
    image_url = f"{base}/series17/{n:02d}.jpg"
    print(f"{now:%Y-%m-%d %H:%M} JST -> series17/{n:02d}.jpg を投稿します")

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
