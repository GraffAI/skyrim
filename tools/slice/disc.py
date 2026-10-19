for fn in sorted(os.listdir(ROOT)):
    if not fn.endswith('.xml'): continue
    G=load(fn); objs=G['objs']
    brg=[(txt(o,'name'),txt(o,'behaviorName')) for o in objs.values() if o.get('class')=='hkbBehaviorReferenceGenerator']
    print(fn,'vars',len(G['var']),'events',len(G['ev']),'brg',brg)
