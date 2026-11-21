"""História do CONSEG, do portal da Coordenadoria Estadual dos CONSEG (SSP-SP).

Fonte: http://www.ssp.sp.gov.br/conseg/portal/conseg/historia
Saída: conseg-cidadao/dados-ssp/historia.json e historia.md (texto oficial, sem alteração).
Rode antes do coletar_base.py, que junta a história aos trechos do Bip IA.

Uso: python3 conseg-cidadao/scripts/coletar_historia.py
"""
import html, json, pathlib, re, urllib.request
from datetime import datetime, timezone

URL = "http://www.ssp.sp.gov.br/conseg/v1/HistoriaGerenciador/GetByPortal"
DADOS = pathlib.Path(__file__).resolve().parents[1] / "dados-ssp"


def texto(h):
    h = re.sub(r"<br\s*/?>", "\n", h or "")
    h = re.sub(r"</p>|</li>|</h\d>", "\n\n", h)
    t = html.unescape(re.sub(r"<[^>]+>", "", h)).replace("\xa0", " ")
    t = re.sub(r"[ \t]+", " ", t)
    return re.sub(r"\n\s*\n+", "\n\n", t).strip()


def main():
    req = urllib.request.Request(URL, headers={"User-Agent": "CONSEG Cidadao (con.seg.br) - coleta publica semanal"})
    with urllib.request.urlopen(req, timeout=90) as r:
        dados = json.loads(r.read().decode("utf-8"))["data"] or []
    partes = [
        {"titulo": d["titulo"].strip(), "publicadoEm": (d.get("dataPublicacao") or "")[:10], "texto": texto(d.get("descricao"))}
        for d in sorted(dados, key=lambda x: int(x.get("ordem") or 0))
    ]
    agora = datetime.now(timezone.utc).isoformat(timespec="seconds")
    doc = {"fonte": "Coordenadoria Estadual dos CONSEG - SSP-SP (História do CONSEG)", "url": "http://www.ssp.sp.gov.br/conseg/portal/conseg/historia", "atualizadoEm": agora, "partes": partes}
    DADOS.mkdir(parents=True, exist_ok=True)
    (DADOS / "historia.json").write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    md = ["# História do CONSEG", "", f"Fonte: [Coordenadoria Estadual dos CONSEG (SSP-SP)]({doc['url']}). Cópia do texto oficial.", ""]
    for p in partes:
        md += [f"## {p['titulo']}", "", p["texto"], ""]
    (DADOS / "historia.md").write_text("\n".join(md), encoding="utf-8")
    print(f"ok: {len(partes)} partes da história")


if __name__ == "__main__":
    main()
