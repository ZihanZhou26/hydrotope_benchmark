Get["analyze_sig.m"];
parts = FileNames["n6_part_*.m"];
raw = Join @@ (Get /@ parts);
(* also include original n6_data.m points *)
If[FileExistsQ["n6_data.m"],
  raw = Join[raw, Table[{e[[5]], e[[6]]}, {e, Get["n6_data.m"]}]]];
raw = DeleteDuplicates[raw];
Print["total n6 points: ", Length[raw]];
analyzeBySig[6, raw];
