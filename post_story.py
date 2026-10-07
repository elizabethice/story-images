"""毎日のストーリーズ自動投稿(画像のみ)。

曜日ごとの画像(mon.png〜sun.png)をInstagramのストーリーズに投稿する。
必要な環境変数:
  IG_USER_ID       Instagramアカウント(elizabeth_icequeen)のID
  IG_ACCESS_TOKEN  Instagramのアクセストークン(絶対にコードやログに書かない)
  IMAGE_BASE_URL   画像の公開URLの共通部分
                   例: https://raw.githubusercontent.com/elizabethice/story-images/main
"""
import os
import sys
import time
from datetime import datetime
from zoneinfo import ZoneInfo

import requests

GRAPH = "https://graph.instagram.com/v21.0"
DAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]


def main() -> int:
    user_id = os.environ["IG_USER_ID"]
    token = os.environ["IG_ACCESS_TOKEN"]
    base = os.environ["IMAGE_BASE_URL"].rstrip("/")

    now = datetime.now(ZoneInfo("Asia/Tokyo"))
    day = DAYS[now.weekday()]
    image_url = f"{base}/{day}.png"
    print(f"{now:%Y-%m-%d %H:%M} JST -> {day}.png を投稿します")

    # 1) ストーリー用のメディアコンテナを作る
    r = requests.post(
        f"{GRAPH}/{user_id}/media",
        data={"image_url": image_url, "media_type": "STORIES", "access_token": token},
        timeout=60,
    )
    if not r.ok:
        print("コンテナ作成に失敗:", r.status_code, r.text.replace(token, "***"))
        return 1
    creation_id = r.json()["id"]

    # 2) 処理完了を少し待つ
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

    # 3) 公開する
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
