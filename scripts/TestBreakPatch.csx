// Test: round-trip compile of gml_GlobalScript_scrStrings (root entry containing
// breakString as child) — pass 1 with ORIGINAL decompiled source, pass 2 with the
// fixed source. Verifies via decompile + disassembly diff.
using System;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;

string work = @"D:\Steam\steamapps\common\Dead Estate\_loc_work";
var root = Data.Code.First(c => c.Name.Content == "gml_GlobalScript_scrStrings");
GlobalDecompileContext gctx = new(Data);
var settings = Data.ToolInfo.DecompilerSettings;
Regex setownerRegex = new Regex(@"pushi?\.[ei] \d+(\n|\r\n)setowner\.e", RegexOptions.Compiled);
string Dis(UndertaleCode c) => setownerRegex.Replace(c.Disassemble(Data.Variables, Data.CodeLocals?.For(c)), "setowner.e");
string Deco(UndertaleCode c) => new Underanalyzer.Decompiler.DecompileContext(gctx, c, settings).DecompileToString();

string origDump = File.ReadAllText(Path.Combine(work, "dump", "CodeEntries", "gml_GlobalScript_scrStrings.gml"), Encoding.UTF8);
string origDis = Dis(root);
Console.WriteLine($"before: children {root.ChildEntries.Count}, {root.Length} bytes, {origDis.Count(c => c == '\n')} asm lines");

// --- pass 1: compile ORIGINAL source unchanged (round-trip sanity)
var group = new CompileGroup(Data, gctx) { MainThreadAction = MainThreadAction };
group.PersistLinkingLookups = true;
group.QueueCodeReplace(root, origDump);
var r1 = group.Compile();
Console.WriteLine($"pass1 Successful={r1.Successful} errors={string.Join("; ", r1.Errors?.Select(e => e.ToString()) ?? Enumerable.Empty<string>())}");
string rtGml = Deco(root);
File.WriteAllText(Path.Combine(work, "dump", "scrStrings_roundtrip.gml"), rtGml, new UTF8Encoding(false));
string rtDis = Dis(root);
Console.WriteLine($"pass1: children {root.ChildEntries.Count}, {root.Length} bytes; asm identical={rtDis == origDis}; gml identical={rtGml == origDump}");
if (rtDis != origDis)
{
    var a = origDis.Split('\n'); var b = rtDis.Split('\n');
    int diffs = 0;
    for (int i = 0; i < Math.Max(a.Length, b.Length) && diffs < 12; i++)
    {
        string x = i < a.Length ? a[i].TrimEnd('\r') : "<EOF>"; string y = i < b.Length ? b[i].TrimEnd('\r') : "<EOF>";
        if (x != y) { Console.WriteLine($"  ASM L{i+1}: {x} | {y}"); diffs++; }
    }
}

// --- pass 2: compile the FIXED source
string fixedGml = File.ReadAllText(Path.Combine(work, "dump", "scrStrings_fixed.gml"), Encoding.UTF8);
group.QueueCodeReplace(root, fixedGml);
var r2 = group.Compile();
Console.WriteLine($"pass2 Successful={r2.Successful} errors={string.Join("; ", r2.Errors?.Select(e => e.ToString()) ?? Enumerable.Empty<string>())}");
string nowGml = Deco(root);
File.WriteAllText(Path.Combine(work, "dump", "scrStrings_patched.gml"), nowGml, new UTF8Encoding(false));
Console.WriteLine($"pass2: children {root.ChildEntries.Count}, {root.Length} bytes; fix present={nowGml.Contains("string_pos(\" \", string_copy(arg0, 1, q))")}");
string nowDis = Dis(root);
File.WriteAllText(Path.Combine(work, "dump", "scrStrings_patched.asm"), nowDis, new UTF8Encoding(false));
Console.WriteLine("done");
