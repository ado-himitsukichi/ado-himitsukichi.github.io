#!/usr/bin/env python3
"""YouTube 動画の説明欄を取る（クレジット抽出用）。使い方: python3 tools/yt_desc.py <id> ..."""
import json, re, sys, urllib.request
def desc(vid):
    s = urllib.request.urlopen(urllib.request.Request("https://www.youtube.com/watch?v=" + vid + "&hl=ja", headers={"User-Agent": "Mozilla/5.0", "Accept-Language": "ja"}), timeout=30).read().decode("utf-8", "ignore")
    m = re.search(r"ytInitialPlayerResponse = (\{.*?\});(?:var|</script>)", s)
    d = json.loads(m.group(1))["videoDetails"]
    return d.get("shortDescription", "")
if __name__ == "__main__":
    for v in sys.argv[1:]:
        print("==", v); print(desc(v))
