// Verify the breakString fix inside the built data_v3e.win:
// decompile the root scrStrings, check the fixed line, disassemble around the
// string_pos call, and verify the child entry + string 3054 content.
using System;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;

string work = @"D:\Steam\steamapps\common\Dead Estate\_loc_work";
var root = Data.Code.First(c => c.Name.Content == "gml_GlobalScript_scrStrings");
GlobalDecompileContext gctx = new(Data);
var settings = Data.ToolInfo.DecompilerSettings;
string gml = new Underanalyzer.Decompiler.DecompileContext(gctx, root, settings).DecompileToString();
bool fixedLine = gml.Contains("string_pos(\" \", string_copy(arg0, 1, q))");
Console.WriteLine($"breakString fixed line present: {fixedLine}");
Console.WriteLine($"root: {root.Length} bytes, children {root.ChildEntries.Count}");
var child = root.ChildEntries.FirstOrDefault(c => c.Name.Content == "gml_Script_breakString");
Console.WriteLine($"breakString child entry: {(child == null ? "MISSING" : child.Name.Content + " @" + child.Offset)}");

string dis = root.Disassemble(Data.Variables, Data.CodeLocals?.For(root));
int n = dis.IndexOf("call.i string_pos");
Console.WriteLine("--- asm around first string_pos call ---");
Console.WriteLine(string.Join("\n", dis.Substring(Math.Max(0, n - 220), 300).Split('\n').Select(l => l.TrimEnd())));
Console.WriteLine("string 3054: " + Data.Strings[3054].Content);
Console.WriteLine("string 3638: " + Data.Strings[3638].Content);
