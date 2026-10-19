import sys
fn=sys.argv[1]; targets=sys.argv[2].split(',')
G=load(fn); objs=G['objs']
root=[o for o in objs.values() if o.get('class')=='hkbBehaviorGraph'][0].get('name')
from collections import deque
par={root:None}; q=deque([root])
while q:
    n=q.popleft()
    for r in sorted(refs(objs[n])):
        if r in objs and r not in par: par[r]=n; q.append(r)
for t in targets:
    for o in objs.values():
        if txt(o,'name')==t:
            n=o.get('name'); chain=[]
            while n: chain.append('%s:%s'%(objs[n].get('class').replace('hkbStateMachine','SM').replace('hkb',''),txt(objs[n],'name'))); n=par.get(n)
            print(t,'<=',' <- '.join(chain[1:]))
