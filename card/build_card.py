#!/usr/bin/env python3
"""坂戸ベース 吹き出し型カード（表裏）を SVG で生成する。
画像生成と違い、幅・正方形・高さ揃えは全部座標で保証される。"""
import qrcode, pathlib

QR_URL = "https://open.spotify.com/show/4KlYeHzLWmrgUl5CO7osx3"

# ---- 版面（すべて実寸の相対値・単位はSVGユーザー単位）----
TAIL_H_   = 175
W, H      = 1000, 1000 - TAIL_H_   # 胴体＋しっぽ＝1000角の正方形に収める
R         = 92             # 角丸
TAIL_W    = 150            # しっぽの幅
TAIL_H    = TAIL_H_        # しっぽの高さ
PAD       = 80             # 版面の余白
GAP       = 60             # 左ブロックとQRの間
S         = (W - PAD*2 - GAP) // 2      # 左右それぞれの正方形の一辺 = 390
TOP       = 70                          # 上ユニットの上端
RED       = "#d8432c"
INK       = "#d8432c"

def qr_svg(url, size, x, y):
    q = qrcode.QRCode(border=0, error_correction=qrcode.constants.ERROR_CORRECT_M)
    q.add_data(url); q.make(fit=True)
    m = q.get_matrix()
    n = len(m)
    c = size / n                      # 1モジュールの辺長
    rects = "".join(
        f'<rect x="{x+j*c:.3f}" y="{y+i*c:.3f}" width="{c:.3f}" height="{c:.3f}"/>'
        for i, row in enumerate(m) for j, v in enumerate(row) if v
    )
    return f'<g fill="#1b1b1b" shape-rendering="crispEdges">{rects}</g>', n

def bubble_path(mirror=False):
    """胴体＋しっぽ。mirror=True で左右反転（裏面＝物理的に反転するため）"""
    if not mirror:
        tx = PAD + 60                 # しっぽの左端
    else:
        tx = W - PAD - 60 - TAIL_W
    return (
        f"M {R} 0 H {W-R} A {R} {R} 0 0 1 {W} {R} V {H-R} "
        f"A {R} {R} 0 0 1 {W-R} {H} "
        f"H {tx+TAIL_W} L {tx+TAIL_W*0.34:.1f} {H+TAIL_H} L {tx} {H} "
        f"H {R} A {R} {R} 0 0 1 0 {H-R} V {R} A {R} {R} 0 0 1 {R} 0 Z"
    )

FONT = "'Hiragino Sans','Hiragino Kaku Gothic ProN','Noto Sans JP',sans-serif"

def card_front(red=RED):
    return f'''<svg class="card" viewBox="-20 -20 {W+40} {H+TAIL_H+40}" xmlns="http://www.w3.org/2000/svg">
  <path d="{bubble_path()}" fill="{red}" stroke="#fff" stroke-width="26" stroke-linejoin="round"/>
  <text x="{W/2}" y="{H/2}" text-anchor="middle" dominant-baseline="central"
        font-family="{FONT}" font-weight="900" font-size="560" fill="#fff">坂</text>
</svg>'''

def card_back():
    qx, qy = PAD + S + GAP, TOP           # QRは右の正方形
    qr, n = qr_svg(QR_URL, S, qx, qy)
    lx = PAD                              # 左ブロックの左端
    # 3行の縦配分: 坂戸(150) / ベース(150) / PODCAST SINCE 2026(52) を S=390 に収める
    h1, h2, h3 = 150, 150, 52
    gap = (S - (h1 + h2 + h3)) / 2        # = 19
    y1 = TOP + h1
    y2 = y1 + gap + h2
    y3 = y2 + gap + h3
    # 下三分の一: 検索窓＋配信表記
    sy   = TOP + S + 100                   # 検索窓の上端
    sh   = 96                             # 検索窓の高さ
    btnw = 150
    return f'''<svg class="card" viewBox="-20 -20 {W+40} {H+TAIL_H+40}" xmlns="http://www.w3.org/2000/svg">
  <path d="{bubble_path(mirror=True)}" fill="#fff" stroke="#fff" stroke-width="26" stroke-linejoin="round"/>

  <!-- 左: 3行すべて textLength で横幅を S に強制（これが「揃えて」の答え） -->
  <g font-family="{FONT}" font-weight="900" fill="{INK}">
    <text x="{lx}" y="{y1}" font-size="{h1}" textLength="{S}" lengthAdjust="spacingAndGlyphs">坂戸</text>
    <text x="{lx}" y="{y2}" font-size="{h2}" textLength="{S}" lengthAdjust="spacingAndGlyphs">ベース</text>
    <text x="{lx}" y="{y3}" font-size="{h3}" textLength="{S}" lengthAdjust="spacingAndGlyphs">PODCAST SINCE 2026</text>
  </g>

  <!-- 右: QR（左ブロックと同じ一辺{S}・上端も下端も一致） -->
  {qr}

  <!-- 下三分の一: 検索窓 -->
  <g>
    <rect x="{PAD}" y="{sy}" width="{W-PAD*2}" height="{sh}" rx="{sh/2}"
          fill="none" stroke="{INK}" stroke-width="7"/>
    <text x="{PAD+46}" y="{sy+sh/2}" dominant-baseline="central"
          font-family="{FONT}" font-weight="900" font-size="52" fill="{INK}">坂戸ベース</text>
    <path d="M {W-PAD-btnw} {sy} h {btnw-sh/2} a {sh/2} {sh/2} 0 0 1 0 {sh} h -{btnw-sh/2} Z" fill="{INK}"/>
    <g transform="translate({W-PAD-btnw/2-6},{sy+sh/2}) scale(1.5)" stroke="#fff" stroke-width="3.4" fill="none">
      <circle cx="-3" cy="-3" r="10"/><path d="M 4.5 4.5 L 13 13" stroke-linecap="round"/>
    </g>
  </g>
  <text x="{PAD}" y="{sy+sh+58}" font-family="{FONT}" font-weight="900" font-size="30"
        fill="{INK}" textLength="{W-PAD*2}" lengthAdjust="spacing"
        >Spotify / Apple Podcasts / YouTube Music で配信中！</text>
</svg>'''

TOJO = [
  ("東上線ブルー",   "#0067c0"), ("TJライナー紺", "#123a6d"),
  ("急行オレンジ",   "#e8620d"), ("東武セージ",   "#2f6f5e"),
  ("川越シルバー",   "#5a6672"), ("池袋ネイビー", "#1b2f5c"),
  ("小江戸えんじ",   "#8c2d3b"), ("坂戸スカイ",   "#1e88c7"),
  ("30000系グレー",  "#7b8794"), ("東上線ブルー×朱", "#0a4f9e"),
]

def swatches():
    cells = []
    for name, col in TOJO:
        cells.append(
          f'<figure><svg viewBox="-20 -20 {W+40} {H+TAIL_H+40}">'
          f'<path d="{bubble_path()}" fill="{col}" stroke="#fff" stroke-width="26" stroke-linejoin="round"/>'
          f'<text x="{W/2}" y="{H/2}" text-anchor="middle" dominant-baseline="central" '
          f'font-family="{FONT}" font-weight="900" font-size="560" fill="#fff">坂</text>'
          f'</svg><figcaption>{name}<br><code>{col}</code></figcaption></figure>')
    return "".join(cells)

html = f'''<meta charset="utf-8"><title>坂戸ベース カード</title>
<style>
  :root{{--paper:#efece5;--ink:#2b2b2b}}
  *{{box-sizing:border-box}}
  body{{margin:0;background:var(--paper);color:var(--ink);
       font-family:{FONT};padding:40px 24px 80px}}
  h1{{font-size:19px;font-weight:900;margin:0 0 4px}}
  p.sub{{margin:0 0 28px;font-size:13px;color:#7a736a}}
  .row{{display:flex;flex-wrap:wrap;gap:36px;align-items:flex-start}}
  .item{{flex:1 1 420px;max-width:520px}}
  .lab{{font-size:12px;font-weight:900;color:#7a736a;margin-bottom:8px}}
  .card{{width:100%;height:auto;display:block;filter:drop-shadow(0 10px 22px rgba(0,0,0,.14))}}
  label{{display:inline-flex;gap:7px;align-items:center;font-size:13px;font-weight:700;
         margin-bottom:22px;cursor:pointer}}
  .sw{{display:grid;grid-template-columns:repeat(auto-fill,minmax(126px,1fr));gap:20px;max-width:1080px}}
  .sw figure{{margin:0}}
  .sw svg{{width:100%;height:auto;display:block;filter:drop-shadow(0 5px 12px rgba(0,0,0,.13))}}
  .sw figcaption{{font-size:11px;font-weight:700;margin-top:7px;line-height:1.45;color:#5f584f}}
  .sw code{{font-size:10px;color:#8d857a}}
  .guide{{display:none}}
  body.g .guide{{display:block}}
</style>
<h1>坂戸ベース 吹き出しカード</h1>
<p class="sub">表と裏は同じ型・同じ寸法。左ブロックとQRは一辺{S}の正方形で上下端が一致。3行は横幅{S}に固定。</p>
<label><input type="checkbox" onchange="document.body.classList.toggle('g',this.checked)">揃えの目安線を出す</label>
<div class="row">
  <div class="item"><div class="lab">表</div>{card_front()}</div>
  <div class="item"><div class="lab">裏</div>{card_back()}</div>
</div>
<h1 style="margin-top:56px">東武東上線から採った吹き出し色 10案</h1>
<p class="sub">前に2回頼んで出てこなかったぶんです。番号でなく色名で呼んでください。</p>
<div class="sw">{swatches()}</div>
<script>
document.querySelectorAll('svg.card').forEach(function(s){{
  var ns='http://www.w3.org/2000/svg', g=document.createElementNS(ns,'g');
  g.setAttribute('class','guide');
  [[{PAD},{TOP},{S},{S}],[{PAD+S+GAP},{TOP},{S},{S}]].forEach(function(r){{
    var x=document.createElementNS(ns,'rect');
    x.setAttribute('x',r[0]);x.setAttribute('y',r[1]);
    x.setAttribute('width',r[2]);x.setAttribute('height',r[3]);
    x.setAttribute('fill','none');x.setAttribute('stroke','#1e88e5');
    x.setAttribute('stroke-width','3');x.setAttribute('stroke-dasharray','12 8');
    g.appendChild(x);
  }});
  s.appendChild(g);
}});
</script>'''

out = pathlib.Path(__file__).with_name("index.html")
out.write_text(html, encoding="utf-8")
print("wrote", out, "| 正方形の一辺 S =", S)
