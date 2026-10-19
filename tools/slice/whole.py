OUTALL={}
for fn in sorted(os.listdir(ROOT)):
    if not fn.endswith('.xml'): continue
    RES={'vars':{},'events':{},'clips':set(),'brg':set(),'charprops':set()}
    run(fn,None,[],False)
    G=load(fn)
    OUTALL[fn]={'declared_vars':G['var'],'declared_types':G['vt'],'declared_events':G['ev'],'vars':RES['vars'],'events':RES['events'],'clips':sorted(RES['clips'])}
print(json.dumps(OUTALL,default=ser))
