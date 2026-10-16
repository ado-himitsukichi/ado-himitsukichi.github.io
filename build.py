#!/usr/bin/env python3
"""Ado 非公式ワクワク秘密基地: data/timeline.json から docs/ に静的サイトを生成する。

- data/timeline.json … 年表。{date: "YYYY" | "YYYY-MM" | "YYYY-MM-DD", cat, title, note, big}
  cat: niconico / feat / release / live / tieup / media / award / milestone / book
  毎月の更新では、前の月のできごとをこのファイルに足して build.py を走らせる。
- これからの予定 … ~/knowledge-os/oshi-events.js（毎週月曜に更新される推しイベント一覧）から
  artist が Ado の行だけを docs/upcoming.js に書き出す。表示は今日以降だけを JS で絞る。
- 画像 … 画像ファイルは置かない（公式素材の複製・転載をしないため）。
  MV は data/mv.json（曲名→公式チャンネルの動画 ID）から YouTube のサムネイルを i.ytimg.com から直接表示し、MV にリンクする。
  公式 X の画像は timeline.json の "x"（ポスト URL）を X の公式埋め込みで表示する。
  動画 ID は tools/find_mv.py "曲名" で探す（@Ado1024 = UCln9P4Qm3-EAY4aiEPmRwEA の動画だけを拾う）。
有志の非公式サイト。アフィリエイト・広告は入れない。歌詞の引用や公式素材は載せない。
"""
import html, json, os, re, shutil
from datetime import date

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "docs")
NAME = "Ado 非公式ワクワク秘密基地"
SITE = "https://masabee1029.github.io/ado-himitsukichi/"
GA = "G-EHWF25C1RB"
EVENTS_JS = os.path.expanduser("~/knowledge-os/oshi-events.js")
TODAY = date.today().isoformat()

CATS = {
    "niconico": ("ニコニコ・はじまり", "#22a7a0"),
    "feat": ("客演・参加", "#8b5cf6"),
    "release": ("リリース", "#2563eb"),
    "live": ("ライブ・ツアー", "#e11d48"),
    "tieup": ("タイアップ", "#ea580c"),
    "media": ("テレビ・ラジオ", "#0891b2"),
    "award": ("受賞・記録", "#ca8a04"),
    "milestone": ("できごと", "#475569"),
    "book": ("本", "#16a34a"),
}
# 時代区分（トップのカードと時代ページ）
ERAS = [
    ("hajimari", "はじまりの部屋", "ニコニコ動画の歌ってみた〜デビュー前", "0000", "2020-10-22", "君の体温"),
    ("debut", "デビューの衝撃", "「うっせぇわ」から『狂言』まで", "2020-10-23", "2022-05-31", "うっせぇわ"),
    ("shinjidai", "新時代、世界へ", "ウタの歌声とアリーナ・紅白", "2022-06-01", "2023-12-31", "新時代"),
    ("sekai", "世界をめぐる", "国立競技場と2つのワールドツアー", "2024-01-01", "2025-12-31", "ルル"),
    ("ima", "いま、そしてこれから", "自作曲「ビバリウム」と日産スタジアム", "2026-01-01", "9999", "ビバリウム"),
]
CAT_PAGES = [("release", "リリース"), ("live", "ライブ・ツアー"), ("tieup", "タイアップ・テレビ")]

esc = html.escape
MV = json.load(open(os.path.join(ROOT, "data", "mv.json"), encoding="utf-8"))
T = sorted(json.load(open(os.path.join(ROOT, "data", "timeline.json"), encoding="utf-8")),
           key=lambda e: e["date"])


def fmt(d):
    p = d.split("-")
    s = p[0] + "年"
    if len(p) > 1:
        s += str(int(p[1])) + "月"
    if len(p) > 2:
        s += str(int(p[2])) + "日"
    return s


def era_of(d):
    for e in ERAS:
        if e[3] <= d <= e[4] + "~":
            return e
    return ERAS[-1]


def thumb_url(vid, size="hqdefault"):
    return f"https://i.ytimg.com/vi/{vid}/{size}.jpg"


def watch(vid):
    return f"https://www.youtube.com/watch?v={vid}"


def thumb(song, cls="pic"):
    m = MV.get(song)
    if not m:
        return f'<div class="{cls} ph"></div>'
    return f'<img class="{cls}" src="{thumb_url(m["id"])}" alt="{esc(m["title"])} のサムネイル（YouTube）" loading="lazy">'


def songs_in(e):
    """年表の項目の「」から、MV がある曲名を拾う。"""
    out = []
    for q in re.findall(r"「([^」]+)」", e["title"] + " " + e.get("note", "")):
        for k in MV:
            if (k == q or (len(k) >= 2 and k in q)) and k not in out:
                out.append(k)
    return out


def mv_card(k):
    m = MV[k]
    return (f'<a class="mv" href="{watch(m["id"])}" target="_blank" rel="noopener">'
            f'<span class="th"><img src="{thumb_url(m["id"], "mqdefault")}" alt="" loading="lazy"><i>▶</i></span>'
            f'<span class="mt">{esc(m["title"])}<small>YouTube で見る（Ado 公式チャンネル）</small></span></a>')


def x_embed(url):
    return (f'<div class="xpost"><blockquote class="twitter-tweet" data-lang="ja" data-dnt="true">'
            f'<a href="{url}">公式 X のポストを見る</a></blockquote></div>')


def item(e, show_year=True):
    name, color = CATS.get(e["cat"], ("その他", "#64748b"))
    note = f'<p>{esc(e["note"])}</p>' if e.get("note") else ""
    note += "".join(mv_card(k) for k in songs_in(e))
    if e.get("x"):
        note += x_embed(e["x"])
    star = ' big' if e.get("big") else ''
    return (f'<li class="ev{star}"><div class="dt">{fmt(e["date"]) if show_year else fmt(e["date"])[5:] or fmt(e["date"])}</div>'
            f'<div class="bd"><span class="chip" style="--c:{color}">{name}</span>'
            f'<h3>{esc(e["title"])}</h3>{note}</div></li>')


def timeline(events, by_year=True):
    if not events:
        return '<p class="empty">まだ記録がありません。</p>'
    out, cur = [], None
    for e in events:
        y = e["date"][:4]
        if by_year and y != cur:
            if cur:
                out.append("</ol>")
            out.append(f'<h2 class="yr" id="y{y}"><a href="{{R}}year/{y}.html">{y}年</a></h2><ol class="tl">')
            cur = y
        out.append(item(e))
    out.append("</ol>")
    if not by_year:
        out.insert(0, '<ol class="tl">')
    return "\n".join(out)


YEARS = sorted({e["date"][:4] for e in T})

NAV = [("index.html", "基地トップ"), ("timeline.html", "全部の年表"), ("era/hajimari.html", "ニコニコ時代"),
       ("release.html", "リリース"), ("live.html", "ライブ"), ("tieup.html", "タイアップ"), ("mv.html", "MV"), ("x.html", "公式Xまとめ"),
       ("schedule.html", "これからの予定"), ("about.html", "この基地について")]

CSS = """
:root{--bg:#f4f6fb;--card:#fff;--ink:#1e2433;--sub:#5b6478;--line:#e3e7f0;--ac:#2f5bea;--ac2:#e0457b;--yl:#ffd84d;--hd:#14193a}
@media (prefers-color-scheme:dark){:root{--bg:#0e1222;--card:#171c31;--ink:#e8ebf5;--sub:#a3abc2;--line:#2a3150;--ac:#7c9bff;--ac2:#ff7aa5;--hd:#0a0d1c}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font-family:"Hiragino Sans","Noto Sans JP",sans-serif;line-height:1.8;font-size:16px}
a{color:var(--ac)}img{max-width:100%;display:block}
.top{background:var(--hd);color:#fff}.top .in{max-width:1180px;margin:auto;padding:12px 16px;display:flex;align-items:center;gap:12px;flex-wrap:wrap}
.logo{color:#fff;text-decoration:none;font-weight:800;font-size:20px;letter-spacing:.02em}.logo span{color:var(--yl)}
.badge{font-size:11px;border:1px solid #fff6;border-radius:99px;padding:1px 8px;color:#fffc}
.gnav{background:var(--card);border-bottom:1px solid var(--line);position:sticky;top:0;z-index:5}
.gnav ul{max-width:1180px;margin:auto;padding:0 8px;list-style:none;display:flex;overflow-x:auto;gap:2px}
.gnav a{display:block;padding:10px 12px;white-space:nowrap;text-decoration:none;color:var(--ink);font-size:14px;font-weight:600;border-bottom:3px solid transparent}
.gnav a.on,.gnav a:hover{border-color:var(--ac2);color:var(--ac2)}
.hero{max-width:1180px;margin:16px auto 0;padding:0 16px}.hero img,.hero .ph{width:100%;aspect-ratio:2.5/1;object-fit:cover;border-radius:14px}
.ph{background:linear-gradient(135deg,#2f5bea,#8b5cf6 55%,#e0457b)}
.layout{max-width:1180px;margin:20px auto;padding:0 16px;display:grid;grid-template-columns:minmax(0,1fr) 300px;gap:24px}
@media(max-width:900px){.layout{grid-template-columns:1fr}}
main>section,.box{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:20px;margin-bottom:20px}
.crumb{font-size:13px;color:var(--sub);margin-bottom:8px}.crumb a{color:var(--sub)}
h1{font-size:26px;line-height:1.4;margin:0 0 8px}h2{font-size:20px;margin:0 0 12px}
.lead{color:var(--sub);margin:0}
.sec-t{display:flex;align-items:center;gap:8px}.sec-t:before{content:"";width:6px;height:22px;background:var(--ac2);border-radius:3px}
.eras{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:14px}
.era{display:block;text-decoration:none;color:inherit;border:1px solid var(--line);border-radius:12px;overflow:hidden;background:var(--bg);transition:transform .15s}
.era:hover{transform:translateY(-3px)}.pic{border-radius:10px;}.era .pic{border-radius:0;width:100%;aspect-ratio:16/10;object-fit:cover}
.era div.t{padding:10px 12px}.era b{display:block;font-size:16px}.era small{color:var(--sub);font-size:12.5px;line-height:1.5;display:block}
.era .n{font-size:12px;color:var(--ac2);font-weight:700}
.years{display:grid;grid-template-columns:repeat(auto-fill,minmax(96px,1fr));gap:8px}
.years a{display:block;text-align:center;padding:10px 4px;border-radius:10px;background:var(--bg);border:1px solid var(--line);text-decoration:none;color:var(--ink);font-weight:700}
.years a small{display:block;font-weight:400;color:var(--sub);font-size:12px}
.years a:hover{border-color:var(--ac)}
.yr{margin:24px 0 8px;font-size:22px}.yr a{color:var(--ink);text-decoration:none}.yr:first-child{margin-top:0}
.tl{list-style:none;margin:0;padding:0;border-left:3px solid var(--line);margin-left:6px}
.ev{position:relative;padding:4px 0 14px 18px;display:grid;grid-template-columns:120px 1fr;gap:10px}
.ev:before{content:"";position:absolute;left:-8px;top:12px;width:13px;height:13px;border-radius:50%;background:var(--card);border:3px solid var(--line)}
.ev.big:before{background:var(--yl);border-color:var(--ac2)}
.ev .dt{font-size:13.5px;color:var(--sub);font-weight:700;padding-top:2px}
.ev h3{margin:2px 0 0;font-size:16.5px;line-height:1.5}.ev.big h3{color:var(--ac2)}.ev p{margin:2px 0 0;font-size:14.5px;color:var(--sub)}
@media(max-width:560px){.ev{grid-template-columns:1fr;gap:0}}
.chip{display:inline-block;font-size:11.5px;font-weight:700;color:var(--c);border:1px solid var(--c);border-radius:99px;padding:0 8px;line-height:1.7}
.up{list-style:none;margin:0;padding:0}.up li{display:flex;gap:12px;padding:10px 0;border-bottom:1px dashed var(--line)}
.up li:last-child{border:0}.up .d{flex:0 0 74px;text-align:center;background:var(--bg);border-radius:10px;padding:4px;font-weight:800;line-height:1.3}
.up .d small{display:block;font-weight:400;font-size:11px;color:var(--sub)}.up .k{font-size:11.5px;color:var(--ac2);font-weight:700}
.side .box{padding:16px}.side h2{font-size:16px}.side ul{list-style:none;margin:0;padding:0}.side li a{display:block;padding:6px 4px;border-bottom:1px solid var(--line);text-decoration:none;color:var(--ink);font-size:14.5px}
.side li a:hover{color:var(--ac2)}.side .note{font-size:13px;color:var(--sub);margin:0}
.side .sticky{position:sticky;top:56px}
.notice{font-size:13.5px;background:var(--bg);border-left:4px solid var(--yl);padding:10px 12px;border-radius:6px;color:var(--sub)}
.pager{display:flex;justify-content:space-between;gap:10px;margin-top:10px;flex-wrap:wrap}
.pager a{padding:8px 14px;border:1px solid var(--line);border-radius:99px;text-decoration:none;background:var(--card)}
.empty{color:var(--sub)}
.mv{display:flex;gap:10px;align-items:center;margin-top:8px;padding:6px;border:1px solid var(--line);border-radius:10px;text-decoration:none;color:var(--ink);background:var(--bg);max-width:460px}
.mv:hover{border-color:#ff0033}.mv .th{position:relative;flex:0 0 160px}.mv .th img{width:160px;aspect-ratio:16/9;object-fit:cover;border-radius:6px}
.mv .th i{position:absolute;inset:0;margin:auto;width:34px;height:24px;border-radius:7px;background:#ff0033;color:#fff;font-style:normal;font-size:12px;display:grid;place-items:center}
.mv .mt{font-size:14px;font-weight:700;line-height:1.5}.mv .mt small{display:block;font-weight:400;color:var(--sub);font-size:12px}
@media(max-width:560px){.mv .th{flex-basis:120px}.mv .th img{width:120px}}
.xpost{max-width:460px;margin-top:6px}.xpost .twitter-tweet{margin:6px 0!important}
.mosaic{display:grid;grid-template-columns:repeat(4,1fr);gap:6px;border-radius:14px;overflow:hidden}
.mosaic a{position:relative;display:block}.mosaic img{width:100%;aspect-ratio:16/9;object-fit:cover;display:block;transition:opacity .15s}.mosaic a:hover img{opacity:.8}
@media(max-width:700px){.mosaic{grid-template-columns:repeat(2,1fr)}}
.mvgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:14px}
.mvgrid a{text-decoration:none;color:var(--ink);font-size:14px;font-weight:700;line-height:1.5}.mvgrid img{width:100%;aspect-ratio:16/9;object-fit:cover;border-radius:10px;margin-bottom:4px}
.xgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:14px;align-items:start}
.xgrid h3{font-size:15px;margin:0}.credit{font-size:12.5px;color:var(--sub);margin:6px 0 0}
footer{background:var(--hd);color:#c8cde0;font-size:13px;text-align:center;padding:24px 16px;line-height:1.9}footer a{color:#fff}
"""


def sidebar():
    eras = "".join(f'<li><a href="{{R}}era/{e[0]}.html">{e[1]}</a></li>' for e in ERAS)
    years = "".join(f'<li><a href="{{R}}year/{y}.html">{y}年</a></li>' for y in YEARS)
    return f"""<aside class="side">
<div class="box"><h2>🔑 この基地について</h2><p class="note">Ado さんを応援する有志がつくった<b>非公式</b>の年表サイトです。ニコニコ動画のころから今までの歩みを、毎月のイベントごとに書き足していきます。公式とは関係ありません。</p></div>
<div class="box"><h2>🗺 時代でたどる</h2><ul>{eras}</ul></div>
<div class="box sticky"><h2>📅 年でたどる</h2><ul>{years}</ul>
<h2 style="margin-top:14px">📣 公式はこちら</h2><ul>
<li><a href="https://www.universal-music.co.jp/ado/" rel="noopener" target="_blank">公式サイト（ユニバーサル ミュージック）</a></li>
<li><a href="https://www.youtube.com/@Ado1024" rel="noopener" target="_blank">公式 YouTube チャンネル</a></li>
<li><a href="https://x.com/ado1024imokenp" rel="noopener" target="_blank">Ado さんの X（@ado1024imokenp）</a></li>
<li><a href="https://x.com/ado_staff" rel="noopener" target="_blank">Ado Staff の X（@ado_staff）</a></li>
<li><a href="https://cloud9pro.co.jp/artist/profile/ado/" rel="noopener" target="_blank">クラウドナイン プロフィール</a></li></ul></div>
</aside>"""


def page(path, title, desc, body, crumb=None, hero=False):
    depth = path.count("/")
    R = "../" * depth
    nav = "".join(f'<li><a href="{R}{h}"{" class=on" if h == path else ""}>{t}</a></li>' for h, t in NAV)
    cr = ""
    if crumb:
        cr = '<div class="crumb"><a href="' + R + 'index.html">基地トップ</a> › ' + " › ".join(crumb) + "</div>"
    full = NAME if path == "index.html" else f"{title}｜{NAME}"
    heroh = f'<div class="hero">{hero}</div>' if hero else ""
    og = thumb_url(MV["うっせぇわ"]["id"], "hqdefault")
    widgets = '<script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>' if "twitter-tweet" in body else ""
    doc = f"""<!doctype html><html lang="ja"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(full)}</title><meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{SITE}{path}">
<meta property="og:title" content="{esc(full)}"><meta property="og:description" content="{esc(desc)}">
<meta property="og:type" content="website"><meta property="og:url" content="{SITE}{path}">
{f'<meta property="og:image" content="{og}"><meta name="twitter:card" content="summary_large_image">' if og else ''}
<script async src="https://www.googletagmanager.com/gtag/js?id={GA}"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}gtag('js',new Date());gtag('config','{GA}');</script>
<style>{CSS}</style></head><body>
<header class="top"><div class="in"><a class="logo" href="{R}index.html">Ado 非公式<span>ワクワク</span>秘密基地</a><span class="badge">有志の非公式ファンサイト</span></div></header>
<nav class="gnav"><ul>{nav}</ul></nav>
{heroh}
<div class="layout"><main>{cr}{body}</main>{sidebar()}</div>
<footer>{NAME} は、Ado さんを応援する有志による<b>非公式</b>のファンサイトです。Ado さん本人・所属事務所・レーベルとは関係ありません。<br>
掲載情報は公開されている報道・公式発表をもとにしています。最新・正確な情報は<a href="https://www.universal-music.co.jp/ado/" target="_blank" rel="noopener">公式サイト</a>でご確認ください。<br>
画像ファイルの複製・転載はしていません。MV のサムネイルは YouTube から、公式 X の画像は X の埋め込み機能でそのまま表示しています（権利は各権利者に帰属します）。 ／ <a href="{R}about.html">この基地について・プライバシー</a><br>最終更新: {TODAY}</footer>
{widgets}</body></html>"""
    doc = doc.replace("{R}", R)
    p = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="utf-8").write(doc)
    PAGES.append(path)


def upcoming_box(limit, title="これからの予定", more=True):
    link = '<p style="margin:10px 0 0;text-align:right"><a href="{R}schedule.html">予定をもっと見る →</a></p>' if more else ""
    return f"""<section><h2 class="sec-t">{title}</h2>
<ul class="up" id="up" data-limit="{limit}"><li class="empty">読み込み中…</li></ul>{link}
<p class="notice" style="margin-top:12px">予定は公式発表・報道をもとに毎週まとめています。変更になることがあるので、参加前に必ず公式でご確認ください。</p></section>
<script src="{{R}}upcoming.js"></script><script>
(function(){{var el=document.getElementById('up'),lim=+el.dataset.limit,t=new Date(),pad=function(n){{return('0'+n).slice(-2)}},
today=t.getFullYear()+'-'+pad(t.getMonth()+1)+'-'+pad(t.getDate()),K={{live:'ライブ',release:'リリース',tieup:'タイアップ',event:'イベント',anniv:'記念日',media:'テレビ・ラジオ・配信',ticket:'チケット'}},
W='日月火水木金土',it=(window.ADO_UPCOMING||[]).filter(function(e){{return e.date>=today}}).slice(0,lim);
if(!it.length){{el.innerHTML='<li class="empty">いま分かっている予定はありません。</li>';return}}
el.innerHTML=it.map(function(e){{var d=new Date(e.date+'T00:00:00');return '<li><div class="d">'+(d.getMonth()+1)+'/'+d.getDate()+'<small>'+d.getFullYear()+'（'+W[d.getDay()]+'）</small></div><div><span class="k">'+(K[e.kind]||'')+'</span><div>'+e.title.replace(/[<>&]/g,'')+'</div></div></li>'}}).join('')}})();
</script>"""


def write_upcoming():
    items = []
    if os.path.exists(EVENTS_JS):
        s = open(EVENTS_JS, encoding="utf-8").read()
        for m in re.finditer(r'\{\s*date:\s*"([\d-]+)",\s*artist:\s*"Ado",\s*title:\s*"((?:[^"\\]|\\.)*)",\s*kind:\s*"(\w+)"', s):
            d, t, k = m.group(1), json.loads('"' + m.group(2) + '"'), m.group(3)
            if k == "anniv":
                continue
            items.append({"date": d, "title": t, "kind": k})
    items.sort(key=lambda e: e["date"])
    open(os.path.join(OUT, "upcoming.js"), "w", encoding="utf-8").write(
        "window.ADO_UPCOMING=" + json.dumps(items, ensure_ascii=False) + ";\n")
    return len(items)


def build():
    if os.path.exists(OUT):
        for n in os.listdir(OUT):
            p = os.path.join(OUT, n)
            if n == "CNAME":
                continue
            shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
    os.makedirs(OUT, exist_ok=True)
    open(os.path.join(OUT, ".nojekyll"), "w").close()
    n_up = write_upcoming()

    # トップ
    era_cards = []
    for e in ERAS:
        n = sum(1 for x in T if era_of(x["date"]) == e)
        era_cards.append(f'<a class="era" href="{{R}}era/{e[0]}.html">{thumb(e[5])}'
                         f'<div class="t"><span class="n">{n} のできごと</span><b>{e[1]}</b><small>{e[2]}</small></div></a>')
    year_cards = "".join(f'<a href="{{R}}year/{y}.html">{y}<small>{sum(1 for x in T if x["date"][:4] == y)} 件</small></a>' for y in YEARS)
    recent = [e for e in T if e["date"] <= TODAY][-6:][::-1]
    body = f"""<section><h1>ようこそ、ワクワク秘密基地へ！</h1>
<p class="lead">2017年、ニコニコ動画に投稿された1本の「歌ってみた」から、国立競技場・日産スタジアム・世界のステージまで。歌い手 Ado さんの歩みを、ファンの手で年表にまとめた非公式の秘密基地です。これからも毎月、新しいできごとを書き足していきます。</p></section>
{upcoming_box(5)}
<section><h2 class="sec-t">時代でたどる Ado の歩み</h2><div class="eras">{"".join(era_cards)}</div></section>
<section><h2 class="sec-t">最近のできごと</h2>{timeline(recent, by_year=False)}
<p style="margin:6px 0 0;text-align:right"><a href="{{R}}timeline.html">全部の年表を見る →</a></p></section>
<section><h2 class="sec-t">年でたどる</h2><div class="years">{year_cards}</div></section>"""
    top = ["うっせぇわ", "新時代", "唱", "踊", "ギラギラ", "ルル", "エルフ", "ビバリウム"]
    mosaic = '<div class="mosaic">' + "".join(
        f'<a href="{watch(MV[k]["id"])}" target="_blank" rel="noopener" title="{esc(MV[k]["title"])}"><img src="{thumb_url(MV[k]["id"])}" alt="{esc(MV[k]["title"])}"></a>'
        for k in top if k in MV) + "</div>"
    page("index.html", NAME, "歌い手 Ado さんの歩みを、ニコニコ動画の歌ってみた時代から今まで年表にまとめた有志の非公式ファンサイト。毎月のイベントごとに更新。", body, hero=mosaic)

    # 全年表
    jump = " ".join(f'<a href="#y{y}">{y}</a>' for y in YEARS)
    page("timeline.html", "全部の年表", "Ado さんの活動を最初の歌ってみたから最新ニュースまで、すべて時系列で。",
         f'<section><h1>全部の年表</h1><p class="lead">黄色い印は特に大きなできごとです。 年へジャンプ: {jump}</p></section><section>{timeline(T)}</section>',
         crumb=["全部の年表"])

    # 時代ページ
    for i, e in enumerate(ERAS):
        ev = [x for x in T if era_of(x["date"]) == e]
        pv = f'<a href="{e[0] and ERAS[i-1][0]}.html">← {ERAS[i-1][1]}</a>' if i else "<span></span>"
        nx = f'<a href="{ERAS[i+1][0]}.html">{ERAS[i+1][1]} →</a>' if i + 1 < len(ERAS) else "<span></span>"
        page(f"era/{e[0]}.html", e[1], f"Ado さんの「{e[1]}」— {e[2]}の時代を年表でたどります。",
             f'<section><a href="{watch(MV[e[5]]["id"])}" target="_blank" rel="noopener">{thumb(e[5])}</a><p class="credit">画像: 「{esc(MV[e[5]]["title"])}」MV のサムネイル（YouTube・Ado 公式チャンネル）</p><h1 style="margin-top:14px">{e[1]}</h1><p class="lead">{e[2]}</p></section>'
             f'<section>{timeline(ev)}<div class="pager">{pv}{nx}</div></section>', crumb=[e[1]])

    # 年ページ
    for i, y in enumerate(YEARS):
        ev = [x for x in T if x["date"][:4] == y]
        pv = f'<a href="{YEARS[i-1]}.html">← {YEARS[i-1]}年</a>' if i else "<span></span>"
        nx = f'<a href="{YEARS[i+1]}.html">{YEARS[i+1]}年 →</a>' if i + 1 < len(YEARS) else "<span></span>"
        page(f"year/{y}.html", f"{y}年の Ado", f"{y}年の Ado さんのできごと（{len(ev)}件）を年表で。",
             f'<section><h1>{y}年の Ado</h1><p class="lead">{len(ev)} 件のできごと</p></section>'
             f'<section>{timeline(ev, by_year=False)}<div class="pager">{pv}{nx}</div></section>', crumb=[f"{y}年"])

    # カテゴリページ
    groups = {"release": {"release", "feat", "book"}, "live": {"live"}, "tieup": {"tieup", "media", "award"}}
    leads = {"release": "配信シングル・アルバム・客演・本のできごと。", "live": "ワンマンライブ・ツアー・フェス出演の記録。",
             "tieup": "映画・アニメ・ドラマのタイアップ、テレビ・ラジオ出演、受賞と記録。"}
    for k, t in CAT_PAGES:
        ev = [x for x in T if x["cat"] in groups[k]]
        page(f"{k}.html", t, f"Ado さんの{t}の年表。{leads[k]}",
             f'<section><h1>{t}</h1><p class="lead">{leads[k]}</p></section><section>{timeline(ev)}</section>', crumb=[t])

    # MV ギャラリー
    sec = []
    for kind, lead in [("オリジナル", "オリジナル曲の MV"), ("ウタ", "映画『ONE PIECE FILM RED』ウタの歌唱曲"), ("歌ってみた", "歌ってみた・カバー")]:
        cards = "".join(f'<a href="{watch(m["id"])}" target="_blank" rel="noopener"><img src="{thumb_url(m["id"])}" alt="" loading="lazy">{esc(m["title"])}</a>'
                        for m in MV.values() if m["kind"] == kind)
        sec.append(f'<section><h2 class="sec-t">{lead}</h2><div class="mvgrid">{cards}</div></section>')
    page("mv.html", "MV ギャラリー", "Ado さんの MV を、YouTube 公式チャンネルへのリンクでまとめました。",
         '<section><h1>MV ギャラリー</h1><p class="lead">サムネイルを押すと YouTube の Ado 公式チャンネルで MV が開きます。</p></section>' + "".join(sec),
         crumb=["MV ギャラリー"])

    # 公式 X まとめ
    xs = [e for e in T if e.get("x")][::-1]
    cards = "".join(f'<div><h3>{fmt(e["date"])}｜{esc(e["title"])}</h3>{x_embed(e["x"])}</div>' for e in xs)
    page("x.html", "公式Xまとめ", "Ado さん・Ado Staff の公式 X から、節目のポストを埋め込みでまとめました。",
         '<section><h1>公式Xまとめ</h1><p class="lead">デビュー・ライブ・ツアーなど節目のポストを、X の埋め込みで並べています。最新の情報は '
         '<a href="https://x.com/ado1024imokenp" target="_blank" rel="noopener">@ado1024imokenp</a> と '
         '<a href="https://x.com/ado_staff" target="_blank" rel="noopener">@ado_staff</a> をご覧ください。</p></section>'
         f'<section><div class="xgrid">{cards}</div></section>', crumb=["公式Xまとめ"])

    # 予定
    page("schedule.html", "これからの予定", "Ado さんのこれからのライブ・リリース・テレビ出演などの予定。毎週更新。",
         '<section><h1>これからの予定</h1><p class="lead">ライブ・リリース・放送・チケットの予定をまとめています。</p></section>'
         + upcoming_box(60, "予定一覧", more=False), crumb=["これからの予定"])

    # この基地について
    page("about.html", "この基地について", "Ado 非公式ワクワク秘密基地について、運営方針とプライバシーポリシー。", """<section><h1>この基地について</h1>
<p>「Ado 非公式ワクワク秘密基地」は、歌い手 Ado さんを応援する有志がつくった<b>非公式</b>のファンサイトです。Ado さん本人、所属事務所（クラウドナイン）、レーベル（ユニバーサル ミュージック）とは一切関係ありません。</p>
<h2>このサイトでやっていること</h2><ul>
<li>ニコニコ動画の歌ってみた時代から今までのできごとを、年表にまとめています</li>
<li>毎月、前の月のできごとを書き足します。これからの予定は毎週更新します</li>
<li>情報は公式発表・報道・Wikipedia などの公開情報をもとにしています。まちがいに気づいたときは直します</li></ul>
<h2>やらないこと</h2><ul>
<li>広告・アフィリエイトは載せません</li>
<li>歌詞の引用、公式の写真・イラスト・ロゴの複製・転載はしません。画像は、YouTube 公式チャンネルの MV サムネイル（YouTube から直接表示し、MV にリンク）と、Ado さん・Ado Staff の公式 X ポストの埋め込みだけです。権利は各権利者に帰属します。削除のご依頼があればすぐに対応します</li>
<li>うわさ話や私生活に関することは書きません</li></ul>
<h2>プライバシーポリシー</h2>
<p>MV のサムネイルは YouTube（Google）、公式ポストは X の埋め込みを使っているため、それぞれのサービスが Cookie などで情報を取得する場合があります。アクセスの傾向を知るために Google アナリティクスを使っています。Cookie を使って匿名のアクセス情報を集めますが、個人を特定する情報は集めません。ブラウザの設定で Cookie を無効にできます。</p>
<h2>参考にしている情報源</h2><ul>
<li><a href="https://www.universal-music.co.jp/ado/" target="_blank" rel="noopener">Ado - UNIVERSAL MUSIC JAPAN</a></li>
<li><a href="https://cloud9pro.co.jp/artist/profile/ado/" target="_blank" rel="noopener">株式会社クラウドナイン アーティストプロフィール</a></li>
<li><a href="https://ja.wikipedia.org/wiki/Ado" target="_blank" rel="noopener">Ado - Wikipedia</a></li>
<li>音楽ナタリー、THE FIRST TIMES などの音楽ニュース</li></ul></section>""", crumb=["この基地について"])

    # sitemap / robots
    sm = "".join(f"<url><loc>{SITE}{'' if p == 'index.html' else p}</loc><lastmod>{TODAY}</lastmod></url>" for p in PAGES)
    open(os.path.join(OUT, "sitemap.xml"), "w").write(
        f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>')
    open(os.path.join(OUT, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\nSitemap: {SITE}sitemap.xml\n")
    print(f"built {len(PAGES)} pages, {len(T)} timeline events, {n_up} upcoming")


PAGES = []
if __name__ == "__main__":
    build()
