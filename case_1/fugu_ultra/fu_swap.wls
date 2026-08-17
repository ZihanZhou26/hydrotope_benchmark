Get["fu_defs.m"];
sig={-1,-1,1,1,1};
ws={2,-9/2,5/2,3,-3}; ks=sig*ws^2;
amp1=BGAmplitude[ks,ws,1]/I;
ws2={-9/2,2,5/2,3,-3}; ks2=sig*ws2^2;
amp2=BGAmplitude[ks2,ws2,1]/I;
Print["A(2,-9/2,..)=",amp1," A(-9/2,2,..)=",amp2," equal? ",amp1===amp2];
