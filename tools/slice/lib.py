import sys, re, xml.etree.ElementTree as ET, os, json
ROOT=os.path.expanduser('~/skyrim-data-extracted/xml/meshes/actors/character/behaviors/')
def load(fn):
    t=ET.parse(ROOT+fn).getroot()
    objs={}
    for o in t.iter('hkobject'):
        n=o.get('name')
        if n: objs[n]=o
    sd=[o for o in objs.values() if o.get('class')=='hkbBehaviorGraphStringData'][0]
    gd=[o for o in objs.values() if o.get('class')=='hkbBehaviorGraphData'][0]
    def strs(p): 
        e=sd.find("hkparam[@name='%s']"%p); return [s.text or '' for s in e.findall('hkcstring')] if e is not None else []
    ev=strs('eventNames'); var=strs('variableNames'); cp=strs('characterPropertyNames')
    vi=gd.find("hkparam[@name='variableInfos']")
    vt=[]
    for o in vi.findall('hkobject'):
        vt.append(o.find("hkparam[@name='type']").text)
    return dict(objs=objs,ev=ev,var=var,vt=vt,cp=cp)
def P(o,name):
    e=o.find("hkparam[@name='%s']"%name); return None if e is None else e
def txt(o,name):
    e=P(o,name); return None if e is None else (e.text or '').strip()
def refs(o):
    out=set()
    for e in o.iter('hkparam'):
        if e.text:
            for m in re.findall(r'#\d+',e.text): out.add(m)
    return out
def closure(objs,roots):
    seen=set(); st=list(roots)
    while st:
        n=st.pop()
        if n in seen or n not in objs: continue
        seen.add(n); st.extend(refs(objs[n]))
    return seen
