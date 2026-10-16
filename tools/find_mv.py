#!/usr/bin/env python3
"""曲名から Ado 公式チャンネル（@Ado1024 = UCln9P4Qm3-EAY4aiEPmRwEA）の動画 ID を YouTube 検索で探す。
使い方: python3 tools/find_mv.py "うっせぇわ" "踊" ...  → JSON {曲名: {id, title}} を表示
"""
import json, re, sys, urllib.parse, urllib.request

def search(q):
    url = "https://www.youtube.com/results?hl=ja&gl=JP&search_query=" + urllib.parse.quote(q)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept-Language": "ja"})
    s = urllib.request.urlopen(req, timeout=20).read().decode("utf-8", "ignore")
    m = re.search(r"var ytInitialData = (\{.*?\});</script>", s)
    if not m:
        return []
    out = []
    def walk(o):
        if isinstance(o, dict):
            if "videoRenderer" in o:
                v = o["videoRenderer"]
                owner = json.dumps(v.get("ownerText", {}), ensure_ascii=False)
                title = "".join(r.get("text", "") for r in v.get("title", {}).get("runs", []))
                out.append({"id": v.get("videoId"), "title": title, "official": "UCln9P4Qm3-EAY4aiEPmRwEA" in owner})
            for x in o.values():
                walk(x)
        elif isinstance(o, list):
            for x in o:
                walk(x)
    walk(json.loads(m.group(1)))
    return out

res = {}
for song in sys.argv[1:]:
    hits = [h for h in search("Ado " + song) if h["official"]]
    # 曲名を含む公式動画を優先（MV > 歌ってみた > ライブ）
    pick = None
    for h in hits:
        if song in h["title"] and "LIVE" not in h["title"].upper() and "short" not in h["title"].lower():
            pick = h; break
    if not pick:
        for h in hits:
            if song in h["title"]:
                pick = h; break
    res[song] = pick and {"id": pick["id"], "title": pick["title"]}
print(json.dumps(res, ensure_ascii=False, indent=1))
