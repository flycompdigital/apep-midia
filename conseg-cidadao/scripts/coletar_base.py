"""Base de conhecimento sobre segurança pública, a partir dos Downloads da Coordenadoria Estadual dos CONSEG (SSP-SP).

Fonte: http://www.ssp.sp.gov.br/conseg/portal/downloads (API pública usada pela própria página).

- dados-ssp/base-conhecimento.json: todas as seções e arquivos (título, tipo, id do arquivo oficial e situação do acesso).
- documentos/: cópia dos documentos oficiais, quando o servidor de arquivos da SSP permitir.
- dados-ssp/base-trechos.json: o texto, em trechos, dos documentos oficiais (legislação, roteiros, processo eleitoral,
  administração, treinamento etc.), usado pelo Bip IA como fonte.
  Obras com autor (biblioteca digital de monografias e e-books, hinos e canções) e imagens ficam só listadas,
  com link para o arquivo oficial; o conteúdo delas não é copiado.

Precisa de pdftotext (poppler-utils). .doc antigo usa antiword ou soffice, se houver; senão fica só listado.
Uso: python3 conseg-cidadao/scripts/coletar_base.py
"""
import html, json, urllib.error, pathlib, re, shutil, subprocess, sys, tempfile, time, unicodedata, urllib.parse, urllib.request, zipfile
from datetime import datetime, timezone

BASE = "http://www.ssp.sp.gov.br/conseg/v1/DownloadGerenciador/"
RAIZ = pathlib.Path(__file__).resolve().parents[1]
LISTA = RAIZ / "dados-ssp" / "base-conhecimento.json"
TRECHOS = RAIZ / "dados-ssp" / "base-trechos.json"
HISTORIA = RAIZ / "dados-ssp" / "historia.json"
DOCUMENTOS = RAIZ / "documentos"

# Seções cujo conteúdo não é copiado (obras com autor ou mídia): só título e link oficial.
SO_LISTAR = ("BIBLIOTECA DIGITAL", "HINOS E CAN")
# Documentos muito longos e genéricos que não entram nos trechos do Bip (ficam listados).
FORA_DOS_TRECHOS = ("CONSTITUIÇÃO DA REPÚBLICA",)
TEXTO = {"pdf", "docx", "doc"}
TAM_TRECHO = 1400


class Negado(Exception):
    pass


def pedir(url, binario=False, tentativas=4):
    for t in range(tentativas):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "CONSEG Cidadao (con.seg.br) - coleta publica semanal"})
            with urllib.request.urlopen(req, timeout=180) as r:
                dados = r.read()
                return dados if binario else json.loads(dados.decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code in (401, 403):
                raise Negado(e.code) from e
            if t == tentativas - 1:
                print(f"  falhou {url[:120]}: {e}", file=sys.stderr)
                return None
            time.sleep(3 * (t + 1))
        except Exception as e:  # noqa: BLE001
            if t == tentativas - 1:
                print(f"  falhou {url[:120]}: {e}", file=sys.stderr)
                return None
            time.sleep(3 * (t + 1))


def url_arquivo(arquivo_id):
    r = pedir(BASE + "GetURLArquivo/" + arquivo_id)
    if not r or not r.get("data"):
        return None
    p = urllib.parse.urlsplit(r["data"])
    return urllib.parse.urlunsplit((p.scheme, p.netloc, urllib.parse.quote(p.path), p.query, p.fragment))


def texto_pdf(caminho):
    if not shutil.which("pdftotext"):
        return ""
    r = subprocess.run(["pdftotext", "-layout", "-enc", "UTF-8", str(caminho), "-"], capture_output=True, timeout=300)
    return r.stdout.decode("utf-8", "ignore")


def texto_docx(caminho):
    try:
        with zipfile.ZipFile(caminho) as z:
            xml = z.read("word/document.xml").decode("utf-8", "ignore")
    except Exception:  # noqa: BLE001
        return ""
    xml = re.sub(r"</w:p>", "\n", xml)
    xml = re.sub(r"<w:tab/>", " ", xml)
    return html.unescape(re.sub(r"<[^>]+>", "", xml))


def texto_doc(caminho):
    if shutil.which("antiword"):
        r = subprocess.run(["antiword", str(caminho)], capture_output=True, timeout=120)
        return r.stdout.decode("utf-8", "ignore")
    if shutil.which("soffice"):
        with tempfile.TemporaryDirectory() as d:
            subprocess.run(["soffice", "--headless", "--convert-to", "txt:Text", "--outdir", d, str(caminho)], capture_output=True, timeout=180)
            saida = list(pathlib.Path(d).glob("*.txt"))
            return saida[0].read_text("utf-8", "ignore") if saida else ""
    return ""


def normaliza(t):
    t = t.replace("\r", "").replace("\x0c", "\n")
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r" *\n *", "\n", t)
    return re.sub(r"\n{3,}", "\n\n", t).strip()


def em_trechos(t):
    paragrafos = [p.strip() for p in re.split(r"\n\s*\n", t) if p.strip()]
    trechos, atual = [], ""
    for p in paragrafos:
        p = re.sub(r"\n", " ", p)
        while len(p) > TAM_TRECHO:
            corte = p.rfind(". ", 0, TAM_TRECHO)
            corte = corte + 1 if corte > TAM_TRECHO // 2 else TAM_TRECHO
            if atual:
                trechos.append(atual)
                atual = ""
            trechos.append(p[:corte].strip())
            p = p[corte:].strip()
        if len(atual) + len(p) + 1 > TAM_TRECHO and atual:
            trechos.append(atual)
            atual = p
        else:
            atual = f"{atual}\n{p}" if atual else p
    if atual:
        trechos.append(atual)
    return [x for x in trechos if len(x) > 40]


def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:60]


def main():
    dados = pedir(BASE + "GetByPortal?termo=")["data"]
    secoes, trechos = [], []

    def percorre(no, secao, codigo, itens):
        for i, f in enumerate(sorted(no.get("filhos") or [], key=lambda x: (x.get("grupoPai") or {}).get("codigoFilho", 0) or 0), 1):
            cod = f"{codigo}.{(f.get('grupoPai') or {}).get('codigoFilho') or i}"
            if f.get("arquivoId"):
                nome_arq = f.get("nomeDoAnexo") or ""
                ext = nome_arq.rsplit(".", 1)[-1].lower() if "." in nome_arq else ""
                copiar = ext in TEXTO and not secao.upper().startswith(SO_LISTAR)
                itens.append({"codigo": cod, "titulo": f["nome"].strip(), "arquivoId": f["arquivoId"], "arquivo": nome_arq, "tipo": ext, "copiado": copiar})
            percorre(f, secao, cod, itens)

    for sec in sorted(dados, key=lambda x: (x.get("grupoPai") or {}).get("codigoPai", 0) or 0):
        cod = str((sec.get("grupoPai") or {}).get("codigoPai") or len(secoes) + 1)
        itens = []
        percorre(sec, sec["nome"], cod, itens)
        secoes.append({"codigo": cod, "nome": sec["nome"].strip(), "itens": itens})

    total = sum(len(s["itens"]) for s in secoes)
    print(f"{len(secoes)} seções, {total} arquivos")

    negados = 0
    with tempfile.TemporaryDirectory() as tmp:
        for s in secoes:
            for it in s["itens"]:
                if not it["copiado"]:
                    continue
                if negados >= 3:  # o servidor de arquivos está recusando este acesso: não insiste
                    it["copiado"] = False
                    it["acesso"] = "negado (não testado nesta coleta)"
                    continue
                url = url_arquivo(it["arquivoId"])
                try:
                    bruto = pedir(url, binario=True, tentativas=2) if url else None
                except Negado as e:
                    negados += 1
                    it["acesso"] = f"negado ({e})"
                    print(f"  acesso negado ({e}) ao arquivo {it['codigo']}", file=sys.stderr)
                    bruto = None
                if not bruto:
                    it["copiado"] = False
                    continue
                it["acesso"] = "ok"
                destino = DOCUMENTOS / slug(s["nome"]) / f"{it['codigo']}-{slug(it['titulo'])}.{it['tipo']}"
                destino.parent.mkdir(parents=True, exist_ok=True)
                destino.write_bytes(bruto)
                it["copia"] = str(destino.relative_to(RAIZ))
                arq = pathlib.Path(tmp) / f"a.{it['tipo']}"
                arq.write_bytes(bruto)
                t = {"pdf": texto_pdf, "docx": texto_docx, "doc": texto_doc}[it["tipo"]](arq)
                t = normaliza(t)
                if len(t) < 80:
                    it["copiado"] = False
                    continue
                it["caracteres"] = len(t)
                if it["titulo"].upper().startswith(FORA_DOS_TRECHOS):
                    continue
                fonte = f"{it['codigo']} - {it['titulo']}"
                for n, tr in enumerate(em_trechos(t)):
                    trechos.append({"id": f"{slug(it['titulo'])}-{n}", "fonte": fonte, "secao": s["nome"], "arquivoId": it["arquivoId"], "texto": tr})
                print(f"  {it['codigo']} {it['titulo'][:60]} ({len(t)} caracteres)")

    if HISTORIA.exists():
        for parte in json.loads(HISTORIA.read_text("utf-8")).get("partes", []):
            for n, tr in enumerate(em_trechos(parte["texto"])):
                trechos.append({"id": f"historia-{slug(parte['titulo'])}-{n}", "fonte": f"História do CONSEG - {parte['titulo']}", "secao": "HISTÓRIA", "texto": tr})

    agora = datetime.now(timezone.utc).isoformat(timespec="seconds")
    meta = {"fonte": "Coordenadoria Estadual dos CONSEG - SSP-SP (Downloads)", "url": "http://www.ssp.sp.gov.br/conseg/portal/downloads", "atualizadoEm": agora}
    LISTA.parent.mkdir(parents=True, exist_ok=True)
    LISTA.write_text(json.dumps({**meta, "secoes": secoes}, ensure_ascii=False, indent=1), encoding="utf-8")
    if negados >= 3 and TRECHOS.exists():
        antigo = [t for t in json.loads(TRECHOS.read_text("utf-8")).get("trechos", []) if t.get("secao") != "HISTÓRIA"]
        if antigo and not any(t.get("secao") != "HISTÓRIA" for t in trechos):  # mantém o texto já copiado numa coleta anterior
            trechos = antigo + trechos
    TRECHOS.write_text(json.dumps({**meta, "trechos": trechos}, ensure_ascii=False), encoding="utf-8")
    copiados = sum(1 for s in secoes for i in s["itens"] if i["copiado"])
    print(f"ok: {copiados} documentos copiados, {len(trechos)} trechos" + (" (servidor de arquivos da SSP negou o acesso)" if negados >= 3 else ""))


if __name__ == "__main__":
    main()
