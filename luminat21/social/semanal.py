"""Motor dos posts semanais do LuminaT21 (kit em luminat21/).

Saídas: slideN.jpg (carrossel Instagram com "Arraste" e numeração), resumo.jpg,
carrossel.pdf, story.jpg, reel.mp4 e reel-capa.jpg (sem "Arraste"/numeração).
Sem fotos reais de crianças: só o banner ilustrado do kit.
"""
import asyncio, pathlib, shutil, subprocess
from playwright.async_api import async_playwright

SOCIAL = pathlib.Path(__file__).parent.resolve()
KIT = SOCIAL.parent
ATIVOS = {
    "logo.png": KIT / "divulgacao" / "logo.png",
    "Courgette.woff2": KIT / "divulgacao" / "Courgette.woff2",
    "qr.svg": KIT / "divulgacao" / "qr.svg",
    "familias.jpg": KIT / "originais" / "banner-familias.jpg",
}

CSS = """@font-face{font-family:Courgette;src:url(Courgette.woff2)}*{margin:0;padding:0;box-sizing:border-box}
body{width:1080px;height:%(h)dpx;font-family:Inter,sans-serif;color:#17332f;background:#FBF6EE;position:relative;overflow:hidden}
body:after{content:"";position:absolute;left:-200px;bottom:-260px;width:700px;height:700px;border-radius:50%%;background:radial-gradient(circle,rgba(56,179,166,.16),transparent 65%%)}
.w{position:absolute;inset:%(ins)s;display:flex;flex-direction:column;z-index:2}.ct{flex:1;display:flex;flex-direction:column;justify-content:center}
.logo{height:86px;align-self:flex-start;margin-bottom:24px;flex-shrink:0}
.eb{font-size:28px;font-weight:800;letter-spacing:4px;color:#1A8580;text-transform:uppercase}
h1{font-family:Courgette;font-size:88px;line-height:1.1;color:#0F6A5E;font-weight:400;margin-top:14px}h1 span,h2 span{color:#C58712}
h2{font-family:Courgette;font-size:72px;line-height:1.12;color:#0F6A5E;font-weight:400;margin-top:12px}
p.t{font-size:38px;line-height:1.45;color:#3f5a55;margin-top:26px}
.foto{width:100%%;border-radius:34px;margin-top:34px;box-shadow:0 14px 40px rgba(15,106,94,.18)}
.cards{display:grid;gap:18px;margin-top:34px}.c{background:#fff;border-radius:24px;padding:24px 32px;border-left:10px solid #1A8580;box-shadow:0 6px 18px rgba(0,0,0,.05)}.c.d{border-left-color:#EAB12F}
.c b{font-size:36px;display:block;color:#0F6A5E}.c span{font-size:30px;color:#3f5a55;line-height:1.4;display:block;margin-top:4px}
.fases{display:flex;flex-wrap:wrap;gap:14px;margin-top:30px}.fases i{font-style:normal;font-size:30px;font-weight:700;color:#0F6A5E;background:#fff;border:3px solid #38B3A6;border-radius:999px;padding:12px 26px}
.cta{margin-top:40px;background:#1A8580;color:#fff;border-radius:30px;padding:34px 40px;display:flex;gap:32px;align-items:center}.cta img{width:190px;background:#fff;border-radius:18px;padding:10px}.cta b{font-family:Courgette;font-weight:400;font-size:54px;display:block;color:#FBE08A}.cta span{font-size:30px;display:block;margin-top:8px;line-height:1.4}
.ig{margin-top:22px;background:#fff;border:3px solid #EAB12F;border-radius:26px;padding:24px 32px;font-size:34px;color:#0F6A5E;line-height:1.35}.ig b{color:#C58712}
.av{font-size:30px;color:#6b7f7b;margin-top:24px;line-height:1.4}
.lema{font-family:Courgette;font-size:40px;color:#0F6A5E;margin-top:28px}.heart{color:#E2574C}
.pg{position:absolute;right:84px;bottom:52px;font-size:26px;color:#9aaba7;font-weight:700}.ar{position:absolute;left:84px;bottom:52px;font-size:28px;color:#1A8580;font-weight:700}
"""


def page(inner, formato="feed", n=None, tot=None):
    if formato == "feed":
        v = dict(h=1350, ins="78px 84px 120px")
    else:  # 1080x1920 com área segura (~250 px em cima, ~350 px embaixo)
        v = dict(h=1920, ins="270px 84px 400px")
    ex = ""
    if n:
        ex = f'<div class="pg">{n}/{tot}</div>' + ('<div class="ar">Arraste →</div>' if n < tot else "")
    return (f'<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><style>{CSS % v}</style></head>'
            f'<body><div class="w"><img class="logo" src="logo.png"><div class="ct">{inner}</div></div>{ex}</body></html>')


async def _render(b, html, saida, w, h, pasta):
    f = pasta / (saida.stem + ".html")
    f.write_text(html, encoding="utf-8")
    pg = await b.new_page(viewport={"width": w, "height": h})
    await pg.goto("file://" + str(f))
    await pg.evaluate("document.fonts.ready")
    await pg.wait_for_timeout(300)
    await pg.screenshot(path=str(saida), type="jpeg", quality=92)
    await pg.close()


def _video(frames, saida, dur=5.0, fade=0.6):
    ins, filt = [], []
    for fr in frames:
        ins += ["-loop", "1", "-framerate", "30", "-t", str(dur), "-i", str(fr)]
    ins += ["-f", "lavfi", "-t", "60", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100"]
    prev, off = "[0:v]", 0.0
    for i in range(1, len(frames)):
        off += dur - fade
        filt.append(f"{prev}[{i}:v]xfade=transition=fade:duration={fade}:offset={off:.2f}[v{i}]")
        prev = f"[v{i}]"
    total = dur * len(frames) - fade * (len(frames) - 1)
    filt.append(f"{prev}format=yuv420p,fps=30[vout]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *ins, "-filter_complex", ";".join(filt),
                    "-map", "[vout]", "-map", f"{len(frames)}:a", "-t", f"{total:.2f}",
                    "-c:v", "libx264", "-preset", "veryfast", "-profile:v", "high", "-crf", "20", "-r", "30",
                    "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(saida)], check=True)


def gerar(pasta, slides, resumo, story, reel):
    pasta = pathlib.Path(pasta)
    tmp = pasta / "_tmp"; tmp.mkdir(exist_ok=True)
    for nome, origem in ATIVOS.items():
        shutil.copy(origem, pasta / nome); shutil.copy(origem, tmp / nome)
    n = len(slides)

    async def main():
        async with async_playwright() as p:
            b = await p.chromium.launch(executable_path="/usr/bin/google-chrome")
            for i, c in enumerate(slides, 1):
                await _render(b, page(c, n=i, tot=n), pasta / f"slide{i}.jpg", 1080, 1350, pasta)
                await _render(b, page(c), tmp / f"pdf{i}.jpg", 1080, 1350, tmp)
            await _render(b, page(resumo), pasta / "resumo.jpg", 1080, 1350, pasta)
            await _render(b, page(story, "vertical"), pasta / "story.jpg", 1080, 1920, pasta)
            for i, c in enumerate(reel, 1):
                await _render(b, page(c, "vertical"), tmp / f"reel{i}.jpg", 1080, 1920, tmp)
            await b.close()

    asyncio.run(main())
    from PIL import Image
    ims = [Image.open(tmp / f"pdf{i}.jpg").convert("RGB") for i in range(1, n + 1)]
    ims[0].save(pasta / "carrossel.pdf", save_all=True, append_images=ims[1:], resolution=144)
    frames = [tmp / f"reel{i}.jpg" for i in range(1, len(reel) + 1)]
    shutil.copy(frames[0], pasta / "reel-capa.jpg")
    for i in range(1, len(reel) + 1):
        shutil.copy(tmp / f"reel{i}.html", pasta / f"reel{i}.html")
    _video(frames, pasta / "reel.mp4")
    shutil.rmtree(tmp)
