"""Rebuild the profile SVGs with Python standard-library tools only."""
from pathlib import Path
from html import escape
import xml.etree.ElementTree as ET
r=Path(__file__).resolve().parents[1];a=r/'assets';a.mkdir(exist_ok=True)
INK='#17243b';MUTED='#68758a';TEAL='#168c87';PURPLE='#8057cf';BLUE='#5c65dd';AMBER='#b97830'
def start(w,h,title,desc,bg='#ffffff'):
 return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc">',f'<title id="title">{escape(title)}</title><desc id="desc">{escape(desc)}</desc>',f'<rect width="{w}" height="{h}" rx="24" fill="{bg}"/>']
def text(s,x,y,value,size=18,color=INK,weight=400):s.append(f'<text x="{x}" y="{y}" font-family="Inter,Arial,sans-serif" font-size="{size}" fill="{color}" font-weight="{weight}">{escape(value)}</text>')
def rect(s,x,y,w,h,fill,stroke='none',radius=12):s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" stroke="{stroke}"/>')
def line(s,x1,y1,x2,y2,color,width=2):s.append(f'<path d="M{x1} {y1} L{x2} {y2}" stroke="{color}" stroke-width="{width}" fill="none"/>')
def circle(s,x,y,rad,fill,stroke='none'):s.append(f'<circle cx="{x}" cy="{y}" r="{rad}" fill="{fill}" stroke="{stroke}"/>')
def save(name,s):
 s.append('</svg>');body='\n'.join(s)+'\n';ET.fromstring(body);(a/name).write_text(body)
s=start(1440,440,'Prabal Pratap Singh — machine learning and software engineering','Software engineer in London. MEng Computer Science, University of Birmingham. Research, systems, and useful software.','#0e1729')
text(s,64,55,'PRBLYDV / LONDON',14,'#91a8ca',600)
text(s,64,138,'Prabal Pratap Singh',60,'#f5f7fc',700)
text(s,64,192,'Machine learning. Systems. Useful software.',28,'#cfdaed',500)
text(s,64,235,'MEng Computer Science · University of Birmingham',18,'#91a8ca')
# Abstract feature-flow illustration; decorative, not a performance chart.
for x,y in [(1060,94),(1220,74),(1345,144),(1250,236),(1080,236)]:
 for xx,yy in [(1160,154)]:line(s,x,y,xx,yy,'#354764',2)
 circle(s,x,y,6,'#8ba0c3')
for dx,dy,c in [(0,0,'#6ed4c3'),(28,-15,'#ad9ce9'),(28,15,'#83a9ec')]:circle(s,1146+dx,154+dy,12,c)
for x,y,txt,c in [(1025,58,'RESEARCH','#6ed4c3'),(1240,110,'BUILD','#ad9ce9'),(1166,282,'EVALUATE','#83a9ec')]:text(s,x,y,txt,12,c,600)
for x,title,detail,color in [(64,'ML RESEARCH','Speech · language · multimodal learning','#6ed4c3'),(510,'SYSTEMS','Python · C++ · training and evaluation','#ad9ce9'),(956,'PRODUCTS','Desktop tools · practical interfaces','#83a9ec')]:
 rect(s,x,325,420,82,'#18243a','#2b3a53');text(s,x+20,355,title,12,color,600);text(s,x+20,385,detail,16,'#d2dcee')
save('profile-hero.svg',s)
projects=[
 ('grammar-scoring.svg','01 / SPEECH + LANGUAGE','Spoken grammar scoring',['Research-led experiments with text,','speech features, and spectrograms.'],'Grouped validation · error analysis',TEAL,'Grammar scoring project with multimodal models and documented evaluation.'),
 ('poker-cfr.svg','02 / GAME THEORY + SYSTEMS','pokerCFR',['Deep CFR research with Python and C++','engines, training, evaluation, and a GUI.'],'Neural regret minimization · exact rules',PURPLE,'Poker research project with reference and native engines, Deep CFR, and evaluation.'),
 ('multimodal-hate.svg','03 / MULTIMODAL LEARNING','Video hate-speech detection',['Combine text, audio, and video features','with attention-based multimodal fusion.'],'HateMM-based research · PyTorch',BLUE,'Hate speech detection research combining text, audio, and video signals.'),
 ('tradelens.svg','04 / DESKTOP SOFTWARE','TradeLens',['A Windows companion for inspecting','MT5 trade risk before placing a trade.'],'Read-only analysis · visual explanations',AMBER,'TradeLens desktop tool for read-only trade risk analysis; it does not place orders.')]
for name,tag,title,desc,footer,color,alt in projects:
 s=start(700,278,title,alt,'#f7f9fc');rect(s,1,1,698,276,'#f7f9fc','#e2e7ef',20);rect(s,28,30,5,20,color,radius=2)
 text(s,46,45,tag,12,MUTED,600);text(s,28,103,title,29,INK,700)
 for i,row in enumerate(desc):text(s,28,147+i*27,row,19,MUTED)
 line(s,28,209,672,209,'#e2e7ef',1);text(s,28,246,footer,14,color,500);text(s,645,103,'↗',27,color,500);save(name,s)
s=start(1440,200,'Selected milestones','Recorded public leaderboard rank fifth in the SHL grammar assessment on 15 October 2026; MEng Computer Science; JEE Advanced rank 7999.','#f5f7fb')
for x,accent,big,title,note in [(30,TEAL,'5th','SHL assessment · public leaderboard','Recorded 15 Oct 2026 · public RMSE 0.3141'),(505,BLUE,'MEng','Computer Science','University of Birmingham'),(980,PURPLE,'7,999','JEE Advanced · All India Rank','Personal academic milestone')]:
 rect(s,x,18,430,164,'#ffffff','#e3e8f0',14);text(s,x+22,70,big,38,accent,700);text(s,x+22,109,title,17,INK,600);text(s,x+22,146,note,13,MUTED)
save('milestones.svg',s)
