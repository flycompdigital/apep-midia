"""Coleta os CONSEGs do Estado de São Paulo no portal público da Coordenadoria Estadual dos CONSEG (SSP-SP).

Fonte: http://www.ssp.sp.gov.br/conseg/portal/conseg/localize/null (API pública usada pela própria página).
Lógica do portal: município + CEP ou logradouro -> delegacia da área -> CONSEG.
Saída: cidadao-no-conseg/dados-ssp/consegs.json e, do presidente (cargo público), a foto em dados-ssp/presidentes/<id>.jpg.
Dos demais membros da diretoria guarda nome e cargo, sem foto.

Uso: python3 cidadao-no-conseg/scripts/coletar_consegs.py
"""
import base64, io, json, pathlib, re, sys, time, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

BASE = "http://www.ssp.sp.gov.br/conseg/api/v1/ConsegGerenciador/"
DADOS = pathlib.Path(__file__).resolve().parents[1] / "dados-ssp"
SAIDA = DADOS / "consegs.json"
FOTOS = DADOS / "presidentes"
# Nomes dos cargos como no próprio portal da SSP (idCargo).
CARGOS = {1: "Presidente", 2: "Vice-Presidente", 3: "Primeiro Secretário", 4: "Segundo Secretário", 6: "Diretor Social"}


def salva_foto(id_conseg, b64):
    """Guarda a foto do presidente (reduzida para 400 px, se o Pillow estiver instalado)."""
    try:
        dados = base64.b64decode(b64)
    except Exception:  # noqa: BLE001
        return None
    try:
        from PIL import Image

        im = Image.open(io.BytesIO(dados)).convert("RGB")
        im.thumbnail((400, 400))
        saida = io.BytesIO()
        im.save(saida, "JPEG", quality=82, optimize=True)
        dados = saida.getvalue()
    except Exception:  # noqa: BLE001
        pass
    FOTOS.mkdir(parents=True, exist_ok=True)
    (FOTOS / f"{id_conseg}.jpg").write_bytes(dados)
    return f"presidentes/{id_conseg}.jpg"
TERMOS = ["RUA", "AVENIDA", "PRACA", "ESTRADA", "A"]


def get(caminho, tentativas=4):
    url = BASE + caminho
    for t in range(tentativas):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "CONSEG Cidadao (con.seg.br) - coleta publica semanal", "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=90) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:  # noqa: BLE001
            if t == tentativas - 1:
                print(f"  falhou {caminho}: {e}", file=sys.stderr)
                return None
            time.sleep(2 * (t + 1))


def limpa(s):
    return re.sub(r"\s+", " ", s).strip() if isinstance(s, str) else s


def sem_numero(nome):
    return limpa(re.sub(r"^\s*\d+\s*[.\-)ºª°]?\s*", "", nome or ""))


def nome_de(o):
    return limpa(o.get("nome")) if isinstance(o, dict) and o.get("nome") else None


def resumo(c):
    """Campos úteis de um CONSEG, com a estrutura policial achatada."""
    dp = c.get("delegacia") or {}
    sec = dp.get("seccional") or {}
    cia = c.get("companhia") or {}
    btl = cia.get("batalhao") or {}
    return {
        "id": c["id"],
        "nome": limpa(c.get("nome")),
        "sigla": c.get("sigla"),
        "codigoRIC": c.get("codigoRIC"),
        "situacao": c.get("situacao"),
        "regiao": c.get("regiao"),
        "email": limpa(c.get("emailConseg")),
        "presidente": sem_numero(c.get("nomePresidenteConseg")) or None,
        "eleicao": (c.get("eleicao") or "")[:10] or None,
        "homologacao": (c.get("homologacao") or "")[:10] or None,
        "oficio": limpa(c.get("oficio")),
        "policiaCivil": {
            "idDelegacia": c.get("idDelegacia"),
            "delegacia": nome_de(dp),
            "seccional": nome_de(sec),
            "departamento": nome_de(sec.get("departamento")),
        },
        "policiaMilitar": {
            "idCompanhia": c.get("idCompanhia"),
            "companhia": nome_de(cia),
            "batalhao": nome_de(btl),
            "comando": nome_de(btl.get("comando")),
        },
    }


def consegs_do_municipio(mun, ids_esperados):
    """Acha uma delegacia do município por logradouro e devolve todos os CONSEGs do município."""
    vistos = {}
    delegacias_testadas = set()
    for termo in TERMOS:
        q = urllib.parse.urlencode({"idMunicipio": mun["id"], "municipioNome": mun["descricao"], "cep": "", "endereco": termo, "numero": 0})
        r = get(f"GetEnderecosByFilter?{q}")
        for end in (r or {}).get("data") or []:
            dp = end.get("idDelegacia")
            if not dp or dp in delegacias_testadas:
                continue
            delegacias_testadas.add(dp)
            d = (get(f"GetConsegsByFilter?idMunicipio={mun['id']}&delegacia={dp}") or {}).get("data")
            if not d:
                continue
            vistos[d["id"]] = d
            for c in (d.get("municipio") or {}).get("conseg") or []:
                vistos.setdefault(c["id"], c)
            if ids_esperados <= set(vistos):
                return vistos
            if len(delegacias_testadas) >= 6:
                break
        if vistos:
            return vistos
    return vistos


def main():
    municipios = {m["id"]: m for m in get("GetAllMunicipios")["items"]}
    lista = get("GetAllConseg")["data"]
    por_mun = {}
    for c in lista:
        por_mun.setdefault(c["idMunicipio"], set()).add(c["id"])
    print(f"{len(lista)} CONSEGs em {len(por_mun)} municípios")

    detalhes = {}

    def tarefa(id_mun):
        mun = municipios.get(id_mun)
        if not mun:
            return {}
        return consegs_do_municipio(mun, por_mun[id_mun])

    with ThreadPoolExecutor(max_workers=4) as ex:
        for i, achados in enumerate(ex.map(tarefa, por_mun), 1):
            detalhes.update(achados)
            if i % 25 == 0:
                print(f"  {i}/{len(por_mun)} municípios")

    def completa(c):
        reun = (get(f"GetReunioes?idConseg={c['id']}") or {}).get("data") or []
        dire = (get(f"GetMembrosDiretoria?idConseg={c['id']}") or {}).get("data") or []
        return c["id"], reun, dire

    saida = []
    extras = {}
    with ThreadPoolExecutor(max_workers=4) as ex:
        for id_c, reun, dire in ex.map(completa, lista):
            extras[id_c] = (reun, dire)

    for c in sorted(lista, key=lambda x: (municipios.get(x["idMunicipio"], {}).get("descricao", ""), x["nome"])):
        base = resumo(detalhes[c["id"]]) if c["id"] in detalhes else {"id": c["id"], "nome": limpa(c["nome"]), "semDetalhe": True}
        reun, dire = extras.get(c["id"], ([], []))
        base["idMunicipio"] = c["idMunicipio"]
        base["municipio"] = municipios.get(c["idMunicipio"], {}).get("descricao")
        base["reunioes"] = [
            {
                "data": r.get("data"),
                "local": limpa(r.get("local")),
                "endereco": limpa(r.get("endereco")),
                "cep": r.get("cep"),
                "online": r.get("tipoReuniao") == 1,
                "link": limpa(r.get("link")) or None,
                "pauta": limpa(r.get("pauta")) or None,
            }
            for r in reun
        ]
        base["diretoria"] = [
            {"nome": sem_numero(m.get("nome")), "idCargo": m.get("idCargo"), "cargo": CARGOS.get(m.get("idCargo"))}
            for m in sorted(dire, key=lambda m: m.get("idCargo") or 99)
            if m.get("nome")
        ]
        pres = next((m for m in dire if m.get("idCargo") == 1), None)
        base["presidenteFoto"] = salva_foto(c["id"], pres["foto"]) if pres and pres.get("foto") else None
        if pres and not base.get("presidente"):
            base["presidente"] = sem_numero(pres.get("nome"))
        saida.append(base)

    validas = {c["presidenteFoto"] for c in saida if c.get("presidenteFoto")}
    for f in FOTOS.glob("*.jpg") if FOTOS.exists() else []:
        if f"presidentes/{f.name}" not in validas:
            f.unlink()  # presidente trocou ou a foto saiu do portal
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    doc = {
        "fonte": "Coordenadoria Estadual dos CONSEG - SSP-SP (portal público)",
        "url": "http://www.ssp.sp.gov.br/conseg/portal/conseg/localize/null",
        "atualizadoEm": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "municipios": sorted(
            [{"id": i, "nome": municipios[i]["descricao"]} for i in por_mun if i in municipios], key=lambda m: m["nome"]
        ),
        "consegs": saida,
    }
    SAIDA.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    sem = sum(1 for c in saida if c.get("semDetalhe"))
    print(f"ok: {len(saida)} CONSEGs, {sem} sem detalhe, {sum(len(c['reunioes']) for c in saida)} reuniões agendadas -> {SAIDA}")


if __name__ == "__main__":
    main()
