fn=sys.argv[1]; want=set(sys.argv[2].split(',')); G=load(fn); objs=G['objs']; var=G['var']
from collections import deque
gr=[o for o in objs.values() if o.get('class')=='hkbBehaviorGraph'][0].get('name')
par={gr:None}; q=deque([gr])
while q:
    n=q.popleft()
    for x in sorted(refs(objs[n])):
        if x in objs and x not in par: par[x]=n; q.append(x)
def chain(n):
    c=[]
    while n:
        o=objs[n]
        if txt(o,'name'): c.append(txt(o,'name'))
        n=par.get(n)
    return ' <- '.join(c[:6])
for n,o in objs.items():
    vb=txt(o,'variableBindingSet')
    if vb and vb.startswith('#'):
        for b in P(objs[vb],'bindings').findall('hkobject'):
            if txt(b,'bindingType')=='BINDING_TYPE_VARIABLE' and var[int(txt(b,'variableIndex'))] in want:
                print(var[int(txt(b,'variableIndex'))],o.get('class'),txt(b,'memberPath'),'::',chain(n))
    if o.get('class') in('hkbExpressionDataArray','hkbExpressionCondition'):
        xs=[txt(x,'expression') for x in P(o,'expressionsData').findall('hkobject')] if o.get('class')=='hkbExpressionDataArray' else [txt(o,'expression')]
        for x in xs:
            ids=set(re.findall(r'[A-Za-z_]\w*',x or ''))&want
            if ids:
                lhs=re.match(r'\s*([A-Za-z_]\w*)\s*=(?!=)',x or '')
                print(sorted(ids),o.get('class'),'LHS='+(lhs.group(1) if lhs else '-'),'::',chain(par.get(n)))
