import re
import json
import time
import html
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE = "https://www.boatrace.jp/owpc/pc/data/racersearch/result"

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (compatible; BOATRACE-Sukigao9/1.0)"
})

items = {}

for lo in range(2000, 5600, 100):
    hi = lo + 99

    try:
        r = session.get(
            BASE,
            params={
                "prevpgid": "TDAT320",
                "toban_left": f"{lo:04d}",
                "toban_right": f"{hi:04d}",
            },
            timeout=30,
        )
        r.raise_for_status()

        soup = BeautifulSoup(r.text, "html.parser")

    except Exception as e:
        print("skip", lo, hi, e)
        continue

    # レーサー検索結果の各プロフィールリンクを探す
    for a in soup.find_all("a", href=True):

        href = a.get("href", "")

        if "racersearch/profile" not in href:
            continue

        # リンク周辺のテキストから登録番号・名前・級別を取得
        text = " ".join(a.stripped_strings)

        parent = a.parent
        parent_text = (
            " ".join(parent.stripped_strings)
            if parent
            else text
        )

        # 4桁の登録番号
        match = re.search(r"(?<!\d)(\d{4})(?!\d)", parent_text)

        if not match:
            continue

        racer_id = match.group(1)

        # 写真
        img = a.find("img")

        photo = ""

        if img:
            src = img.get("src") or img.get("data-src")

            if src:
                photo = urljoin(r.url, src)

        # 名前
        name = text

        name = re.sub(
            r"^\s*\d{4}\s*",
            "",
            name
        ).strip()

        # 級別
        grade_match = re.search(
            r"級別\s*[：:]\s*(A1|A2|B1|B2)",
            parent_text
        )

        grade = grade_match.group(1) if grade_match else ""

        if racer_id not in items:
            items[racer_id] = {
                "id": racer_id,
                "name": name,
                "grade": grade,
                "photo": photo,
                "profile": urljoin(r.url, href),
            }

    print(lo, hi, "racers:", len(items))

    time.sleep(0.5)

print("TOTAL RACERS:", len(items))

with open("racers.js", "w", encoding="utf-8") as f:
    f.write(
        "window.RACERS="
        + json.dumps(
            list(items.values()),
            ensure_ascii=False,
            separators=(",", ":")
        )
        + ";\n"
    )
