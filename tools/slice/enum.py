from collections import Counter
C=Counter(); B=Counter()
def rec(e,path,cls):
    for p in e.findall('hkparam'):
        nm=p.get('name'); np=path+[nm]
        t=(p.text or '').strip()
        if re.fullmatch(r'-?\d+',t) and (nm in('id','eventId') or 'event' in nm.lower()): C[(cls,'.'.join(np))]+=1
        for sub in p.findall('hkobject'): rec(sub,np,cls)
for fn in sorted(os.listdir(ROOT)):
    if not fn.endswith('.xml'): continue
    G=load(fn)
    for o in G['objs'].values():
        rec(o,[],o.get('class'))
        if o.get('class')=='hkbVariableBindingSet':
            pass
for k,v in sorted(C.items()): print(v,k)
