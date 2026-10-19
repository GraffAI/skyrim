import json,sys
d=json.load(open(sys.argv[1])); det=set(sys.argv[2].split(',')) if len(sys.argv)>2 else set()
V=d['vars'];E=d['events']
def tag(files):
    t=set()
    for f in files:
        t.add(f.split('#')[1] if '#' in f else 'core')
    return '+'.join(sorted(t))
def fl(files): return ','.join(sorted(set(f.split('#')[0].replace('.xml','') for f in files)))
print('VARS',len(V))
for k in sorted(V,key=str.lower):
    v=V[k]; print(' %-28s %-6s R=%d W=%d %-5s %s | %s'%(k,v['type'].replace('VARIABLE_TYPE_',''),len(v['R']),len(v['W']),tag(v['files']),fl(v['files']),';'.join(sorted(v['W']))[:70]))
    if k in det: print('     R:',sorted(v['R']))
print('EVENTS',len(E))
for k in sorted(E,key=str.lower): v=E[k]; print(' %-34s %-12s L=%s R=%s | %s'%(k,tag(v['files']),len(v['L']),','.join(sorted(x.replace('hkbStateMachine','SM').split('.')[0] for x in v['R'])),fl(v['files'])))
print('BRG',d['brg']); print('CLIPS',len(d['clips'])); print('CHARPROPS',d['charprops'])
