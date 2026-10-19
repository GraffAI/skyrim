import sys
fn=sys.argv[1]; maxd=int(sys.argv[2])
G=load(fn); objs=G['objs']
root=[o for o in objs.values() if o.get('class')=='hkbBehaviorGraph'][0]
seen=set()
def walk(n,d):
    if n not in objs or d>maxd: return
    o=objs[n]; c=o.get('class')
    show = c in ('hkbStateMachine','hkbBehaviorReferenceGenerator','hkbStateMachineStateInfo','hkbBlenderGenerator','BSCyclicBlendTransitionGenerator','hkbManualSelectorGenerator','hkbClipGenerator')
    nd=d
    if show:
        extra=''
        if c=='hkbBehaviorReferenceGenerator': extra=txt(o,'behaviorName')
        if c=='hkbClipGenerator': extra=txt(o,'animationName')
        print('  '*d+'%s %s %s %s'%(n,c.replace('hkbStateMachine','SM'),txt(o,'name'),extra))
        nd=d+1
    if n in seen: return
    seen.add(n)
    for r in sorted(refs(o)):
        if r!=n: 
            rc=objs.get(r)
            if rc is not None and rc.get('class') in ('hkbVariableBindingSet','hkbStateMachineTransitionInfoArray','hkbStateMachineEventPropertyArray','hkbClipTriggerArray','hkbBlendingTransitionEffect'): continue
            walk(r,nd)
start=[o.get('name') for o in objs.values() if txt(o,'name')==sys.argv[3]][0] if len(sys.argv)>3 else root.get('name'); walk(start,0)
