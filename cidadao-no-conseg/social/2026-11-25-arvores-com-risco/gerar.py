"""Árvores com risco de queda: o caminho da rua até o CONSEG.
Fonte: SBT News, 23/11/2026 (temporal de 23/11 em SP)."""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from semanal import gerar, ck, passos

LG = '<img class="lg" src="cidadao-no-conseg-assinatura.svg">'
FONTE = '<p class="f">Fonte: SBT News, 23/11/2026</p>'

ABRE = ('<div class="eb">Depois do temporal</div><div class="big" style="margin-top:20px">36</div>'
        '<h2 style="margin-top:6px">chamados por <span class="g">queda de árvore</span> em um só dia.</h2>')
ABRE_P = ('<p class="s">Foi o que os Bombeiros registraram na segunda (23/11), na capital e na Grande SP. '
          'Árvore com risco na sua rua se resolve antes da próxima chuva.</p>')

SINAIS = ('<div class="eb t0">Repare na sua rua</div><h2>Sinais de que a árvore <span class="g">precisa de vistoria</span></h2>'
          + ck("rachado", "Tronco inclinado, rachado ou oco")
          + ck("arvore", "Galhos secos ou pendurados")
          + ck("fio", "Galhos encostando na fiação")
          + ck("calcada", "Raízes levantando a calçada")
          + '<p class="s" style="font-size:34px">Anote o endereço e tire foto. É o começo do pedido.</p>')

PASSOS = [
    ("Organize a rua", "O grupo do WhatsApp junta fotos e endereços."),
    ("Registre na subprefeitura", "Peça vistoria ou poda pelo 156 e guarde o protocolo."),
    ("Leve ao CONSEG", "Sem resposta? O tutor leva os protocolos à reunião mensal."),
    ("Acompanhe", "Cobre o retorno até a vistoria acontecer."),
]
CAMINHO = '<div class="eb t0">O caminho</div>' + passos(PASSOS)

EMERG = ('<div class="alerta"><b>Árvore caída ou fio no chão é emergência:</b> ligue 193 (Bombeiros) ou 199 (Defesa Civil). '
         'O Cidadão no CONSEG não é canal de emergência.</div>')
FIM = ('<div class="eb t0">Antes da próxima chuva</div><h2>A rua organizada <span class="g">pede antes de cair.</span></h2>'
       + EMERG + '<span class="btn">cidadaonoconseg.com.br</span>'
       '<div class="apep"><img src="apep-escudo.png"><span>Uma iniciativa da APEP Brasil.<br>Apartidária · 0% verba pública.</span></div>')

SLIDES = [LG + ABRE + ABRE_P + FONTE, SINAIS, CAMINHO, FIM]

RESUMO = (LG + '<h2 style="font-size:58px;margin-top:28px">36 chamados por <span class="g">queda de árvore</span> em um dia em SP.</h2>'
          '<p class="s" style="font-size:32px;margin-top:14px">Árvore com risco na sua rua? O caminho:</p>'
          + passos(PASSOS, compacto=True)
          + '<p class="s" style="font-size:30px;margin-top:18px">Emergência: 193 (Bombeiros) ou 199 (Defesa Civil).</p>'
          '<p class="f" style="margin-top:8px">Fonte: SBT News, 23/11/2026 · <span class="g">cidadaonoconseg.com.br</span></p>')

STORY = (LG + '<div class="big" style="margin-top:40px">36</div><h2 style="margin-top:6px">chamados por <span class="g">queda de árvore</span> em um só dia em SP.</h2>'
         '<p class="s">Árvore com risco na sua rua? Organize os vizinhos, peça vistoria à subprefeitura e leve ao CONSEG.</p>'
         '<span class="btn">cidadaonoconseg.com.br</span><p class="f">Fonte: SBT News, 23/11/2026</p>')

REEL = [
    LG + ABRE + '<p class="s">Bombeiros, segunda (23/11), capital e Grande SP.</p>' + FONTE,
    SINAIS,
    CAMINHO,
    '<div class="eb t0">Antes da próxima chuva</div><h2>A rua organizada <span class="g">pede antes de cair.</span></h2>' + EMERG
    + '<span class="btn">cidadaonoconseg.com.br</span><div class="apep"><img src="apep-escudo.png"><span>Uma iniciativa da APEP Brasil.<br>Apartidária · 0% verba pública.</span></div>',
]

if __name__ == "__main__":
    gerar(pathlib.Path(__file__).parent, SLIDES, RESUMO, STORY, REEL)
