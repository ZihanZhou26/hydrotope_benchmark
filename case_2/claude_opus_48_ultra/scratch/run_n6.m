Get["BGcore.m"];
Get["labelseq.m"];
d = Get["n6_data.m"];   (* entries: {sig, fw, w1, w2, ws, P6} *)
raw = Table[{e[[5]], e[[6]]}, {e, d}];
Print["n6 pts: ", Length[raw]];
res = analyzeData[6, raw];
