fn=sys.argv[1]; G=load(fn); objs=G['objs']; var=G['var']
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
        o=objs[n]; 
        if txt(o,'name'): c.append(txt(o,'name'))
        n=par.get(n)
    return ' <- '.join(c[:7])
for n,o in objs.items():
    if o.get('class') in sys.argv[2].split(','):
        print(o.get('class'),txt(o,'name'),'::',chain(n))
        if o.get('class')=='hkbEvaluateExpressionModifier':
            ea=objs[txt(o,'expressions')]
            for x in P(ea,'expressionsData').findall('hkobject'):
                ids=[i for i in re.findall(r'[A-Za-z_]\w*',txt(x,'expression') or '') ]
                print('   expr idents(vars only):',[i for i in ids if i in var], 'assignEvt', txt(x,'assignmentEventIndex'))
        vb=txt(o,'variableBindingSet')
        if vb and vb.startswith('#'):
            for b in P(objs[vb],'bindings').findall('hkobject'):
                if txt(b,'bindingType')=='BINDING_TYPE_VARIABLE': print('   bind',txt(b,'memberPath'),'->',var[int(txt(b,'variableIndex'))])
