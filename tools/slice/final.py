import json
d=json.load(open('comps.json')); K=json.load(open('cls.json')); C=json.load(open('contract_min.json'))
L=set(C['L']);G=set(C['G']);T=set(C['T'])
def ecls(n):
    l=n in L; r=n in G or n in T or n.split('.')[0] in T
    return 'engine-sent' if l and not r else 'graph-only' if r and not l else 'both' if l and r else 'neither'
def vcls(n):
    wg,rg=C['V'].get(n,[0,0]); return 'engine-input' if wg==0 and rg>0 else 'graph-out-only' if wg>0 and rg==0 else 'graph-written+read' if wg>0 else 'unreferenced'
def tags(files): return {f.split('#')[1] if '#' in f else 'core' for f in files}
def collect(comps, keep_tags=('core','mg','ctx','in','out'), varfilter=None):
    V={};E={}
    for c in comps:
        for n,v in d[c]['vars'].items():
            if varfilter and c in varfilter and n not in varfilter[c]: continue
            t=tags(v['files'])&set(keep_tags)
            if not t: continue
            x=V.setdefault(n,{'type':v['type'].replace('VARIABLE_TYPE_',''),'W':set(),'R':set(),'comp':set()})
            x['W']|=set(v['W']);x['R']|=set(v['R']);x['comp'].add(c)
        for n,v in d[c]['events'].items():
            t=tags(v['files'])&set(keep_tags)
            if not t: continue
            x=E.setdefault(n,{'L':0,'R':set(),'comp':set(),'tags':set()})
            x['L']+=len(v['L']);x['R']|=set(r.split('.')[0].replace('hkbStateMachine','SM') for r in v['R']);x['comp'].add(c);x['tags']|=t
    return V,E
ss={'L_root_modifiers':{'Speed','Direction','iState','SpeedSampled'}}
LV,LE=collect(['L_root_modifiers','L_mt_default','L_sprint','W_1hm_standing','W_1hm_locomotion'],keep_tags=('core','mg','ctx'),varfilter=ss)
JV,JE=collect(['L_jump'],keep_tags=('core','ctx','in'))
AV,AE=collect(['A_attack_right','W_1hm_ready_mods'],keep_tags=('core','mg','ctx','in','out'))
def show(title,V,E):
    print('##',title,'vars',len(V),'events',len(E))
    for n in sorted(V,key=str.lower):
        v=V[n]; print('V %-24s %-7s %-18s graphW=%s | %s'%(n,v['type'],vcls(n),'Y' if v['W'] else '-',','.join(sorted(c.split('_',1)[1] for c in v['comp']))))
    for n in sorted(E,key=str.lower):
        e=E[n]; print('E %-34s %-11s L=%d R=%s tags=%s | %s'%(n,ecls(n),e['L'],','.join(sorted(e['R'])),'+'.join(sorted(e['tags'])),','.join(sorted(c.split('_',1)[1] for c in e['comp']))))
show('LOCO',LV,LE); show('JUMP',JV,JE); show('ATTACK',AV,AE)
allV=set(LV)|set(AV); allE=set(LE)|set(AE)
print('LOCO+ATTACK vars',len(allV),'events',len(allE),' +JUMP vars',len(allV|set(JV)),'events',len(allE|set(JE)))
