Get["fu_defs.m"];
(* Reduce variables: on-shell, sum w=0 and sum sigma w^2=0. Use free vars u1..u_{n-2} = w_2..w_{n-1}? 
   Actually MakeKinematics solves w1,wn from w2..w_{n-1}. But that's only ONE branch.
   For a GLOBAL rational function we want A as function on the (n-2)-dim on-shell variety.
   Parametrize variety by (w2,...,w_{n-1}) is wrong (misses configs). 
   Better: A is a function of all w_i restricted to the 2 constraints; a global rational
   function in C(w1..wn)/(constraints). We can fit using independent coords:
   choose t_i = w_i for i=1..n-2 as independent? The constraints then fix w_{n-1},w_n.
   But which legs are "minus"? legs 1,2 are minus. Let's use independent coordinates = 
   w_1,w_3,w_4,...,w_{n-1} (n-2 of them) and solve w_2 (minus) and w_n (plus) from constraints? 
   sigma_2=-1, sigma_n=+1, sigma_2+sigma_n=0 OK so linear solvable. *)
(* test: n=5, independent {w1,w3,w4}, solve w2(minus),w5(plus). *)
n=5;sig={-1,-1,1,1,1};
solve[w1_,w3_,w4_]:=Module[{w2,w5,a,b,c},
 (* w2+w5 = -(w1+w3+w4); -w2^2+w5^2 = -(-w1^2+w3^2+w4^2) i.e. sigma2 w2^2+sigma5 w5^2 = -(sig1 w1^2+sig3 w3^2+sig4 w4^2) *)
 (* let S=-(w1+w3+w4)=w2+w5 ; M = -(- w1^2 + w3^2+w4^2) = -w2^2+w5^2 = (w5-w2)(w5+w2)=(w5-w2)S *)
 (* so w5-w2 = M/S. *)
 a=-(w1+w3+w4); b=-(-w1^2+w3^2+w4^2);
 w5=(a+b/a)/2; w2=(a-b/a)/2; {w1,w2,w3,w4,w5}];
ws=solve[-9/2,5/2,3];Print["ws=",ws," sumw=",Total[ws]," mom=",Total[sig*ws^2]];
ks=sig*ws^2; Print["A/I=",BGAmplitude[ks,ws,1]/I];
