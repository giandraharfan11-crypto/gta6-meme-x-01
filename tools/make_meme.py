#!/usr/bin/env python3
"""Build meme.png for the make.fun gta6-meme-x-01 entry.

Pipeline (all local, Pillow only):
  1. Extract the make.fun ghost mascot from the OFFICIAL press mark
     (tools/assets/mark-1024.png, downloaded from https://make.fun/press/).
     The mark is a magenta disc with a black ring; the mascot (white ghost
     with sparkle eyes + magenta star coin + white coin) lives inside it.
     We drop the disc/ring and keep the mascot itself.
  2. Dress the ghost: sunglasses + a Hawaiian shirt band clipped to its
     silhouette, so it reads as a character in the scene, not a sticker.
  3. Composite it large onto the empty beach chair of the AI-generated
     base scene (tools/assets/base.png: cobweb skeleton waiting in a dead
     pre-order line on the left, Leonida beach on the right).
  4. Letter the blank wooden sign in the base scene ("GTA VI / PRE-ORDER
     LINE / EST. 2013"), add a make.fun name pill in-scene, and draw the
     two meme captions in heavy outlined bold type sized to survive the
     judge's 480x480 shrink.

Run:  python3 tools/make_meme.py
Out:  meme.png at the repository root (1200x1200 PNG).
"""
from pathlib import Path
import math
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
ASSETS = Path(__file__).resolve().parent / "assets"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

W = 1200
TOP_BAR = 168
CROP_TOP, CROP_BOT = 225, 1365  # base-image rows holding the actual scene
SCENE_H = 855  # (CROP_BOT - CROP_TOP) * 0.75
BOT_BAR = W - TOP_BAR - SCENE_H  # 177

INK = (25, 20, 25)
MAGENTA = (196, 28, 131)
GOLD = (255, 217, 77)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_BOLD, size)


def is_magenta(px) -> bool:
    r, g, b = px[0], px[1], px[2]
    return r > 150 and g < 90 and 70 < b < 180


def extract_ghost() -> Image.Image:
    """Cut the mascot out of the official circular mark.

    Segmentation by colour + proximity, which is robust where pure
    geometry is not (the star coin nearly touches the badge ring):
      core  = white pixels (ghost body, star, small coin) plus magenta
              pixels inside the two coin circles (from mark.svg geometry);
      keep  = core pixels, plus dark outline pixels within 15 px of the
              core (the mascot's black stroke). The magenta disc and the
              badge ring are neither core nor near it, so they vanish.
    """
    import numpy as np
    from scipy import ndimage

    mark = Image.open(ASSETS / "mark-1024.png").convert("RGBA")
    arr = np.array(mark)
    r = arr[:, :, 0].astype(int)
    g = arr[:, :, 1].astype(int)
    b = arr[:, :, 2].astype(int)
    a = arr[:, :, 3]
    yy, xx = np.mgrid[0:mark.height, 0:mark.width]
    white = (r > 200) & (g > 200) & (b > 200) & (a > 0)
    magenta = (r > 150) & (g < 90) & (b > 70) & (b < 180) & (a > 0)
    in_coin = np.zeros_like(white)
    # Only the star coin has a magenta fill, and its fill radius is ~122,
    # well inside its ~135 black outline: a 150 radius would also capture
    # a crescent of the surrounding disc. The small coin's fill is white,
    # so it is already core and needs no circle.
    for ccx, ccy, cr in [(793, 441, 122)]:
        in_coin |= (xx - ccx) ** 2 + (yy - ccy) ** 2 < cr * cr
    core = white | (magenta & in_coin)
    dist_to_core = ndimage.distance_transform_edt(~core)
    dark = (r < 90) & (g < 90) & (b < 90) & (a > 0)
    keep = core | (dark & (dist_to_core <= 15))
    # In this raster the star coin's outline merges into the badge ring
    # on its right side, so proximity alone keeps a chunk of ring there.
    # Nothing legit lives at x > 880 except the star coin disc itself
    # (centre 793,441, outer radius ~140): keep only that disc there.
    star_disc = (xx - 793) ** 2 + (yy - 441) ** 2 <= 148 ** 2
    keep &= ~((xx > 880) & ~star_disc)
    arr[~keep] = (0, 0, 0, 0)
    # Final sweep: the kept mask is exactly three components (ghost body,
    # star coin, small coin, each >10k px). Anything smaller is a ring
    # fragment that survived above; drop it.
    labels, n = ndimage.label(arr[:, :, 3] > 0)
    sizes = ndimage.sum(arr[:, :, 3] > 0, labels, range(1, n + 1))
    big = np.isin(labels, [i + 1 for i, s in enumerate(sizes) if s >= 10000])
    arr[~big] = (0, 0, 0, 0)
    ghost = Image.fromarray(arr, "RGBA").crop(Image.fromarray(arr, "RGBA").getbbox())
    ghost.save(ASSETS / "ghost-cutout.png")
    return ghost


def dress_ghost(ghost: Image.Image) -> Image.Image:
    """Sunglasses + Hawaiian shirt, drawn on the native-size cutout."""
    g = ghost.copy()
    d = ImageDraw.Draw(g, "RGBA")
    w, h = g.size
    # --- Hawaiian shirt: band across the lower body, clipped to silhouette
    shirt = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shirt)
    y0 = int(h * 0.66)
    sd.rectangle([0, y0, w, h], fill=(255, 110, 72, 255))
    rng = random.Random(42)
    for _ in range(46):  # simple flowers: white petals + gold centre
        fx, fy = rng.randint(10, w - 10), rng.randint(y0 + 12, h - 10)
        if g.getpixel((min(fx, w - 1), min(fy, h - 1)))[3] == 0:
            continue
        for ang in range(0, 360, 72):
            px_ = fx + int(9 * math.cos(math.radians(ang)))
            py_ = fy + int(9 * math.sin(math.radians(ang)))
            sd.ellipse([px_ - 5, py_ - 5, px_ + 5, py_ + 5], fill=(255, 255, 255, 235))
        sd.ellipse([fx - 4, fy - 4, fx + 4, fy + 4], fill=(255, 217, 77, 255))
    for _ in range(26):  # teal leaves
        fx, fy = rng.randint(10, w - 10), rng.randint(y0 + 10, h - 8)
        sd.ellipse([fx - 10, fy - 4, fx + 10, fy + 4], fill=(20, 160, 150, 220))
    # clip shirt to the ghost silhouette within the band
    from PIL import ImageChops
    band_mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(band_mask).rectangle([0, y0, w, h], fill=255)
    shirt.putalpha(ImageChops.multiply(g.split()[3], band_mask))
    g.alpha_composite(shirt)
    d = ImageDraw.Draw(g, "RGBA")
    # --- Sunglasses across the sparkle eyes (eyes sit ~29-44% x, ~36% y)
    ex0, ey0, ex1, ey1 = int(w * 0.13), int(h * 0.29), int(w * 0.63), int(h * 0.46)
    d.rounded_rectangle([ex0, ey0, ex1, ey1], radius=30, fill=(15, 13, 18, 255))
    mid = (ex0 + ex1) // 2
    d.line([ex0 + 20, ey0 + 24, ex0 + 100, ey0 + 24], fill=(255, 255, 255, 210), width=10)
    d.line([mid + 55, ey0 + 24, mid + 135, ey0 + 24], fill=(255, 255, 255, 210), width=10)
    return g


def outlined_text(draw, cx, y, text, fnt, fill, stroke=8):
    draw.text((cx, y), text, font=fnt, fill=fill, anchor="ma",
              stroke_width=stroke, stroke_fill=BLACK)


def fit_font(draw, text, max_size, max_width):
    """Largest bold font (<= max_size) whose stroked text fits max_width."""
    size = max_size
    while size > 20:
        fnt = font(size)
        box = draw.textbbox((0, 0), text, font=fnt, stroke_width=max(4, size // 8))
        if box[2] - box[0] <= max_width:
            return fnt
        size -= 2
    return font(size)


def main() -> None:
    ghost = dress_ghost(extract_ghost())

    base = Image.open(ASSETS / "base.png").convert("RGB")
    scene = base.crop((0, CROP_TOP, 1600, CROP_BOT)).resize((W, SCENE_H), Image.LANCZOS)

    canvas = Image.new("RGB", (W, W), BLACK)
    canvas.paste(scene, (0, TOP_BAR))
    d = ImageDraw.Draw(canvas, "RGBA")

    def sx(bx):  # base-image x -> canvas x
        return bx * 0.75

    def sy(by):  # base-image y -> canvas y
        return TOP_BAR + (by - CROP_TOP) * 0.75

    # --- Letter the blank wooden sign (base coords ~270..700 x 325..540)
    sign_cx = sx((270 + 700) / 2)
    d.text((sign_cx, sy(338)), "GTA VI", font=font(58), fill=(46, 33, 24), anchor="ma")
    d.text((sign_cx, sy(428)), "PRE-ORDER LINE", font=font(30), fill=(46, 33, 24), anchor="ma")
    d.text((sign_cx, sy(478)), "EST. 2013", font=font(30), fill=(46, 33, 24), anchor="ma")

    # --- Ghost on the beach chair, big enough to read at 480px
    gw = 460
    gh = int(ghost.height * gw / ghost.width)
    ghost_r = ghost.resize((gw, gh), Image.LANCZOS)
    gx, gy = 590, 535
    shadow = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).ellipse([gx + 30, gy + gh - 28, gx + gw - 10, gy + gh + 14],
                                   fill=(0, 0, 0, 110))
    canvas.paste(Image.alpha_composite(canvas.convert("RGBA"),
                                       shadow.filter(ImageFilter.GaussianBlur(10))).convert("RGB"),
                 (0, 0))
    canvas.paste(ghost_r, (gx, gy), ghost_r)
    d = ImageDraw.Draw(canvas, "RGBA")

    # --- make.fun name pill, in-scene on the dead store floor
    pill_x, pill_y, pill_w, pill_h = 24, 950, 224, 54
    d.rounded_rectangle([pill_x, pill_y, pill_x + pill_w, pill_y + pill_h],
                        radius=27, fill=(255, 255, 255, 255))
    d.text((pill_x + pill_w / 2, pill_y + 6), "make.fun", font=font(34),
           fill=INK, anchor="ma")

    # --- Captions (auto-fitted so nothing ever clips at the edges)
    top = "13 YEARS WAITING FOR GTA VI"
    f_top = fit_font(d, top, 72, 1150)
    outlined_text(d, W / 2, (TOP_BAR - 86) // 2, top, f_top, WHITE, stroke=10)
    bot1 = "THE GHOST ALREADY MOVED TO LEONIDA"
    f_b1 = fit_font(d, bot1, 54, 1150)
    outlined_text(d, W / 2, TOP_BAR + SCENE_H + 14, bot1, f_b1, WHITE, stroke=8)
    bot2 = "AND GETS PAID THERE"
    f_b2 = fit_font(d, bot2, 54, 1150)
    outlined_text(d, W / 2, TOP_BAR + SCENE_H + 92, bot2, f_b2, GOLD, stroke=8)

    canvas.save(ROOT / "meme.png")
    print(f"wrote {ROOT / 'meme.png'} {canvas.size}")


if __name__ == "__main__":
    main()
