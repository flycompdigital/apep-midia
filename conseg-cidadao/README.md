# CONSEG Cidadão (con.seg.br)

| Pasta | O que tem |
|---|---|
| `dados-ssp/` | Cópia semanal dos dados públicos da Coordenadoria Estadual dos CONSEG (SSP-SP) |
| `documentos/` | Cópia dos documentos oficiais dos Downloads da SSP (assim que a SSP liberar o acesso) |
| `scripts/` | Coletores (rodam toda segunda pela rotina `.github/workflows/atualizar-ssp.yml`) |
| `social/` | Posts e roteiros de vídeo (lançamento, app e Bip IA, HeyGen) |
| `impressos/` | Folder A4 e QR Code |
| `marca/` | Logo do CONSEG Cidadão e da APEP |

## dados-ssp

- `consegs.json`: 446 CONSEGs em 294 municípios. Para cada um: e-mail, delegacia (Polícia Civil), companhia, batalhão e comando (PM), reuniões agendadas e a diretoria com nome e cargo.
- `presidentes/`: foto do presidente de cada CONSEG, quando publicada pela SSP (cargo público). Dos demais cargos guardamos só nome e cargo.
- `base-conhecimento.json`: as 11 seções e os 207 arquivos dos Downloads, com a situação do acesso.
- `base-trechos.json`: texto em trechos usado pelo Bip IA (hoje, só a história, porque os arquivos estão bloqueados).
- `historia.json` e `historia.md`: a história do CONSEG, como publicada no portal.
- `arquivos-bloqueados-401.md` e `.csv`: lista dos arquivos que a SSP bloqueia (para o pedido formal da APEP).

Fontes:
- http://www.ssp.sp.gov.br/conseg/portal/conseg/localize/null
- http://www.ssp.sp.gov.br/conseg/portal/downloads
- http://www.ssp.sp.gov.br/conseg/portal/conseg/historia

Para rodar à mão: `pip install pillow`, depois `python3 conseg-cidadao/scripts/coletar_historia.py`, `coletar_consegs.py` e `coletar_base.py`, nessa ordem.
