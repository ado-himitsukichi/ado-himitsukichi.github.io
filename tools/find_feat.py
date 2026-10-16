#!/usr/bin/env python3
"""feat. 曲の公式動画を探す。引数: "アーティスト|曲名" ...
YouTube は検索結果のうち「タイトルに曲名」かつ「チャンネル名にアーティスト名（の一部）」の動画、
ニコニコ動画はスナップショット検索 API でタイトルに曲名と Ado を含む動画を返す。"""
import json, re, sys, unicodedata, urllib.parse, urllib.request

UA = {"User-Agent": "Mozilla/5.0", "Accept-Language": "ja"}
n = lambda s: re.sub(r"[\s　・、。!！?？.\-]", "", unicodedata.normalize("NFKC", s)).lower()

def yt(q):
    s = urllib.request.urlopen(urllib.request.Request("https://www.youtube.com/results?hl=ja&gl=JP&search_query=" + urllib.parse.quote(q), headers=UA), timeout=20).read().decode("utf-8", "ignore")
    d = json.loads(re.search(r"var ytInitialData = (\{.*?\});</script>", s).group(1))
    out = []
    def walk(o):
        if isinstance(o, dict):
            if "videoRenderer" in o:
                v = o["videoRenderer"]
                out.append({"id": v["videoId"], "title": "".join(r.get("text", "") for r in v["title"]["runs"]),
                            "ch": "".join(r.get("text", "") for r in v.get("ownerText", {}).get("runs", []))})
            for x in o.values(): walk(x)
        elif isinstance(o, list):
            for x in o: walk(x)
    walk(d)
    return out

def nico(q):
    url = ("https://snapshot.search.nicovideo.jp/api/v2/snapshot/video/contents/search?targets=title&fields=contentId,title,viewCounter,userId"
           "&_sort=-viewCounter&_limit=10&_context=ado-himitsukichi&q=" + urllib.parse.quote(q))
    return json.loads(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=20).read()).get("data", [])

res = {}
for arg in sys.argv[1:]:
    artist, song = arg.split("|")
    hit = None
    for v in yt(f"{artist} {song} Ado"):
        if n(song) in n(v["title"]) and any(n(a) in n(v["ch"]) for a in re.split(r"[/／,]", artist) if a):
            hit = v; break
    nh = None
    for v in nico(f"{song} Ado"):
        if n(song) in n(v["title"]):
            nh = v; break
    res[song] = {"artist": artist, "yt": hit, "nico": nh and {"id": nh["contentId"], "title": nh["title"], "views": nh["viewCounter"]}}
print(json.dumps(res, ensure_ascii=False, indent=1))
