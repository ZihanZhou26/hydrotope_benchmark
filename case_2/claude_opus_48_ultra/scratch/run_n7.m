Get["labelseq.m"];
Get["analyze_sig.m"];
parts = FileNames["n7_part_*.m"];
raw = DeleteDuplicates[Join @@ (Get /@ parts)];
Print["n7 total pts: ", Length[raw]];
Print["======== by label sequence ========"];
analyzeData[7, raw];
Print["======== by full signature ========"];
analyzeBySig[7, raw];
