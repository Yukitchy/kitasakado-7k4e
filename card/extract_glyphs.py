#!/usr/bin/env python3
"""ChatGPTが描いたロゴ画像から、白い字形だけをアンチエイリアス付きで抜き出す。
出力: assets/line-sakado.png / line-base.png / saka.png（いずれも透過・任意色）"""
import numpy as np, pathlib
from PIL import Image

SRC  = pathlib.Path.home()/"Downloads/sakado-mainlogo-3000.png"
OUT  = pathlib.Path(__file__).parent/"assets"; OUT.mkdir(exist_ok=True)

im = np.asarray(Image.open(SRC).convert("RGB")).astype(np.float32)
H, W, _ = im.shape
r, g, b = im[:,:,0], im[:,:,1], im[:,:,2]

# 赤い吹き出しの範囲
red = (r > 140) & (g < 115) & (b < 115)
ys, xs = np.where(red)
y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()

# 赤→白のグラデーションを alpha に変換（縁がギザつかない）
lum = 0.299*r + 0.587*g + 0.114*b
alpha = np.clip((lum - 118) / (248 - 118), 0, 1)
inside = np.zeros((H, W), bool); inside[y0:y1+1, x0:x1+1] = True
alpha = np.where(inside, alpha, 0)

# 行の帯を検出
prof  = (alpha > 0.5).sum(axis=1)
thr   = max(20, W // 120)
bands, cur = [], None
for y, n in enumerate(prof):
    if n > thr:
        cur = [y, y] if cur is None else [cur[0], y]
    elif cur:
        if cur[1] - cur[0] > H // 40: bands.append(cur)
        cur = None
if cur and cur[1] - cur[0] > H // 40: bands.append(cur)

def save(name, ya, yb, xa=None, xb=None, color=(255,255,255)):
    a = alpha[ya:yb+1]
    cols = np.where((a > 0.5).any(axis=0))[0]
    xa = cols.min() if xa is None else xa
    xb = cols.max() if xb is None else xb
    a = a[:, xa:xb+1]
    rgba = np.zeros((*a.shape, 4), np.uint8)
    rgba[:,:,0], rgba[:,:,1], rgba[:,:,2] = color
    rgba[:,:,3] = (a * 255).astype(np.uint8)
    Image.fromarray(rgba, "RGBA").save(OUT/f"{name}.png")
    return f"{name}.png {a.shape[1]}x{a.shape[0]}"

print("帯:", bands)
# bands = [吹き出し上端, 坂戸, ベース, 吹き出し下部] を想定し、中2つが本命
b_sakado, b_base = bands[1], bands[2]
log = [save("line-sakado", *b_sakado), save("line-base", *b_base)]

# 「坂」1文字＝坂戸の帯を列の切れ目で割る
a = alpha[b_sakado[0]:b_sakado[1]+1]
cols = (a > 0.5).sum(axis=0)
on = np.where(cols > 0)[0]
lo, hi = on.min(), on.max()
gap = next((x for x in range(lo + (hi-lo)//3, lo + 2*(hi-lo)//3) if cols[x] == 0), None)
log.append(save("saka", *b_sakado, xa=lo, xb=(gap-1 if gap else (lo+hi)//2)))
print(" / ".join(log))

# --- 仕上げ: 小さな抽出ノイズを落とす（本体より十分小さい塊だけ消す）---
def denoise(name, keep_ratio=0.04):
    from scipy import ndimage
    f = OUT/f"{name}.png"
    im = np.array(Image.open(f))
    lab, n = ndimage.label(im[:,:,3] > 90)
    if n <= 1: return f"{name}: 単一領域"
    sizes = ndimage.sum(np.ones_like(lab), lab, range(1, n+1))
    keep = sizes >= sizes.max() * keep_ratio
    mask = keep[lab - 1] & (lab > 0)
    im[:,:,3] = np.where(mask, im[:,:,3], 0)
    Image.fromarray(im, "RGBA").save(f)
    return f"{name}: {n}塊 → {int(keep.sum())}塊"

for nm in ["saka", "line-sakado", "line-base"]:
    print(denoise(nm))
