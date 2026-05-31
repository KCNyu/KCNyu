import json
import re
import sys

import requests
from bs4 import BeautifulSoup

README_PATH = "README.md"
URL_TOKEN = "shengyuli"
PROFILE_URL = f"https://www.zhihu.com/people/{URL_TOKEN}"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

START = "<!--START_SECTION:zhihu-followers-->"
END = "<!--END_SECTION:zhihu-followers-->"


def fmt(n):
    """Format an int with thousands separators, matching the existing style."""
    return f"{int(n):,}"


def parse_existing(content):
    """Pull the last-known numbers out of the README so a failed fetch never wipes them."""
    section = content.split(START, 1)[-1].split(END, 1)[0]
    nums = re.findall(r"[\d,]+", section)
    if len(nums) == 4:
        return [int(n.replace(",", "")) for n in nums]
    return None


def fetch_counts():
    """Return (agree, like, collection, follower) from Zhihu's embedded initial data."""
    r = requests.get(PROFILE_URL, headers=HEADERS, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.content, "html.parser")
    raw = soup.find("script", id="js-initialData")
    if not raw or not raw.string:
        raise RuntimeError("js-initialData not found (page layout changed or blocked)")
    data = json.loads(raw.string)
    user = data["initialState"]["entities"]["users"][URL_TOKEN]
    return (
        user["voteupCount"],      # 赞同
        user.get("likesCount", user.get("thankedCount", 0)),  # 喜欢
        user["favoritedCount"],   # 收藏
        user["followerCount"],    # 关注者
    )


def main():
    with open(README_PATH, "r", encoding="utf-8") as fh:
        content = fh.read()

    fallback = parse_existing(content)
    try:
        agree, like, collection, follower = fetch_counts()
    except Exception as exc:  # noqa: BLE001 - never let a fetch error corrupt the README
        if fallback is None:
            print(f"::error::Zhihu fetch failed and no previous data to keep: {exc}")
            sys.exit(1)
        print(f"::warning::Zhihu fetch failed, keeping previous numbers: {exc}")
        agree, like, collection, follower = fallback

    zhihu = "获得{}次赞同，{}次喜欢，{}次收藏，{}个关注".format(
        fmt(agree), fmt(like), fmt(collection), fmt(follower)
    )
    print(zhihu)

    new_content = re.sub(
        rf"(?<={re.escape(START)})[\s\S]*(?={re.escape(END)})",
        f"\n{zhihu}\n",
        content,
    )
    with open(README_PATH, "w", encoding="utf-8") as fh:
        fh.write(new_content)


if __name__ == "__main__":
    main()
