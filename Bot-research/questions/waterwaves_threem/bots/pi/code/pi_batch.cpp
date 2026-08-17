// pi_batch.cpp -- PI's own batched exact-rational BGAmplitude evaluator for
// round-8 independent verification. The Engine below is a faithful copy of the
// shared bg.cpp engine (EKernel/FKernel/Vertex/Propagator/BGCurrent/BGAmplitude);
// only the I/O is changed: read many raw --amp points from stdin (one per line,
// "W1,...,Wn ; K1,...,Kn") and print the exact A_n imaginary part as a rational
// "p/q" (or "0" if Re!=0 unexpectedly). A guard prints "SIGFPE" for any point
// that divides by zero (wall / channel / pole) so a batch is not aborted.
//
// Build: g++ -O2 -std=c++17 -o pi_batch pi_batch.cpp -lgmpxx -lgmp
#include <bits/stdc++.h>
#include <gmpxx.h>
using namespace std;

static inline mpq_class absR(const mpq_class& x){ return abs(x); }

static vector<mpq_class> parseList(const string& s){
  vector<mpq_class> v; if(s.empty()) return v; stringstream ss(s); string t;
  while(getline(ss,t,',')) if(!t.empty()){ mpq_class q(t); q.canonicalize(); v.push_back(q);} return v;
}
static inline string sval(const mpq_class& x){ return x.get_str(); }

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

struct Cx { mpq_class re, im; };
struct DivZero {};

struct Engine {
  static Cx cadd(const Cx&a,const Cx&b){ return {a.re+b.re, a.im+b.im}; }
  static Cx cmul(const Cx&a,const Cx&b){ return {a.re*b.re-a.im*b.im, a.re*b.im+a.im*b.re}; }
  vector<mpq_class> K, W; mpq_class G{1};
  unordered_map<string,mpq_class> Em, Fm;
  unordered_map<unsigned long long,Cx> BGm;
  mpq_class fact(int k){ mpq_class r(1); for(int i=2;i<=k;i++) r=r*mpq_class(i); return r; }
  mpq_class powi(const mpq_class&b,int e){ mpq_class r(1); for(int i=0;i<e;i++) r=r*b; return r; }
  string keyOf(int n,const vector<mpq_class>&ps){ string s=to_string(n); for(auto&p:ps){ s.push_back('|'); s+=sval(p);} return s; }
  mpq_class EKernel(int n,const vector<mpq_class>&ps){
    if(n==3) return (mpq_class(-1)/mpq_class(2))*(absR(ps[0])*absR(ps[1]) + ps[0]*ps[1]);
    string key=keyOf(n,ps); auto it=Em.find(key); if(it!=Em.end()) return it->second;
    mpq_class p1=ps[0], p2=ps[1]; vector<mpq_class> rest(ps.begin()+2, ps.end());
    mpq_class qp2=absR(p2), rs(0); for(auto&r:rest) rs=rs+r;
    mpq_class res = powi(qp2,n-3)*EKernel(3,{p1,p2,rs})/fact(n-2);
    for(int m=1;m<=n-3;m++){
      mpq_class part(0); for(int j=0;j<m;j++) part=part+rest[j];
      vector<mpq_class> nl{p1, p2+part}; for(size_t j=m;j<rest.size();j++) nl.push_back(rest[j]);
      res = res - powi(qp2,m)/fact(m)*EKernel(n-m,nl);
    }
    Em[key]=res; return res;
  }
  mpq_class FKernel(int n,const vector<mpq_class>&ps){
    if(n==3){ if(absR(ps[0])==0||absR(ps[1])==0) throw DivZero{}; return mpq_class(-1) - ps[0]*ps[1]/(absR(ps[0])*absR(ps[1])); }
    string key=keyOf(n,ps); auto it=Fm.find(key); if(it!=Fm.end()) return it->second;
    mpq_class p1=ps[0], p2=ps[1]; vector<mpq_class> rest(ps.begin()+2, ps.end());
    mpq_class qp1=absR(p1), qp2=absR(p2);
    if(qp1==0||qp2==0) throw DivZero{};
    mpq_class res = mpq_class(2)*EKernel(n,ps)/qp1;
    for(int m=1;m<=n-3;m++){
      mpq_class part(0); for(int j=0;j<m;j++) part=part+rest[j];
      mpq_class sigM=p2+part;
      vector<mpq_class> el{-sigM, p2}; for(int j=0;j<m;j++) el.push_back(rest[j]);
      vector<mpq_class> fl{p1, sigM};  for(size_t j=m;j<rest.size();j++) fl.push_back(rest[j]);
      res = res - mpq_class(2)*EKernel(m+2,el)*FKernel(n-m,fl);
    }
    res = res/qp2; Fm[key]=res; return res;
  }
  Cx Vertex(int n,const vector<mpq_class>&moms,const vector<mpq_class>&om){
    vector<int> p(n); iota(p.begin(),p.end(),0); mpq_class acc(0); vector<mpq_class> pm(n);
    do { for(int i=0;i<n;i++) pm[i]=moms[p[i]]; acc = acc + om[p[0]]*om[p[1]]*FKernel(n,pm); }
    while(next_permutation(p.begin(),p.end()));
    return Cx{mpq_class(0), -acc/mpq_class(2)};
  }
  Cx Propagator(const mpq_class&wS,const mpq_class&kS){ if(absR(kS)==0) throw DivZero{}; mpq_class D = wS*wS/absR(kS) - G; if(D==0) throw DivZero{}; return Cx{mpq_class(0), mpq_class(-1)/D}; }
  Cx BGCurrent(const vector<int>&S){
    if(S.size()==1) return Cx{mpq_class(1),mpq_class(0)};
    unsigned long long mask=0; for(int i:S) mask|=(1ULL<<i);
    auto it=BGm.find(mask); if(it!=BGm.end()) return it->second;
    mpq_class wS(0),kS(0); for(int i:S){ wS=wS+W[i]; kS=kS+K[i]; }
    Cx result{mpq_class(0),mpq_class(0)};
    for(int m=2;m<=(int)S.size();m++)
      for(auto& part:SetPartitions(S,m)){
        vector<mpq_class> vM{-kS}, vO{-wS};
        for(auto& blk:part){ mpq_class km(0),om(0); for(int i:blk){ km=km+K[i]; om=om+W[i]; } vM.push_back(km); vO.push_back(om); }
        Cx v=Vertex(m+1,vM,vO), prod{mpq_class(1),mpq_class(0)};
        for(auto& blk:part) prod=cmul(prod,BGCurrent(blk));
        result=cadd(result,cmul(v,prod));
      }
    result=cmul(result,Propagator(wS,kS)); BGm[mask]=result; return result;
  }
  Cx BGAmplitude(int N){
    BGm.clear(); Em.clear(); Fm.clear();
    vector<int> rest; for(int i=2;i<=N;i++) rest.push_back(i);
    Cx result{mpq_class(0),mpq_class(0)};
    for(int m=2;m<=N-1;m++)
      for(auto& part:SetPartitions(rest,m)){
        vector<mpq_class> vM{K[1]}, vO{W[1]};
        for(auto& blk:part){ mpq_class km(0),om(0); for(int i:blk){ km=km+K[i]; om=om+W[i]; } vM.push_back(km); vO.push_back(om); }
        Cx v=Vertex(m+1,vM,vO), prod{mpq_class(1),mpq_class(0)};
        for(auto& blk:part) prod=cmul(prod,BGCurrent(blk));
        result=cadd(result,cmul(v,prod));
      }
    return result;
  }
};

int main(){
  string line;
  while(getline(cin,line)){
    if(line.empty()) continue;
    size_t bar=line.find('|');
    if(bar==string::npos){ cout<<"ERR\n"; continue; }
    string Ws=line.substr(0,bar), Ks=line.substr(bar+1);
    auto W=parseList(Ws), K=parseList(Ks);
    if(W.size()!=K.size()||W.empty()){ cout<<"ERR\n"; continue; }
    int N=(int)W.size();
    Engine E; E.G=mpq_class(1);
    E.W.assign(N+1,mpq_class(0)); E.K.assign(N+1,mpq_class(0));
    for(int i=1;i<=N;i++){ E.W[i]=W[i-1]; E.K[i]=K[i-1]; }
    try{
      Cx A=E.BGAmplitude(N);
      A.re.canonicalize(); A.im.canonicalize();
      if(A.re!=0){ cout<<"RE("<<A.re.get_str()<<")|"<<A.im.get_str()<<"\n"; }
      else cout<<A.im.get_str()<<"\n";
    }catch(DivZero&){ cout<<"SIGFPE\n"; }
  }
  return 0;
}
