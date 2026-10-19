# usage: spec = list of (file, root_node_name or None, [stop node names], context:bool)
LISTEN={'EventToCrossBlend','EventToFreezeBlendValue','eventToCheckFor','activateEventId','deactivateEventId','startMatchingEventId','startPlayingEventId','randomTransitionEventId','returnToPreviousStateEventId','transitionToNextHigherStateEventId','transitionToNextLowerStateEventId','eventId','enterEventId','exitEventId'}
RAISE={'eventToSend','event','EventToSend1','EventToSend2','EventToSend3','targetOutOfLimitEvent','contactEvent','alarmEvent','ungroundedEvent','eventToSendWhenStateOrTransitionChanges','events','triggers','eventData','assignmentEventIndex'}
OUT={('hkbStateMachine','isActive'),('hkbStateMachine','currentStateId'),('BSInterpValueModifier','result'),('hkbDampingModifier','dampedValue'),('hkbDampingModifier','dampedVector'),('BSSpeedSamplerModifier','speedOut'),('BSDirectAtModifier','currentHeadingOffset'),('BSDirectAtModifier','currentPitchOffset'),('BSLookAtModifier','targetOutsideLimits'),('BSIStateManagerModifier','iStateVar'),('BSGetTimeStepModifier','timeStep'),('BSDecomposeVectorModifier','x'),('BSDecomposeVectorModifier','y'),('BSDecomposeVectorModifier','z'),('BSDecomposeVectorModifier','w'),('hkbTransformVectorModifier','vectorOut'),('hkbFootIkControlsModifier','errorOut'),('hkbFootIkModifier','errorOutTranslation'),('hkbFootIkModifier','alignWithGroundRotation')}
def isout(cls,mp):
    head=mp.split('/')[0].split(':')[0]
    if cls=='BSIsActiveModifier' and head.startswith('bIsActive'): return True
    return (cls,head) in OUT
def ownerof(objs):
    m={}
    for n,o in objs.items():
        p=P(o,'variableBindingSet')
        if p is not None and (p.text or '').strip().startswith('#'): m[p.text.strip()]=n
    return m
def byname(objs,name):
    r=[n for n,o in objs.items() if txt(o,'name')==name]; return r[0]
def closure2(objs,roots,stops):
    seen=set(); st=list(roots)
    while st:
        n=st.pop()
        if n in seen or n not in objs: continue
        seen.add(n)
        if n in stops: continue
        st.extend(refs(objs[n]))
    return seen
def scan(G,nodes,res,fn,tfilter=None):
    objs=G['objs']; ev=G['ev']; var=G['var']; own=ownerof(objs)
    def addev(i,kind,where):
        i=int(i)
        if i<0 or i>=len(ev): return
        res['events'].setdefault(ev[i],{'L':set(),'R':set(),'files':set()})
        res['events'][ev[i]][kind].add(where); res['events'][ev[i]]['files'].add(fn)
    def addvar(name,kind,where):
        res['vars'].setdefault(name,{'type':G['vt'][var.index(name)] if name in var else '?','R':set(),'W':set(),'files':set()})
        res['vars'][name][kind].add(where); res['vars'][name]['files'].add(fn)
    def walkev(e,cls,top):
        for p in e.findall('hkparam'):
            nm=p.get('name'); t=(p.text or '').strip()
            tp=top or nm
            if re.fullmatch(r'-?\d+',t) and (nm in('id','eventId','enterEventId','exitEventId') or nm in LISTEN or nm=='assignmentEventIndex'):
                key=nm if nm!='id' else tp
                if key in LISTEN or nm in('eventId','enterEventId','exitEventId'): addev(t,'L',cls+'.'+tp)
                elif key in RAISE: addev(t,'R',cls+'.'+tp)
            for sub in p.findall('hkobject'): walkev(sub,cls,tp)
    for n in nodes:
        o=objs[n]; cls=o.get('class')
        if cls=='hkbClipGenerator': res['clips'].add((fn,txt(o,'name'),txt(o,'animationName')))
        if cls=='hkbBehaviorReferenceGenerator': res['brg'].add(txt(o,'behaviorName'))
        if cls=='hkbStateMachineTransitionInfoArray' and tfilter is not None:
            for t in P(o,'transitions').findall('hkobject'):
                if not tfilter(n,t): continue
                for k in ('eventId',):
                    addev(txt(t,k),'L',cls+'.transitions')
                c=txt(t,'condition')
                if c and c.startswith('#'): nodes_extra.append(c)
            continue
        walkev(o,cls,None)
        if cls=='hkbStateMachine':
            s=txt(o,'syncVariableIndex')
            if s and int(s)>=0: addvar(var[int(s)],'R','hkbStateMachine.syncVariableIndex')
        if cls=='hkbVariableBindingSet':
            ow=objs[own[n]].get('class') if n in own else '?'
            for b in P(o,'bindings').findall('hkobject'):
                if txt(b,'bindingType')!='BINDING_TYPE_VARIABLE': 
                    res['charprops'].add(txt(b,'memberPath')); continue
                vi=int(txt(b,'variableIndex')); mp=txt(b,'memberPath')
                addvar(var[vi],'W' if isout(ow,mp) else 'R',ow+'.'+mp)
        exprs=[]
        if cls=='hkbExpressionCondition': exprs.append(txt(o,'expression'))
        if cls=='hkbExpressionDataArray':
            for x in P(o,'expressionsData').findall('hkobject'): exprs.append(txt(x,'expression'))
        for x in exprs:
            x=x or ''
            m=re.match(r'\s*([A-Za-z_]\w*)\s*=(?!=)\s*(.*)',x)
            if m:
                if m.group(1) in var: addvar(m.group(1),'W',cls+'.lhs')
                rhs=m.group(2)
            else: rhs=x
            for idn in re.findall(r'[A-Za-z_]\w*',rhs):
                if idn in var: addvar(idn,'R',cls+'.expr')
                elif idn in ev: addev(ev.index(idn),'R',cls+'.expr')
nodes_extra=[]
def run(fn,root,stops,context,ctx_sms=None):
    G=load(fn); objs=G['objs']
    stopn={byname(objs,s) for s in stops}
    r=byname(objs,root) if root else [o for o in objs.values() if o.get('class')=='hkbBehaviorGraph'][0].get('name')
    nodes=closure2(objs,[r],stopn)
    scan(G,nodes,RES,fn)
    if context:
        # BFS parents, then for each ancestor: own params; transitions into/out of on-path states
        from collections import deque
        gr=[o for o in objs.values() if o.get('class')=='hkbBehaviorGraph'][0].get('name')
        par={gr:None}; q=deque([gr])
        while q:
            n=q.popleft()
            for x in sorted(refs(objs[n])):
                if x in objs and x not in par: par[x]=n; q.append(x)
        chain=[]; n=par[r]
        while n: chain.append(n); n=par[n]
        chainset=set(chain)|{r}
        onpath_ids={}
        ctx=set()
        for n in chain:
            o=objs[n]; cls=o.get('class')
            for x in refs(o):
                if x in objs and objs[x].get('class') in ('hkbVariableBindingSet','hkbStateMachineEventPropertyArray'): ctx.add(x)
        global nodes_extra; nodes_extra=[]
        for n in chain:
            o=objs[n]
            if o.get('class')=='hkbModifierGenerator':
                m=txt(o,'modifier')
                if m and m.startswith('#'): scan(G,closure2(objs,[m],set()),RES,fn+'#mg')
            if o.get('class')!='hkbStateMachine': continue
            if ctx_sms is not None and txt(o,'name') not in ctx_sms: continue
            states=[]
            for s in (P(o,'states').text or '').split():
                so=objs[s]; states.append((s,int(txt(so,'stateId'))))
            pathids={sid for s,sid in states if s in chainset}
            pathstates={s for s,sid in states if s in chainset}
            def tfin(arr,t,pathids=pathids,pathstates=pathstates,o=o,states=states):
                to=int(txt(t,'toStateId'))
                src=[s for s,sid in states if txt(objs[s],'transitions')==arr]
                fromp=bool(src and src[0] in pathstates)
                return to in pathids and not fromp
            def tfout(arr,t,pathids=pathids,pathstates=pathstates,o=o,states=states):
                to=int(txt(t,'toStateId'))
                src=[s for s,sid in states if txt(objs[s],'transitions')==arr]
                fromp=bool(src and src[0] in pathstates)
                return fromp and to not in pathids
            arrs=[txt(o,'wildcardTransitions')]+[txt(objs[s],'transitions') for s,_ in states]
            for a in arrs:
                if a and a.startswith('#'):
                    scan(G,[a],RES,fn+'#in',tfilter=tfin)
                    scan(G,[a],RES,fn+'#out',tfilter=tfout)
        scan(G,list(ctx)+nodes_extra+[c for c in chain if objs[c].get('class')!='hkbBehaviorGraph'],RES,fn+'#ctx')
RES={'vars':{},'events':{},'clips':set(),'brg':set(),'charprops':set()}
for sp in SPEC: run(*sp)
def ser(x):
    if isinstance(x,set): return sorted(map(str,x)) if not all(isinstance(i,tuple) for i in x) else sorted(x)
    raise TypeError
print(json.dumps({k:RES[k] for k in RES},default=ser))
