G=load('1hm_behavior.xml'); objs=G['objs']; ev=G['ev']
for sm in ['1HM_AttackBehavior','1HM_Behavior']:
  o=[x for x in objs.values() if txt(x,'name')==sm][0]
  for s in P(o,'states').text.split():
    so=objs[s]; a=txt(so,'transitions')
    if txt(so,'name') not in ('AttackRight_State','1HM_Ready_State','AttackState') or not a.startswith('#'): continue
    for t in P(objs[a],'transitions').findall('hkobject'):
        e=int(txt(t,'eventId'))
        iv={}
        for k in ('triggerInterval','initiateInterval'):
            x=t.find("hkparam[@name='%s']/hkobject"%k)
            iv[k]=tuple(ev[int(txt(x,p))] if int(txt(x,p))>=0 else None for p in ('enterEventId','exitEventId'))+(txt(x,'enterTime'),txt(x,'exitTime'))
        if 'USE_' in txt(t,'flags') and ev[e] in('attackStart','AttackStartH2HRight','attackStartLeftHand','attackRelease'):
            print(sm,txt(so,'name'),ev[e],'->',txt(t,'toStateId'),iv,txt(t,'flags'))
