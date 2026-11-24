"""Motor dos posts semanais do Cidadão no CONSEG.

Cada pasta AAAA-MM-DD-tema/ tem um gerar.py que define SLIDES, RESUMO, STORY e REEL
e chama gerar(). Saídas: slideN.jpg (carrossel Instagram, com "Arraste" e numeração),
resumo.jpg (Facebook/LinkedIn), carrossel.pdf (LinkedIn, sem "Arraste"/numeração),
story.jpg, reel.mp4 e reel-capa.jpg (sem "Arraste"/numeração).
"""
import asyncio, pathlib, shutil, subprocess
from playwright.async_api import async_playwright

SOCIAL = pathlib.Path(__file__).parent.resolve()
MARCA = SOCIAL.parent / "marca"
IMPRESSOS = SOCIAL.parent / "impressos"

CSS = """
*{margin:0;padding:0;box-sizing:border-box}
body{width:1080px;height:%(h)dpx;background:#17212d;color:#fff;font-family:Inter,sans-serif;position:relative;overflow:hidden}
body:before{content:"";position:absolute;right:-240px;top:-240px;width:760px;height:760px;border-radius:50%%;background:radial-gradient(circle,rgba(227,166,48,.22),transparent 65%%)}
.w{position:absolute;inset:%(ins)s;display:flex;flex-direction:column;justify-content:center;z-index:2}
.lg{height:92px;align-self:flex-start}
.eb{font-size:30px;font-weight:800;letter-spacing:5px;color:#e3a630;text-transform:uppercase;margin-top:36px}
.eb.t0{margin-top:0}
h1{font-family:'Inter Display',Inter;font-weight:900;font-size:90px;line-height:1.04;letter-spacing:-1.5px;margin-top:22px}
h2{font-family:'Inter Display',Inter;font-weight:900;font-size:70px;line-height:1.07;letter-spacing:-1px;margin-top:18px}
.g{color:#e3a630}
p.s{font-size:40px;line-height:1.42;color:#cbd5e1;margin-top:28px}
p.f{font-size:30px;color:#94a3b8;margin-top:28px}
.card{background:rgba(255,255,255,.06);border:2px solid rgba(255,255,255,.1);border-left:10px solid #e3a630;border-radius:26px;padding:24px 32px;margin-top:20px}
.card b{display:block;font-size:30px;color:#e3a630;letter-spacing:2px}.card h3{font-size:42px;margin-top:4px}.card p{font-size:32px;color:#cbd5e1;line-height:1.35;margin-top:6px}
.ck{display:flex;gap:24px;align-items:center;background:rgba(255,255,255,.06);border:2px solid rgba(255,255,255,.1);border-radius:24px;padding:22px 28px;margin-top:18px;font-size:38px;font-weight:600}
.ck svg{width:58px;height:58px;flex-shrink:0}
.alerta{background:#06543c;border-radius:28px;padding:30px 36px;margin-top:34px;font-size:34px;line-height:1.4}
.alerta b{color:#e3a630}
.foot{position:absolute;left:90px;right:90px;bottom:%(fb)dpx;display:flex;justify-content:space-between;align-items:center;font-size:28px;color:#94a3b8;border-top:2px solid rgba(255,255,255,.1);padding-top:24px;z-index:2}
.foot b{color:#fff}.sw{color:#e3a630;font-weight:700}
.btn{display:inline-block;margin-top:36px;background:#e3a630;color:#17212d;font-weight:900;font-size:40px;padding:24px 44px;border-radius:999px;align-self:flex-start}
.apep{display:flex;gap:22px;align-items:center;margin-top:36px;font-size:30px;color:#cbd5e1;line-height:1.35}.apep img{height:110px}
.big{font-family:'Inter Display',Inter;font-weight:900;font-size:220px;line-height:.9;color:#e3a630;letter-spacing:-6px}
"""

ICONES = {
 "arvore": '<svg viewBox="0 0 24 24" fill="none" stroke="#e3a630" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22v-7"/><path d="M8 15h8a5 5 0 0 0 1.5-9.8A5.5 5.5 0 0 0 7 5a4.5 4.5 0 0 0 1 10z"/></svg>',
 "fio": '<svg viewBox="0 0 24 24" fill="none" stroke="#e3a630" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M13 2 4 14h7l-1 8 9-12h-7z"/></svg>',
 "rachado": '<svg viewBox="0 0 24 24" fill="none" stroke="#e3a630" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2 9 8l4 3-3 5 2 6"/><rect x="4" y="2" width="16" height="20" rx="3"/></svg>',
 "calcada": '<svg viewBox="0 0 24 24" fill="none" stroke="#e3a630" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 20h20"/><path d="M4 20c2-5 4-7 8-7s6 2 8 7"/><path d="M12 13V4"/></svg>',
 "oco": '<svg viewBox="0 0 24 24" fill="none" stroke="#e3a630" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M12 8v5"/><path d="M12 16h.01"/></svg>',
 "semaforo": '<svg viewBox="0 0 24 24" fill="none" stroke="#e3a630" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="7" y="2" width="10" height="20" rx="3"/><circle cx="12" cy="7" r="1.6"/><circle cx="12" cy="12" r="1.6"/><circle cx="12" cy="17" r="1.6"/></svg>',
 "faixa": '<svg viewBox="0 0 24 24" fill="none" stroke="#e3a630" stroke-width="2" stroke-linecap="round"><path d="M5 4v16M9.5 4v16M14 4v16M18.5 4v16"/></svg>',
 "velocidade": '<svg viewBox="0 0 24 24" fill="none" stroke="#e3a630" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 18a8 8 0 1 1 16 0"/><path d="M12 18l4-6"/></svg>',
 "olho": '<svg viewBox="0 0 24 24" fill="none" stroke="#e3a630" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/></svg>',
}

ASSINA = '<span><b>Cidadão no CONSEG</b> · APEP Brasil</span>'


def ck(icone, texto):
    return f'<div class="ck">{ICONES[icone]}<span>{texto}</span></div>'


def passos(lista, compacto=False):
    if compacto:
        return ''.join(f'<div class="card" style="padding:18px 28px;margin-top:14px"><h3 style="font-size:36px;margin-top:0"><span class="g">{i}.</span> {t}</h3><p style="font-size:30px">{d}</p></div>' for i, (t, d) in enumerate(lista, 1))
    return ''.join(f'<div class="card"><b>{i}</b><h3>{t}</h3><p>{d}</p></div>' for i, (t, d) in enumerate(lista, 1))


def tela(corpo, direita, formato="feed"):
    if formato == "feed":
        v = dict(h=1350, ins="96px 90px 160px", fb=60)
    else:  # story/reel 1080x1920: área segura ~250 px em cima e ~350 px embaixo
        v = dict(h=1920, ins="270px 90px 500px", fb=380)
    return (f'<!DOCTYPE html><html lang="pt-BR"><head><meta charset="utf-8"><style>{CSS % v}</style></head>'
            f'<body><div class="w">{corpo}</div><div class="foot">{ASSINA}<span class="sw">{direita}</span></div></body></html>')


async def _render(b, html, saida, w, h, pasta):
    f = pasta / (saida.stem + ".html")
    f.write_text(html, encoding="utf-8")
    pg = await b.new_page(viewport={"width": w, "height": h})
    await pg.goto("file://" + str(f))
    await pg.evaluate("document.fonts.ready")
    await pg.wait_for_timeout(250)
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
        out = f"[v{i}]"
        filt.append(f"{prev}[{i}:v]xfade=transition=fade:duration={fade}:offset={off:.2f}{out}")
        prev = out
    total = dur * len(frames) - fade * (len(frames) - 1)
    filt.append(f"{prev}format=yuv420p,fps=30[vout]")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", *ins, "-filter_complex", ";".join(filt),
           "-map", "[vout]", "-map", f"{len(frames)}:a", "-t", f"{total:.2f}",
           "-c:v", "libx264", "-preset", "veryfast", "-profile:v", "high", "-crf", "20", "-r", "30",
           "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(saida)]
    subprocess.run(cmd, check=True)


def gerar(pasta, slides, resumo, story, reel):
    """slides: lista de (corpo_html); resumo/story: corpo_html; reel: lista de corpo_html."""
    pasta = pathlib.Path(pasta)
    for f in ["cidadao-no-conseg-assinatura.svg", "apep-escudo.png"]:
        shutil.copy(MARCA / f, pasta / f)
    shutil.copy(IMPRESSOS / "qr-conseg.svg", pasta / "qr-conseg.svg")
    tmp = pasta / "_tmp"; tmp.mkdir(exist_ok=True)
    n = len(slides)

    async def main():
        async with async_playwright() as p:
            b = await p.chromium.launch(executable_path="/usr/bin/google-chrome")
            for i, c in enumerate(slides, 1):
                dir_ = (f"Arraste →&nbsp;&nbsp;{i}/{n}" if i < n else f"{i}/{n}")
                await _render(b, tela(c, dir_), pasta / f"slide{i}.jpg", 1080, 1350, pasta)
                # versão limpa para o PDF do LinkedIn
                await _render(b, tela(c, "cidadaonoconseg.com.br"), tmp / f"pdf{i}.jpg", 1080, 1350, tmp)
            await _render(b, tela(resumo, "Apartidária · 0% verba pública"), pasta / "resumo.jpg", 1080, 1350, pasta)
            await _render(b, tela(story, "cidadaonoconseg.com.br", "vertical"), pasta / "story.jpg", 1080, 1920, pasta)
            for i, c in enumerate(reel, 1):
                await _render(b, tela(c, "cidadaonoconseg.com.br", "vertical"), tmp / f"reel{i}.jpg", 1080, 1920, tmp)
            await b.close()

    for f in ["cidadao-no-conseg-assinatura.svg", "apep-escudo.png", "qr-conseg.svg"]:
        shutil.copy(pasta / f, tmp / f)
    asyncio.run(main())
    from PIL import Image
    ims = [Image.open(tmp / f"pdf{i}.jpg").convert("RGB") for i in range(1, n + 1)]
    ims[0].save(pasta / "carrossel.pdf", save_all=True, append_images=ims[1:], resolution=144)
    frames = [tmp / f"reel{i}.jpg" for i in range(1, len(reel) + 1)]
    shutil.copy(frames[0], pasta / "reel-capa.jpg")
    for i, fr in enumerate(frames, 1):
        (pasta / f"reel{i}.html").write_text((tmp / f"reel{i}.html").read_text(encoding="utf-8"), encoding="utf-8")
    _video(frames, pasta / "reel.mp4")
    shutil.rmtree(tmp)
