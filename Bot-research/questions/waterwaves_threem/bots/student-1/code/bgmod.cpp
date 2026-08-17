// bgmod.cpp -- MODULAR (F_p) Berends-Giele oracle for n=7 fits (student-1, round 8).
// Shared bg.cpp left pristine; private copy adding a finite-field scalar `Fp`.
//
// WHY: exact GMP at n=7 ~1 s/eval (bignum blowup). Over F_p there is no blowup, ~5x faster, and the
// fit machinery is modular anyway (mod p + rational reconstruction). EXACT-in-F_p (no float verdicts).
//
// SIGN: the BG recursion's abs() applies ONLY to momenta = integer-linear combos of the external
// k_i (built via +/-, never products), so each Fp carries its exact integer coefficient vector c[]
// over K[1..N]; abs() reads the sign EXACTLY from sum_i c[i]*Kq[i] (Kq exact mpq). Validated == ./bg
// (reduced mod p) at n=5,6,7 over many chamber points.  Build: g++ -O2 -std=c++17 -o bgmod bgmod.cpp -lgmpxx -lgmp
// Use: echo "7|2,3,5,7,11/2|-1,-1,-1,1,1,1,1" | ./bgmod --batchmod   # prints im(A_n) mod P per line
#include <bits/stdc++.h>
#include <gmpxx.h>
using namespace std;
typedef unsigned long long u64;
typedef __uint128_t u128;

static const u64 MOD = 2305843009213693951ULL; // 2^61 - 1
static inline u64 madd(u64 a,u64 b){ a+=b; if(a>=MOD) a-=MOD; return a; }
static inline u64 msub(u64 a,u64 b){ return a>=b? a-b : a+MOD-b; }
static inline u64 mmul(u64 a,u64 b){ return (u64)((u128)a*b % MOD); }
static inline u64 mpw(u64 a,u64 e){ u64 r=1; a%=MOD; while(e){ if(e&1) r=mmul(r,a); a=mmul(a,a); e>>=1;} return r; }
static inline u64 minvf(u64 a){ return mpw(a%MOD, MOD-2); }

static const int MAXN = 9;
static mpq_class Kq[MAXN+1];   // exact external momenta K[1..N], set per evaluation (for signs)
static int NLEGS = 0;

struct Fp {
  u64 v;
  signed char c[MAXN+1];   // integer coeffs over K[1..N] (valid iff mom)
  bool mom;                // is this a tracked momentum (linear combo of K[i])?
  Fp(): v(0), mom(false) { for(int i=0;i<=MAXN;i++) c[i]=0; }
  Fp(long long x){ long long m=x%(long long)MOD; v=(u64)(m<0?m+(long long)MOD:m); mom=false; for(int i=0;i<=MAXN;i++) c[i]=0; }
};
static inline Fp mk(u64 v){ Fp r; r.v=v; r.mom=false; return r; }
static inline Fp zmom(){ Fp r; r.v=0; r.mom=true; for(int i=0;i<=MAXN;i++) r.c[i]=0; return r; } // additive identity for momentum sums
static inline Fp operator+(const Fp&x,const Fp&y){ Fp r; r.v=madd(x.v,y.v);
  if(x.mom&&y.mom){ r.mom=true; for(int i=0;i<=MAXN;i++) r.c[i]=x.c[i]+y.c[i]; } else r.mom=false; return r; }
static inline Fp operator-(const Fp&x,const Fp&y){ Fp r; r.v=msub(x.v,y.v);
  if(x.mom&&y.mom){ r.mom=true; for(int i=0;i<=MAXN;i++) r.c[i]=x.c[i]-y.c[i]; } else r.mom=false; return r; }
static inline Fp operator*(const Fp&x,const Fp&y){ return mk(mmul(x.v,y.v)); }       // product is never a momentum
static inline Fp operator/(const Fp&x,const Fp&y){ return mk(mmul(x.v,minvf(y.v))); }
static inline Fp operator-(const Fp&x){ Fp r; r.v=(x.v?MOD-x.v:0); r.mom=x.mom; if(x.mom) for(int i=0;i<=MAXN;i++) r.c[i]=-x.c[i]; return r; }

// exact sign of a tracked momentum
static inline int momsign(const Fp& x){
  mpq_class s(0);
  for(int i=1;i<=NLEGS;i++) if(x.c[i]) s += mpq_class(x.c[i])*Kq[i];
  return sgn(s);
}
static long long g_nonmom=0, g_ambig=0;
static inline Fp absR(const Fp& x){
  // x must be a tracked momentum here; sign from exact integer combo.
  if(!x.mom){ g_nonmom++; }
  int s = x.mom ? momsign(x) : 0;
  if(x.mom && s==0 && x.v!=0){ g_ambig++; }
  return (s < 0) ? mk(x.v?MOD-x.v:0) : mk(x.v);
}
struct ZeroDivM{};
static inline void chk(const Fp& d){ if(d.v==0) throw ZeroDivM{}; }

template<class R> R parse1(const string& t);
template<> Fp parse1<Fp>(const string& t){
  size_t p=t.find('/');
  if(p==string::npos){ return Fp((long long)strtoll(t.c_str(),nullptr,10)); }
  long long num=strtoll(t.substr(0,p).c_str(),nullptr,10);
  long long den=strtoll(t.substr(p+1).c_str(),nullptr,10);
  return Fp(num)/Fp(den);
}
template<> mpq_class parse1<mpq_class>(const string& t){ mpq_class q(t); q.canonicalize(); return q; }
template<class R> vector<R> parseList(const string& s){
  vector<R> v; if(s.empty()) return v; stringstream ss(s); string t;
  while(getline(ss,t,',')) if(!t.empty()) v.push_back(parse1<R>(t));
  return v;
}

static vector<vector<vector<int>>> SetPartitions(const vector<int>& S,int k){
  if(k==1) return {{S}};
  if(k>(int)S.size()) return {};
  int mn=*min_element(S.begin(),S.end());
  vector<int> X; for(int x:S) if(x!=mn) X.push_back(x);
  int L=(int)S.size(), xs=(int)X.size();
  vector<vector<vector<int>>> out;
  for(int mask=0; mask<(1<<xs); ++mask){
    if(__builtin_popcount(mask) > L-k) continue;
    set<int> fps{mn}; vector<int> fp{mn};
    for(int b=0;b<xs;b++) if(mask&(1<<b)){ fp.push_back(X[b]); fps.insert(X[b]); }
    sort(fp.begin(),fp.end());
    vector<int> rem; for(int v:S) if(!fps.count(v)) rem.push_back(v);
    if((int)rem.size()>=k-1)
      for(auto& sp:SetPartitions(rem,k-1)){ vector<vector<int>> b{fp}; for(auto&x:sp) b.push_back(x); out.push_back(b);}
  }
  return out;
}

struct Engine {
  struct Cx { Fp re, im; };
  static Cx cadd(const Cx&a,const Cx&b){ return {a.re+b.re, a.im+b.im}; }
  static Cx cmul(const Cx&a,const Cx&b){ return {a.re*b.re-a.im*b.im, a.re*b.im+a.im*b.re}; }
  vector<Fp> K,W; Fp G{(long long)1};
  unordered_map<string,Fp> Em,Fm;
  unordered_map<u64,Cx> BGm;
  Fp fact(int k){ Fp r((long long)1); for(int i=2;i<=k;i++) r=r*Fp((long long)i); return r; }
  Fp powi(const Fp&b,int e){ Fp r((long long)1); for(int i=0;i<e;i++) r=r*b; return r; }
  // COLLISION-FREE key: the exact residues (distinct momenta -> distinct residue tuples within an eval).
  string keyOf(int n,const vector<Fp>&ps){ string s=to_string(n); for(auto&p:ps){ s.push_back('|'); s+=to_string(p.v);} return s; }
  Fp EKernel(int n,const vector<Fp>&ps){
    if(n==3) return (Fp((long long)-1)/Fp((long long)2))*(absR(ps[0])*absR(ps[1]) + ps[0]*ps[1]);
    string key=keyOf(n,ps); auto it=Em.find(key); if(it!=Em.end()) return it->second;
    Fp p1=ps[0],p2=ps[1]; vector<Fp> rest(ps.begin()+2,ps.end());
    Fp qp2=absR(p2), rs=zmom(); for(auto&r:rest) rs=rs+r;
    Fp res = powi(qp2,n-3)*EKernel(3,{p1,p2,rs})/fact(n-2);
    for(int m=1;m<=n-3;m++){
      Fp part=zmom(); for(int j=0;j<m;j++) part=part+rest[j];
      vector<Fp> nl{p1,p2+part}; for(size_t j=m;j<rest.size();j++) nl.push_back(rest[j]);
      res = res - powi(qp2,m)/fact(m)*EKernel(n-m,nl);
    }
    Em[key]=res; return res;
  }
  Fp FKernel(int n,const vector<Fp>&ps){
    if(n==3){ chk(absR(ps[0])*absR(ps[1])); return Fp((long long)-1) - ps[0]*ps[1]/(absR(ps[0])*absR(ps[1])); }
    string key=keyOf(n,ps); auto it=Fm.find(key); if(it!=Fm.end()) return it->second;
    Fp p1=ps[0],p2=ps[1]; vector<Fp> rest(ps.begin()+2,ps.end());
    Fp qp1=absR(p1),qp2=absR(p2); chk(qp1); chk(qp2);
    Fp res = Fp((long long)2)*EKernel(n,ps)/qp1;
    for(int m=1;m<=n-3;m++){
      Fp part=zmom(); for(int j=0;j<m;j++) part=part+rest[j];
      Fp sigM=p2+part;
      vector<Fp> el{-sigM,p2}; for(int j=0;j<m;j++) el.push_back(rest[j]);
      vector<Fp> fl{p1,sigM};  for(size_t j=m;j<rest.size();j++) fl.push_back(rest[j]);
      res = res - Fp((long long)2)*EKernel(m+2,el)*FKernel(n-m,fl);
    }
    res = res/qp2; Fm[key]=res; return res;
  }
  Cx Vertex(int n,const vector<Fp>&moms,const vector<Fp>&om){
    vector<int> p(n); iota(p.begin(),p.end(),0); Fp acc((long long)0); vector<Fp> pm(n);
    do { for(int i=0;i<n;i++) pm[i]=moms[p[i]]; acc=acc+om[p[0]]*om[p[1]]*FKernel(n,pm); }
    while(next_permutation(p.begin(),p.end()));
    return Cx{Fp((long long)0), -acc/Fp((long long)2)};
  }
  Cx Propagator(const Fp&wS,const Fp&kS){ chk(absR(kS)); Fp D=wS*wS/absR(kS)-G; chk(D); return Cx{Fp((long long)0), Fp((long long)-1)/D}; }
  Cx BGCurrent(const vector<int>&S){
    if(S.size()==1) return Cx{Fp((long long)1),Fp((long long)0)};
    u64 mask=0; for(int i:S) mask|=(1ULL<<i);
    auto it=BGm.find(mask); if(it!=BGm.end()) return it->second;
    Fp wS((long long)0),kS=zmom(); for(int i:S){ wS=wS+W[i]; kS=kS+K[i]; }
    Cx result{Fp((long long)0),Fp((long long)0)};
    for(int m=2;m<=(int)S.size();m++)
      for(auto& part:SetPartitions(S,m)){
        vector<Fp> vM{-kS}, vO{-wS};
        for(auto& blk:part){ Fp km=zmom(),om((long long)0); for(int i:blk){ km=km+K[i]; om=om+W[i]; } vM.push_back(km); vO.push_back(om);}
        Cx v=Vertex(m+1,vM,vO), prod{Fp((long long)1),Fp((long long)0)};
        for(auto& blk:part) prod=cmul(prod,BGCurrent(blk));
        result=cadd(result,cmul(v,prod));
      }
    result=cmul(result,Propagator(wS,kS)); BGm[mask]=result; return result;
  }
  Cx BGAmplitude(int N){
    BGm.clear(); Em.clear(); Fm.clear();
    vector<int> rest; for(int i=2;i<=N;i++) rest.push_back(i);
    Cx result{Fp((long long)0),Fp((long long)0)};
    for(int m=2;m<=N-1;m++)
      for(auto& part:SetPartitions(rest,m)){
        vector<Fp> vM{K[1]}, vO{W[1]};
        for(auto& blk:part){ Fp km=zmom(),om((long long)0); for(int i:blk){ km=km+K[i]; om=om+W[i]; } vM.push_back(km); vO.push_back(om);}
        Cx v=Vertex(m+1,vM,vO), prod{Fp((long long)1),Fp((long long)0)};
        for(auto& blk:part) prod=cmul(prod,BGCurrent(blk));
        result=cadd(result,cmul(v,prod));
      }
    return result;
  }
};

static int runBatchMod(){
  string line;
  while(getline(cin,line)){
    if(line.empty()){ cout<<"\n"; continue; }
    stringstream ss(line); string Ntok,wtok,stok;
    getline(ss,Ntok,'|'); getline(ss,wtok,'|'); getline(ss,stok,'|');
    int N=atoi(Ntok.c_str());
    auto freeW=parseList<Fp>(wtok), sig=parseList<Fp>(stok);
    auto freeWq=parseList<mpq_class>(wtok), sigq=parseList<mpq_class>(stok);
    if((int)freeW.size()!=N-2 || (int)sig.size()!=N){ cout<<"ERR\n"; continue; }
    // exact solve (mpq) for W, then K -> Kq (for exact signs)
    mpq_class sumFq(0); for(auto&x:freeWq) sumFq+=x;
    if(sumFq==0){ cout<<"ERR\n"; continue; }
    mpq_class sumSq(0); for(int i=0;i<N-2;i++) sumSq += sigq[i+1]*freeWq[i]*freeWq[i];
    mpq_class wnq = -(sigq[0]*sumFq*sumFq + sumSq)/(mpq_class(2)*sigq[0]*sumFq);
    mpq_class w1q = -(sumFq+wnq);
    vector<mpq_class> Wq(N+1, mpq_class(0));
    Wq[1]=w1q; for(int i=0;i<N-2;i++) Wq[i+2]=freeWq[i]; Wq[N]=wnq;
    NLEGS=N; for(int i=1;i<=N;i++){ Kq[i]=sigq[i-1]*Wq[i]*Wq[i]; Kq[i].canonicalize(); }
    // residue solve (Fp)
    Fp sumFree((long long)0); for(auto&x:freeW) sumFree=sumFree+x;
    Fp sumSig((long long)0); for(int i=0;i<N-2;i++) sumSig=sumSig+sig[i+1]*freeW[i]*freeW[i];
    try{
      Engine E; E.G=Fp((long long)1);
      Fp wn = -(sig[0]*sumFree*sumFree + sumSig)/(Fp((long long)2)*sig[0]*sumFree);
      Fp w1 = -(sumFree+wn);
      E.W.assign(N+1,Fp((long long)0)); E.K.assign(N+1,Fp((long long)0));
      E.W[1]=w1; for(int i=0;i<N-2;i++) E.W[i+2]=freeW[i]; E.W[N]=wn;
      for(int i=1;i<=N;i++){
        Fp ki = sig[i-1]*E.W[i]*E.W[i]/E.G;     // residue of K[i]
        ki.mom=true; for(int j=0;j<=MAXN;j++) ki.c[j]=0; ki.c[i]=1;  // tag as the i-th external momentum
        E.K[i]=ki;
      }
      auto A=E.BGAmplitude(N);
      cout<<A.im.v<<"\n";
      if(getenv("BGDBG")) fprintf(stderr,"nonmom=%lld ambig=%lld\n",g_nonmom,g_ambig);
    }catch(ZeroDivM&){ cout<<"ERR\n"; }
  }
  return 0;
}

int main(int argc,char**argv){
  bool batchmod=false;
  for(int i=1;i<argc;i++){ string a=argv[i]; if(a=="--batchmod") batchmod=true; }
  if(batchmod) return runBatchMod();
  cerr<<"usage: ./bgmod --batchmod  (stdin: N|wcsv|scsv per line; prints im mod "<<MOD<<")\n";
  return 1;
}
