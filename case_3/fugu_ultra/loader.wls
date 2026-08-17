(* shared loader: imports ONLY ../OnShellBG.m, strips its demo tests *)
code = Import[FileNameJoin[{DirectoryName[$InputFileName], "..", "OnShellBG.m"}], "Text"];
defs = StringSplit[code, "(* ================================================================ *)\n(*  VI. TESTS"][[1]];
ToExpression[defs];
