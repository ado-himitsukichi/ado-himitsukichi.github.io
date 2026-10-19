#!/usr/bin/env python3
"""YouTube 検索の上位を「動画ID | タイトル | チャンネル名」で出す（タイアップ先の公式動画を探す用）。
使い方: python3 tools/yt_search.py "検索語" ..."""
import json, re, sys, urllib.parse, urllib.request

def search(q, n=8):
    url = "https://www.youtube.com/results?hl=ja&gl=JP&search_query=" + urllib.parse.quote(q)
    s = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept-Language": "ja"}), timeout=20).read().decode("utf-8", "ignore")
    d = json.loads(re.search(r"var ytInitialData = (\{.*?\});</script>", s).group(1))
    out = []
    def walk(o):
        if isinstance(o, dict):
            if "videoRenderer" in o:
                v = o["videoRenderer"]
                out.append((v["videoId"], "".join(r.get("text", "") for r in v["title"]["runs"]),
                            "".join(r.get("text", "") for r in v.get("ownerText", {}).get("runs", [])),
                            (v.get("lengthText") or {}).get("simpleText", "")))
            for x in o.values(): walk(x)
        elif isinstance(o, list):
            for x in o: walk(x)
    walk(d)
    return out[:n]

if __name__ == "__main__":
    for q in sys.argv[1:]:
        print("==", q)
        for vid, t, ch, ln in search(q):
            print(f"  {vid} | {t[:60]} | {ch} | {ln}")
