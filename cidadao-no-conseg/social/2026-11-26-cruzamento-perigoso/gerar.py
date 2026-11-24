"""Cruzamento perigoso: do relato dos vizinhos ao pedido na CET e no CONSEG.
Fontes: Urgente News, com informações do Metrópoles (23/11/2026); Encontra Jardim Anália Franco (23/10/2026)."""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from semanal import gerar, ck, passos

LG = '<img class="lg" src="cidadao-no-conseg-assinatura.svg">'
FONTE = '<p class="f">Fonte: Urgente News, com informações do Metrópoles, 23/11/2026</p>'

ABRE = ('<div class="eb">Jabaquara, zona sul de SP</div>'
        '<h1>Um cruzamento que <span class="g">os moradores já conheciam.</span></h1>')
ABRE_P = ('<p class="s">No sábado (21/11), uma mulher foi atropelada na faixa de pedestres no cruzamento das avenidas '
          'Rodrigues Montemor e Benigno Carrera. Moradores relatam histórico de colisões no local.</p>')

PROVA = ('<div class="eb t0">Risco conhecido</div><h2>O susto de cada dia <span class="g">vira prova.</span></h2>'
         '<p class="s" style="font-size:36px">Batidas e quase-atropelamentos anotados com data, horário e local sustentam o pedido de:</p>'
         + ck("faixa", "Sinalização e faixa bem visível")
         + ck("semaforo", "Ajuste no tempo do semáforo")
         + ck("velocidade", "Redução e fiscalização de velocidade")
         + ck("olho", "Mais atenção do policiamento no trecho"))

PASSOS = [
    ("Organize a rua", "O grupo do WhatsApp reúne os relatos do cruzamento."),
    ("Registre na CET", "Peça estudo do local pelo 156, com fotos, e guarde o protocolo."),
    ("Leve ao CONSEG", "O tutor apresenta a pauta à PM, à Polícia Civil e aos órgãos presentes."),
    ("Acompanhe", "Cobre o retorno nas reuniões seguintes."),
]
CAMINHO = '<div class="eb t0">O caminho</div>' + passos(PASSOS)

EXEMPLO = ('<div class="eb t0">Funciona assim</div><h2>No CONSEG Tatuapé, <span class="g">a pauta andou.</span></h2>'
           '<p class="s" style="font-size:36px">Em outubro, moradores levaram à reunião um cruzamento com atropelamentos. '
           'A Prefeitura e a CET se comprometeram a estudar uma solução para o local.</p>'
           '<p class="f">Fonte: Encontra Jardim Anália Franco, 23/10/2026</p>'
           '<div class="alerta"><b>Em emergência, ligue 190.</b> O Cidadão no CONSEG não é canal de emergência.</div>'
           '<span class="btn">cidadaonoconseg.com.br</span>')

SLIDES = [LG + ABRE + ABRE_P + FONTE, PROVA, CAMINHO, EXEMPLO]

RESUMO = (LG + '<h2 style="font-size:56px;margin-top:26px">Cruzamento perigoso <span class="g">não pode ficar só na conversa.</span></h2>'
          '<p class="s" style="font-size:30px;margin-top:12px">No Jabaquara, moradores relatam histórico de colisões no cruzamento onde uma mulher foi atropelada no sábado (21/11). O caminho:</p>'
          + passos(PASSOS, compacto=True)
          + '<p class="f" style="margin-top:16px">Fonte: Urgente News / Metrópoles · <span class="g">cidadaonoconseg.com.br</span></p>')

STORY = (LG + '<h1 style="margin-top:40px">Cruzamento perigoso <span class="g">não pode ficar só na conversa.</span></h1>'
         '<p class="s">Junte os relatos da rua, peça estudo à CET pelo 156 e leve a pauta à reunião do CONSEG.</p>'
         '<span class="btn">cidadaonoconseg.com.br</span><p class="f">Caso do Jabaquara: Urgente News, com informações do Metrópoles</p>')

REEL = [
    LG + ABRE + '<p class="s">Moradores relatam histórico de colisões no cruzamento onde uma mulher foi atropelada na faixa, no sábado (21/11).</p>' + FONTE,
    PROVA,
    CAMINHO,
    EXEMPLO,
]

if __name__ == "__main__":
    gerar(pathlib.Path(__file__).parent, SLIDES, RESUMO, STORY, REEL)
