#!/usr/bin/env python3
"""歌ってみた（ニコニコ動画 user/39170211 と YouTube @Ado1024）を曲ごとにまとめ、
最初に投稿された日で data/timeline.json（cat: cover）と data/mv.json に入れる。
入力: data/raw/nico_*.json（nvapi）と data/raw/yt_covers.json（[{id,title,date}]）。何度流しても重複しない。"""
import glob, json, os, re, unicodedata
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = lambda *p: os.path.join(ROOT, "data", *p)

def parts(title):
    t = unicodedata.normalize("NFKC", title)
    variant = ""
    for pat, lab in [(r"ワンコーラス", "ワンコーラス"), (r"long ver", "long ver."), (r"【Re】", "Re")]:
        if re.search(pat, t, re.I):
            variant = lab
    t = re.sub(r"【(Ado|Adoと[^】]*|Re|Cover|ワンコーラス|オリジナルMV|初投稿|春だけど|茨薔薇咲アドヲ|合唱)】", "", t)
    t = re.sub(r"【Ado\w*】|\[[^\]]*\]|/\s*Ado\w*|#\S+", "", t)
    t = re.sub(r"【[^】]*】", "", t)
    t = re.sub(r"\(long ver\.\)|\(Basket Worm\)|ver\.\s*Ado.*|cover\s*\(.*\)|\(Limited Special Track\)", "", t, flags=re.I)
    t = re.sub(r"\s*feat\.?\s*Ado", "", t, flags=re.I)
    t = re.sub(r"歌ってみた|歌いました|Ado", "", t)
    name = t.strip(" 　,、「」").strip()
    return name, variant

def key(name):
    return re.sub(r"[\s　・、。!！?？,★’'&＆]", "", name).lower()

def main():
    mv = json.load(open(D("mv.json"), encoding="utf-8"))
    T = json.load(open(D("timeline.json"), encoding="utf-8"))
    songs = {}
    for f in sorted(glob.glob(D("raw", "nico_*.json"))):
        for it in json.load(open(f))["data"]["items"]:
            x = it["essential"]
            # ニコニコにはオリジナル曲（【Ado】うっせぇわ など）も上がっているので、歌ってみただけを拾う
            if not (re.search(r"歌ってみた|歌いました|feat\.? ?Ado", x["title"]) or x["registeredAt"][:10] < "2020-10-23"):
                continue
            name, var = parts(x["title"])
            if not name:
                continue
            songs.setdefault(key(name), {"name": name, "v": []})["v"].append(
                {"svc": "nico", "sm": x["id"], "title": x["title"], "date": x["registeredAt"][:10],
                 "thumb": x["thumbnail"].get("middleUrl") or x["thumbnail"]["url"], "var": var})
    for x in json.load(open(D("raw", "yt_covers.json"))):
        name, var = parts(x["title"])
        songs.setdefault(key(name), {"name": name, "v": []})["v"].append(
            {"svc": "yt", "id": x["id"], "title": x["title"], "date": x["date"], "var": var})
    # 既存の「ニコニコのみ」年表と mv は作り直す
    T = [e for e in T if not (e["cat"] == "niconico" and "（ニコニコ動画のみ）" in e["title"]) and e["cat"] != "cover"]
    for k in [k for k, m in mv.items() if m["kind"] in ("ニコニコのみ",) or k.startswith("cover:")]:
        del mv[k]
    # 年表の既存項目で歌ってみたにあたるもの（君の体温 など）は、その項目に動画をつける
    first_post = {e["date"]: e for e in T if e["cat"] == "niconico"}
    n_new = 0
    for sk, s in songs.items():
        if not s["name"] or sk in ("新人歌い手グループビバハピ",):
            continue
        keys = []
        bykey = {}
        for v in sorted(s["v"], key=lambda v: v["date"]):
            vk = s["name"] + (f"（{v['var']}）" if v["var"] else "")
            m = bykey.setdefault(vk, {"title": v["title"], "kind": "歌ってみた"})
            if v["svc"] == "yt":
                m.setdefault("id", v["id"]); m["yt_date"] = m.get("yt_date") or v["date"]
            else:
                m.setdefault("nico", v["sm"]); m.setdefault("nico_thumb", v["thumb"]); m["nico_date"] = m.get("nico_date") or v["date"]
            if vk not in keys:
                keys.append(vk)
        for vk, m in bykey.items():
            if not m.get("id"):
                m["kind"] = "ニコニコのみ"
            # 既存の mv（ボッカデラベリタ など）と同じ曲なら統合
            old = mv.get(s["name"]) if vk == s["name"] else None
            if old and old.get("kind") == "歌ってみた":
                old.update({k2: v2 for k2, v2 in m.items() if k2 not in ("title", "kind")})
            else:
                mv["cover:" + vk] = m
        vkeys = [(s["name"] if (s["name"] in mv and vk == s["name"]) else "cover:" + vk) for vk in keys]
        first = min(v["date"] for v in s["v"])
        nd = min((v["date"] for v in s["v"] if v["svc"] == "nico"), default=None)
        yd = min((v["date"] for v in s["v"] if v["svc"] == "yt"), default=None)
        def jd(d): y, mo, da = d.split("-"); return f"{y}年{int(mo)}月{int(da)}日"
        if nd and yd:
            note = f"ニコニコ動画 {jd(nd)}・YouTube {jd(yd)} に投稿。" if nd != yd else "ニコニコ動画と YouTube に投稿。"
        elif nd:
            note = "ニコニコ動画だけに投稿（YouTube にはありません）。"
        else:
            note = "YouTube に投稿。"
        if first in first_post and key(s["name"]) in key(first_post[first]["title"]):
            first_post[first]["videos"] = vkeys
            continue
        T.append({"date": first, "cat": "cover", "title": f"「{s['name']}」を歌ってみた", "note": note, "big": False, "videos": vkeys})
        n_new += 1
    T.sort(key=lambda e: e["date"])
    json.dump(mv, open(D("mv.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(T, open(D("timeline.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"songs {len(songs)}, cover entries {n_new}, timeline {len(T)}, mv {len(mv)}")

if __name__ == "__main__":
    main()
