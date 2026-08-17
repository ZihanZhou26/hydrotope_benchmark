Get["fit_spline.m"];
parts = FileNames["n6_part_*.m"];
raw = Join @@ (Get /@ parts);
If[FileExistsQ["n6_data.m"], raw = Join[raw, Table[{e[[5]], e[[6]]}, {e, Get["n6_data.m"]}]]];
raw = DeleteDuplicates[raw];
Print["total pts: ", Length[raw]];
fitSpline[6, raw];
