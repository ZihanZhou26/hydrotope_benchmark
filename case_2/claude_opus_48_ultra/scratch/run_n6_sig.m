Get["analyze_sig.m"];
d = Get["n6_data.m"];
raw = Table[{e[[5]], e[[6]]}, {e, d}];
analyzeBySig[6, raw];
