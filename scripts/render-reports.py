from pathlib import Path
import re,html
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,PageBreak,Table,TableStyle
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
ROOT=Path(__file__).resolve().parents[1]
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='Text',fontName='Helvetica',fontSize=10,leading=14,spaceAfter=8))
styles['Heading1'].fontSize=18;styles['Heading1'].leading=22;styles['Heading1'].textColor=colors.HexColor('#99134b')
styles['Heading2'].fontSize=12;styles['Heading2'].leading=15;styles['Heading2'].spaceBefore=10
styles.add(ParagraphStyle(name='Cell',fontSize=9,leading=12))
def inline(t):
 t=html.escape(t.replace('—','-').replace('–','-').replace('→',' > '))
 t=re.sub(r'`([^`]+)`',r'<font name="Courier">\1</font>',t)
 t=re.sub(r'\*\*([^*]+)\*\*',r'<b>\1</b>',t)
 t=re.sub(r'\*([^*]+)\*',r'<i>\1</i>',t)
 return t

def footer(c,d):
 c.setStrokeColor(colors.HexColor('#dddde4'));c.line(42,39,A4[0]-42,39)
 c.setFont('Helvetica',8);c.setFillColor(colors.HexColor('#555566'));c.drawString(42,26,'FIAP | CardioIA Conectada | rm568506 | Dados sintéticos')
 c.drawRightString(A4[0]-42,26,str(d.page))
def render(source,name):
 text=(ROOT/source).read_text();blocks=re.split(r'\n\s*\n',text.strip());story=[]
 for b in blocks:
  if re.search('<!-- pagebreak -->',b,re.I):story.append(PageBreak());continue
  if b.startswith('|'):
   rows=[]
   for line in b.splitlines():
    if re.match(r'^\|[\s:|-]+\|$',line):continue
    rows.append([Paragraph(inline(x.strip()),styles['Cell']) for x in line.strip('|').split('|')])
   tab=Table(rows,colWidths=[165,125,205] if len(rows[0])==3 else None,hAlign='LEFT')
   tab.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#f1e8ee')),('GRID',(0,0),(-1,-1),.4,colors.HexColor('#dddddd')),('VALIGN',(0,0),(-1,-1),'TOP'),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]));story.extend([tab,Spacer(1,10)]);continue
  if b.startswith('# '):story.append(Paragraph(inline(b[2:]),styles['Heading1']));continue
  if b.startswith('## '):story.append(Paragraph(inline(b[3:]),styles['Heading2']));continue
  story.append(Paragraph(inline(b).replace('  \n','<br/>').replace('\n','<br/>' if b.startswith('- ') else ' '),styles['Text']))
 target=ROOT/'output/pdf'/name
 SimpleDocTemplate(str(target),pagesize=A4,rightMargin=42,leftMargin=42,topMargin=40,bottomMargin=51,title=name.replace('.pdf',''),author='Guilherme Yamada Dantas - rm568506').build(story,onFirstPage=footer,onLaterPages=footer)
 print(target)
for source,name in [('docs/edge/relatorio-edge.md','01-relatorio-edge.pdf'),('docs/mqtt/relatorio.md','02-relatorio-mqtt.pdf'),('docs/rest/relatorio.md','03-relatorio-rest.pdf'),('docs/ia/relatorio-comparativo.md','04-relatorio-ia.pdf')]:render(source,name)
