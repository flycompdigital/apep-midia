"""LuminaT21: 3 de dezembro, Dia Internacional das Pessoas com Deficiência (ONU).
Divulgação do portal luminat21.org (Lumina) e do perfil @familiast21_zonaleste."""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from semanal import gerar

AV = '<p class="av">A Lumina orienta e encaminha, mas não substitui médicos e terapeutas.</p>'
ABRE = ('<div class="eb">3 de dezembro · Dia Internacional das Pessoas com Deficiência</div>'
        '<h1>Inclusão <span>se faz junto.</span></h1>')
FOTO = '<img class="foto" src="familias.jpg">'

INFO = ('<div class="eb">Informação que acolhe</div><h2>Dúvidas fazem parte <span>do caminho</span></h2>'
        '<p class="t">No portal LuminaT21, a Lumina responde às dúvidas das famílias de pessoas com síndrome de Down, '
        'a qualquer hora e em linguagem simples, com um guia para cada fase da vida.</p>'
        '<div class="fases"><i>Primeiro mês</i><i>Primeiro ano</i><i>Infância</i><i>Adolescência</i><i>Vida adulta</i></div>' + AV)

REDE = ('<div class="eb">Ninguém caminha sozinho</div><h2>Uma rede de famílias <span>na Zona Leste</span></h2>'
        '<p class="t">O perfil @familiast21_zonaleste conecta famílias T21 da Zona Leste de São Paulo para trocar experiências e apoio.</p>'
        '<div class="cards"><div class="c"><b>Troca de experiências</b><span>Quem vive o mesmo caminho entende.</span></div>'
        '<div class="c d"><b>Entre no grupo</b><span>Cadastro pelo portal luminat21.org.</span></div></div>')

CTA = ('<h2>Faça parte <span>dessa rede</span></h2>'
       '<div class="cta"><img src="qr.svg"><div><b>luminat21.org</b><span>Converse com a Lumina e entre no grupo de famílias.</span></div></div>'
       '<div class="ig">Siga <b>@familiast21_zonaleste</b> no Instagram</div>'
       '<p class="lema">A luz do amor <span class="heart">♥</span> a força da inclusão.</p>')

SLIDES = [ABRE + FOTO, INFO, REDE, CTA]

RESUMO = (ABRE + FOTO.replace('class="foto"', 'class="foto" style="margin-top:20px;width:600px;align-self:center"')
          + '<p class="t" style="font-size:31px;margin-top:18px">A Lumina tira dúvidas das famílias de pessoas com síndrome de Down, a qualquer hora. '
          'E @familiast21_zonaleste conecta famílias T21 da Zona Leste de SP.</p>'
          '<div class="cta" style="margin-top:22px;padding:22px 30px"><img src="qr.svg" style="width:140px"><div><b style="font-size:46px">luminat21.org</b>'
          '<span>Converse com a Lumina e entre no grupo.</span></div></div>'
          '<p class="av" style="margin-top:14px">A Lumina orienta e encaminha, mas não substitui médicos e terapeutas.</p>')

STORY = (ABRE + FOTO + '<p class="t">Informação e uma rede de famílias T21 na Zona Leste de SP.</p>'
         '<div class="cta"><img src="qr.svg"><div><b>luminat21.org</b><span>Siga @familiast21_zonaleste</span></div></div>')

REEL = [ABRE + FOTO, INFO, REDE, CTA]

if __name__ == "__main__":
    gerar(pathlib.Path(__file__).parent, SLIDES, RESUMO, STORY, REEL)
