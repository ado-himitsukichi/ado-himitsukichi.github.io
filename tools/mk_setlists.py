# -*- coding: utf-8 -*-
import json, re, sys
SONGS = ["唱", "うっせぇわ", "私は最強", "逆光", "クラクラ", "MIRROR", "Blue Flame", "And July", "Episode X", "DND",
         "踊", "モンストロ", "新時代", "綺羅", "おどるポンポコリン", "Enter Sandman", "0", "Tot Musica", "アイ・アイ・ア", "Stay Gold",
         "Asteroid", "DIGNITY", "Chandelier", "ロックスター", "ギラギラ", "レディメイド", "エンゼルシーク", "ラッキー・ブルート", "ルル", "春に舞う",
         "エルフ", "風のゆくえ", "ショコラカタブラ", "Love me forever!", "アタシは問題作", "FREEDOM", "立ち入り禁止", "心という名の不可解", "ビバリウム", "永遠のあくる日",
         "MAGIC", "Value", "真夜中のドア〜stay with me", "愛して愛して愛して", "十戒 (1984)", "リベリオン", "夜のピエロ", "抜け空", "行方知れず", "風と私の物語",
         "彗星列車のベルが鳴る", "アンノウン・マザーグース", "いばら", "きっとコースター", "わたしに花束", "阿修羅ちゃん", "シャルル", "ウタカタララバイ", "ヒバナ", "Villain",
         "ザネリ", "マザーランド", "初夏", "過学習", "会いたくて", "フェイキング・オブ・コメディ", "ハングリーニコル", "オールナイトレディオ", "Hello Signals", "あのバンド",
         "向日葵", "unravel", "ドメスティックでバイオレンス", "桜日和とタイムマシン", "千本桜", "飾りじゃないのよ涙は", "ヴィラン", "ブリキノダンス", "花火", "Ready Steady",
         "恋は戦争", "金木犀", "イート", "世界のつづき", "君の体温", "シザーハンズ", "Bad Apple!!", "エージェント夜を往く", "ブラック★ロックシューター", "ラブカ？",
         "ダーリンダンス", "シカバネーゼ", "罪と罰", "バスケットワーム", "邪魔"]
assert len(SONGS) == 95
COV = {6: "LE SSERAFIM", 7: "Heize", 14: "B.B.クィーンズ", 15: "Metallica", 22: "Sia", 36: "まふまふ", 42: "松原みき", 43: "きくお",
       44: "中森明菜", 50: "After the Rain", 51: "wowaka", 56: "バルーン", 58: "DECO*27", 59: "Stella Jang", 60: "てにをは",
       66: "NILFRUITS", 69: "結束バンド", 71: "TK from 凛として時雨", 74: "黒うさP", 75: "中森明菜", 76: "てにをは", 77: "日向電工",
       79: "Giga", 80: "supercell", 81: "くじら", 82: "jon-YAKITORY", 84: "クワガタP", 85: "Nem", 86: "nomico", 87: "菊地誠",
       88: "supercell", 89: "柊キライ", 90: "かいりきベア", 91: "jon-YAKITORY", 92: "椎名林檎", 93: "GUMI", 94: "syudou"}
W = {"nomico": "nomico", "Tak_Matsumoto": "Tak Matsumoto", "Hatsune_Miku": "初音ミク", "Phantom_Siita": "ファントムシータ",
     "orchestra_/_First_speech": "オーケストラ", "mafumafu": "まふまふ"}
sp = sys.argv[1]
U = open(sp + "/sets.txt", encoding="utf-8").read()
R = open(sp + "/rows.txt", encoding="utf-8").read()
sets = {}
for part in U.replace("\n", "").split(" / "):
    m = re.match(r"#(\d+) (.*)", part.strip())
    sets[int(m.group(1))] = m.group(2)
sets[58] = sets[34]
out = []
for r in R.strip().split(";"):
    d, sid, k = r.split()
    songs = []
    for tok in sets[int(k)].split(","):
        if tok == "E":
            songs.append({"sec": "アンコール"})
            continue
        i = int(re.match(r"\d+", tok).group(0))
        notes = []
        if i in COV:
            notes.append(f"{COV[i]} のカバー")
        if "~d" in tok:
            notes.append("ライブ初披露")
        m = re.search(r"\^w(\S+)", tok)
        if m and m.group(1) in W:
            notes.append(f"with {W[m.group(1)]}")
        s = {"t": SONGS[i]}
        if notes:
            s["n"] = "・".join(notes)
        songs.append(s)
    out.append({"date": d, "sfid": sid, "url": f"https://www.setlist.fm/setlist/ado/{d[:4]}/x-{sid}.html", "songs": songs})
json.dump(out, open(sys.argv[2], "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print(len(out))
