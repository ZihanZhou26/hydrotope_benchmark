Get["bg_defs.m"];
sig={-1,-1,1,1,1};
Do[Block[{fw,ks,ws,amp},
  fw=c;
  {ks,ws}=MakeKinematics[5,fw,sig,1];
  amp=BGAmplitude[ks,ws,1];
  Print["free=",fw," ws=",ws," A=",Simplify[amp]," A/I=",Simplify[amp/I]];
  ],{c,{{2,5/2,3},{2,5/2,3/2},{2,5/2,1},{2,3,4},{3,4,5}}}]
