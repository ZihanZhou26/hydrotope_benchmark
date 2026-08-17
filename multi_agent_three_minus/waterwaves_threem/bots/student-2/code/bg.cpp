// bg.cpp — exact-rational (and fast double) Berends-Giele oracle for 1D
// water-wave amplitudes. Faithful transcription of OnShellBG.m
// (EKernel/FKernel/Vertex/Propagator/SetPartitions/BGCurrent/BGAmplitude/
// MakeKinematics). The engine is templated on the real scalar type, so the
// exact (GMP mpq_class) and fast (long double) paths run the SAME algorithm.
// It is a pure amplitude evaluator — it contains no closed-form/answer.
//
// Build: g++ -O2 -std=c++17 -o bg bg.cpp -lgmpxx -lgmp
// Use:
//   ./bg -n 5 -w 2,3,5 -s -1,-1,-1,1,1 [-g 1]      # on-shell, exact rational
//   ./bg --amp -K <n momenta> -W <n omegas> [-g 1] # raw BGAmplitude, exact
//   ./bg --double -n 8 -w 1,2,3,4,5,6 -s -1,-1,-1,1,1,1,1,1   # fast double mode
// Frequencies/momenta are real; the imaginary unit enters only via (-i/2) in
// Vertex and (-i) in Propagator, so amplitudes are (a+bi) with a,b in the field.
#include <bits/stdc++.h>
#include <gmpxx.h>
using namespace std;

// --- abs for each scalar (ADL/overload) ---
static inline mpq_class absR(const mpq_class& x){ return abs(x); }
static inline long double absR(long double x){ return fabsl(x); }

// zero-denominator signal (so a wall/channel hit in --batch does not SIGFPE-abort
// the whole batch; we catch it and emit ERR for that point only).
struct ZeroDenom {};
static inline void chkz(const mpq_class& d){ if(d==0) throw ZeroDenom{}; }
static inline void chkz(long double d){ if(d==0) throw ZeroDenom{}; }

// --- scalar parse ("5/2", "-3", "0.1") ---
template<class R> R parse1(const string& t);
template<> mpq_class parse1<mpq_class>(const string& t){ mpq_class q(t); q.canonicalize(); return q; }
template<> long double parse1<long double>(const string& t){
  size_t p=t.find('/');
  if(p==string::npos) return strtold(t.c_str(), nullptr);
  return strtold(t.substr(0,p).c_str(), nullptr)/strtold(t.substr(p+1).c_str(), nullptr);
}
template<class R> vector<R> parseList(const string& s){
  vector<R> v; if(s.empty()) return v; stringstream ss(s); string t;
  while(getline(ss,t,',')) if(!t.empty()) v.push_back(parse1<R>(t));
  return v;
}

// --- memo-key serialization of a scalar ---
static inline string sval(const mpq_class& x){ return x.get_str(); }
static inline string sval(long double x){ char b[48]; snprintf(b,sizeof b,"%.20Lg",x); return b; }

// --- set partitions of S into exactly k blocks (index-only; scalar-independent) ---
static vector<vector<vector<int>>> SetPartitions(const vector<int>& S, int k){
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
      for(auto& sp:SetPartitions(rem,k-1)){ vector<vector<int>> b{fp}; for(auto& x:sp) b.push_back(x); out.push_back(b); }
  }
  return out;
}

template<class R>
struct Engine {
  struct Cx { R re, im; };
  static Cx cadd(const Cx&a,const Cx&b){ return {a.re+b.re, a.im+b.im}; }
  static Cx cmul(const Cx&a,const Cx&b){ return {a.re*b.re-a.im*b.im, a.re*b.im+a.im*b.re}; }

  vector<R> K, W; R G{1};                     // 1-indexed: K[1..N], W[1..N]
  unordered_map<string,R> Em, Fm;
  unordered_map<unsigned long long,Cx> BGm;

  R fact(int k){ R r(1); for(int i=2;i<=k;i++) r=r*R(i); return r; }
  R powi(const R&b,int e){ R r(1); for(int i=0;i<e;i++) r=r*b; return r; }
  string keyOf(int n,const vector<R>&ps){ string s=to_string(n); for(auto&p:ps){ s.push_back('|'); s+=sval(p);} return s; }

  R EKernel(int n,const vector<R>&ps){
    if(n==3) return (R(-1)/R(2))*(absR(ps[0])*absR(ps[1]) + ps[0]*ps[1]);
    string key=keyOf(n,ps); auto it=Em.find(key); if(it!=Em.end()) return it->second;
    R p1=ps[0], p2=ps[1]; vector<R> rest(ps.begin()+2, ps.end());
    R qp2=absR(p2), rs(0); for(auto&r:rest) rs=rs+r;
    R res = powi(qp2,n-3)*EKernel(3,{p1,p2,rs})/fact(n-2);
    for(int m=1;m<=n-3;m++){
      R part(0); for(int j=0;j<m;j++) part=part+rest[j];
      vector<R> nl{p1, p2+part}; for(size_t j=m;j<rest.size();j++) nl.push_back(rest[j]);
      res = res - powi(qp2,m)/fact(m)*EKernel(n-m,nl);
    }
    Em[key]=res; return res;
  }
  R FKernel(int n,const vector<R>&ps){
    if(n==3) return R(-1) - ps[0]*ps[1]/(absR(ps[0])*absR(ps[1]));
    string key=keyOf(n,ps); auto it=Fm.find(key); if(it!=Fm.end()) return it->second;
    R p1=ps[0], p2=ps[1]; vector<R> rest(ps.begin()+2, ps.end());
    R qp1=absR(p1), qp2=absR(p2);
    chkz(qp1); chkz(qp2);
    R res = R(2)*EKernel(n,ps)/qp1;
    for(int m=1;m<=n-3;m++){
      R part(0); for(int j=0;j<m;j++) part=part+rest[j];
      R sigM=p2+part;
      vector<R> el{-sigM, p2}; for(int j=0;j<m;j++) el.push_back(rest[j]);
      vector<R> fl{p1, sigM};  for(size_t j=m;j<rest.size();j++) fl.push_back(rest[j]);
      res = res - R(2)*EKernel(m+2,el)*FKernel(n-m,fl);
    }
    res = res/qp2; Fm[key]=res; return res;
  }
  Cx Vertex(int n,const vector<R>&moms,const vector<R>&om){
    vector<int> p(n); iota(p.begin(),p.end(),0); R acc(0); vector<R> pm(n);
    do { for(int i=0;i<n;i++) pm[i]=moms[p[i]]; acc = acc + om[p[0]]*om[p[1]]*FKernel(n,pm); }
    while(next_permutation(p.begin(),p.end()));
    return Cx{R(0), -acc/R(2)};               // (-i/2)*acc
  }
  Cx Propagator(const R&wS,const R&kS){ chkz(absR(kS)); R D = wS*wS/absR(kS) - G; chkz(D); return Cx{R(0), R(-1)/D}; }

  Cx BGCurrent(const vector<int>&S){
    if(S.size()==1) return Cx{R(1),R(0)};
    unsigned long long mask=0; for(int i:S) mask|=(1ULL<<i);
    auto it=BGm.find(mask); if(it!=BGm.end()) return it->second;
    R wS(0),kS(0); for(int i:S){ wS=wS+W[i]; kS=kS+K[i]; }
    Cx result{R(0),R(0)};
    for(int m=2;m<=(int)S.size();m++)
      for(auto& part:SetPartitions(S,m)){
        vector<R> vM{-kS}, vO{-wS};
        for(auto& blk:part){ R km(0),om(0); for(int i:blk){ km=km+K[i]; om=om+W[i]; } vM.push_back(km); vO.push_back(om); }
        Cx v=Vertex(m+1,vM,vO), prod{R(1),R(0)};
        for(auto& blk:part) prod=cmul(prod,BGCurrent(blk));
        result=cadd(result,cmul(v,prod));
      }
    result=cmul(result,Propagator(wS,kS)); BGm[mask]=result; return result;
  }
  Cx BGAmplitude(int N){
    BGm.clear(); Em.clear(); Fm.clear();
    vector<int> rest; for(int i=2;i<=N;i++) rest.push_back(i);
    Cx result{R(0),R(0)};
    for(int m=2;m<=N-1;m++)
      for(auto& part:SetPartitions(rest,m)){
        vector<R> vM{K[1]}, vO{W[1]};
        for(auto& blk:part){ R km(0),om(0); for(int i:blk){ km=km+K[i]; om=om+W[i]; } vM.push_back(km); vO.push_back(om); }
        Cx v=Vertex(m+1,vM,vO), prod{R(1),R(0)};
        for(auto& blk:part) prod=cmul(prod,BGCurrent(blk));
        result=cadd(result,cmul(v,prod));
      }
    return result;
  }
};

template<class R>
int runMode(bool rawAmp,int N,const string&ws,const string&ss,const string&ks,const string&Ws,const string&gs){
  Engine<R> E; E.G = parse1<R>(gs);
  if(rawAmp){
    auto kk=parseList<R>(ks), wwv=parseList<R>(Ws);
    if(kk.empty() || kk.size()!=wwv.size()){ cerr<<"--amp needs -K and -W of equal length n\n"; return 1; }
    N=(int)kk.size(); E.K.assign(N+1,R(0)); E.W.assign(N+1,R(0));
    for(int i=1;i<=N;i++){ E.K[i]=kk[i-1]; E.W[i]=wwv[i-1]; }
  } else {
    auto freeW=parseList<R>(ws), sig=parseList<R>(ss);
    if((int)freeW.size()!=N-2 || (int)sig.size()!=N){ cerr<<"usage: -n N -w <n-2 free freqs> -s <n signs> [-g 1] | --amp -K <n moms> -W <n omegas>\n"; return 1; }
    if(!(sig[0]+sig[N-1]==R(0))){ cerr<<"need sigma_1 + sigma_n = 0\n"; return 1; }
    R sumFree(0); for(auto&x:freeW) sumFree=sumFree+x;
    R sumSig(0); for(int i=0;i<N-2;i++) sumSig = sumSig + sig[i+1]*freeW[i]*freeW[i];
    R wn = -(sig[0]*sumFree*sumFree + sumSig)/(R(2)*sig[0]*sumFree);
    R w1 = -(sumFree+wn);
    E.W.assign(N+1,R(0)); E.K.assign(N+1,R(0));
    E.W[1]=w1; for(int i=0;i<N-2;i++) E.W[i+2]=freeW[i]; E.W[N]=wn;
    for(int i=1;i<=N;i++) E.K[i]=sig[i-1]*E.W[i]*E.W[i]/E.G;
  }
  auto A=E.BGAmplitude(N);
  cout<<"n = "<<N<<"\n";
  if constexpr(is_same_v<R,mpq_class>){
    A.re.canonicalize(); A.im.canonicalize();
    cout<<"omega = {"; for(int i=1;i<=N;i++) cout<<E.W[i].get_str()<<(i<N?", ":"}\n");
    if(A.re==0) cout<<"A_"<<N<<" = i * ("<<A.im.get_str()<<")\n";
    else        cout<<"A_"<<N<<" = ("<<A.re.get_str()<<") + i * ("<<A.im.get_str()<<")\n";
    cout<<"A_"<<N<<" (numeric) = "<<mpf_class(A.re,256).get_d()<<" + "<<mpf_class(A.im,256).get_d()<<" i\n";
  } else {
    cout<<setprecision(15);
    cout<<"omega = {"; for(int i=1;i<=N;i++) cout<<(double)E.W[i]<<(i<N?", ":"}\n");
    cout<<"A_"<<N<<" (double) = "<<(double)A.re<<" + "<<(double)A.im<<" i\n";
  }
  return 0;
}

// --batch: read lines "n|freeCSV|signCSV" from stdin; emit "re;im" (exact) or ERR.
template<class R>
int runBatch(const string& gs){
  R G = parse1<R>(gs);
  string line;
  while(getline(cin,line)){
    if(line.empty()){ cout<<"\n"; continue; }
    // split on '|'
    size_t a=line.find('|'), b=line.rfind('|');
    if(a==string::npos||b==a){ cout<<"ERR\n"; continue; }
    int N=atoi(line.substr(0,a).c_str());
    auto freeW=parseList<R>(line.substr(a+1,b-a-1));
    auto sig=parseList<R>(line.substr(b+1));
    if((int)freeW.size()!=N-2||(int)sig.size()!=N){ cout<<"ERR\n"; continue; }
    try{
      Engine<R> E; E.G=G;
      R sumFree(0); for(auto&x:freeW) sumFree=sumFree+x;
      chkz(sumFree);
      R sumSig(0); for(int i=0;i<N-2;i++) sumSig=sumSig+sig[i+1]*freeW[i]*freeW[i];
      chkz(R(2)*sig[0]*sumFree);
      R wn=-(sig[0]*sumFree*sumFree+sumSig)/(R(2)*sig[0]*sumFree);
      R w1=-(sumFree+wn);
      E.W.assign(N+1,R(0)); E.K.assign(N+1,R(0));
      E.W[1]=w1; for(int i=0;i<N-2;i++) E.W[i+2]=freeW[i]; E.W[N]=wn;
      for(int i=1;i<=N;i++) E.K[i]=sig[i-1]*E.W[i]*E.W[i]/E.G;
      auto A=E.BGAmplitude(N);
      if constexpr(is_same_v<R,mpq_class>){ A.re.canonicalize(); A.im.canonicalize();
        cout<<A.re.get_str()<<";"<<A.im.get_str()<<"\n"; }
      else cout<<setprecision(18)<<(double)A.re<<";"<<(double)A.im<<"\n";
    }catch(ZeroDenom&){ cout<<"ERR\n"; }
    catch(...){ cout<<"ERR\n"; }
  }
  return 0;
}

int main(int argc,char**argv){
  string ws, ss, ks, Ws, gs="1"; bool rawAmp=false, useDouble=false, batch=false; int N=0;
  for(int i=1;i<argc;i++){ string a=argv[i];
    if(a=="--amp") rawAmp=true;
    else if(a=="--batch") batch=true;
    else if(a=="--double") useDouble=true;
    else if(a=="-n") N=atoi(argv[++i]);
    else if(a=="-w") ws=argv[++i];
    else if(a=="-s") ss=argv[++i];
    else if(a=="-K") ks=argv[++i];
    else if(a=="-W") Ws=argv[++i];
    else if(a=="-g") gs=argv[++i];
  }
  if(batch) return useDouble ? runBatch<long double>(gs) : runBatch<mpq_class>(gs);
  return useDouble ? runMode<long double>(rawAmp,N,ws,ss,ks,Ws,gs)
                   : runMode<mpq_class>(rawAmp,N,ws,ss,ks,Ws,gs);
}
