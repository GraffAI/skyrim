fn=sys.argv[1]; G=load(fn); objs=G['objs']; var=G['var']; ev=G['ev']
def binds(o):
    vb=txt(o,'variableBindingSet'); out=[]
    if vb and vb.startswith('#'):
        for b in P(objs[vb],'bindings').findall('hkobject'):
            if txt(b,'bindingType')=='BINDING_TYPE_VARIABLE': out.append((txt(b,'memberPath'),var[int(txt(b,'variableIndex'))]))
    return out
def trans(a):
    out=[]
    if not a or not a.startswith('#'): return out
    for t in P(objs[a],'transitions').findall('hkobject'):
        e=int(txt(t,'eventId')); c=txt(t,'condition'); cs=''
        if c and c.startswith('#'): co=objs[c]; cs=co.get('class')+':'+','.join(i for i in re.findall(r'[A-Za-z_]\w*',txt(co,'expression') or txt(co,'conditionString') or '') if i in var)
        out.append((ev[e] if e>=0 else None, int(txt(t,'toStateId')), cs, txt(t,'flags')))
    return out
for name in sys.argv[2].split(','):
    n=[k for k,o in objs.items() if txt(o,'name')==name][0]; o=objs[n]
    print('==',o.get('class'),name,'startStateId',txt(o,'startStateId'),'binds',binds(o))
    if o.get('class')=='hkbStateMachine':
        print('  wildcard:',trans(txt(o,'wildcardTransitions')))
        for s in (P(o,'states').text or '').split():
            so=objs[s]
            def nev(p):
                a=txt(so,p); 
                return [ev[int(txt(x,'id'))] for x in P(objs[a],'events').findall('hkobject')] if a and a.startswith('#') else []
            print('  state',txt(so,'stateId'),txt(so,'name'),'enter',nev('enterNotifyEvents'),'exit',nev('exitNotifyEvents'))
            for t in trans(txt(so,'transitions')): print('     ->',t)
    if o.get('class')=='hkbClipGenerator':
        tr=txt(o,'triggers')
        if tr and tr.startswith('#'):
            print('  triggers:',[ev[int(x.find("hkparam[@name='event']/hkobject/hkparam[@name='id']").text)] for x in P(objs[tr],'triggers').findall('hkobject')])
