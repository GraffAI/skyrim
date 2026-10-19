import json,sys,os,re
want=json.loads(sys.stdin.readline())
sf=os.path.expanduser('~/skyrim-data-extracted/raw/meshes/animationdatasinglefile.txt')
L=[l.rstrip('\r') for l in open(sf,encoding='latin-1').read().split('\n')]
n=int(L[0]); names=L[1:1+n]; i=1+n; res={}
for p in range(n):
    c=int(L[i]); blk=L[i+1:i+1+c]; i+=1+c; k=int(blk[1])
    if blk[2+k].strip()=='1': m=int(L[i]); i+=1+m
    if names[p]!='DefaultMale.txt': continue
    print('project paths:',blk[2:2+k][:3], file=sys.stderr)
    cur=[];bl=[]
    for l in blk[2+k+1:]:
        if l.strip()=='':
            if cur: bl.append(cur)
            cur=[]
        else: cur.append(l)
    if cur: bl.append(cur)
    for b in bl:
        if len(b)<6 or re.fullmatch(r'-?\d+',b[0].strip()): continue
        nt=int(b[5]); res.setdefault(b[0],[]).append([t.rsplit(':',1)[0] for t in b[6:6+nt]])
out={}
for comp,clips in want.items():
    out[comp]={c:res.get(c) for c in clips}
print(json.dumps(out))
