// Inspect the font_add_sprite_ext call sites in gml_Object_game_Create_0:
// exact instructions with serialized sizes, child entry offsets, branch spans,
// and example push.i/popz.v instructions for potential padding.
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using UndertaleModLib;
using UndertaleModLib.Models;

var code = Data.Code.ByName("gml_Object_game_Create_0");
if (code is null) { Console.WriteLine("game_Create_0 not found"); return; }
Console.WriteLine($"game_Create_0: {code.Instructions.Count} instructions");

// reflection helper for serialized instruction size
var asm = typeof(UndertaleInstruction).Assembly;
MethodInfo calc = null;
foreach (var t in asm.GetTypes())
{
    foreach (var m in t.GetMethods(BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Static | BindingFlags.Instance | BindingFlags.DeclaredOnly))
    {
        if (m.Name.Contains("InstructionSize") || m.Name.Contains("GetSize"))
        {
            Console.WriteLine("candidate: " + t.FullName + "." + m.Name + (m.IsStatic ? " (static)" : " (instance)"));
            if (calc is null) calc = m;
        }
    }
}
if (calc is null)
{
    // fall back: opcode-based size table via instance method on the instruction
    var mi = typeof(UndertaleInstruction).GetMethods(BindingFlags.NonPublic | BindingFlags.Instance)
        .FirstOrDefault(m => m.Name.Contains("Size"));
    Console.WriteLine("fallback instance method: " + (mi?.Name ?? "none"));
    if (mi is null) return;
    calc = mi;
}
Console.WriteLine("using " + calc.DeclaringType.FullName + "." + calc.Name);

long SizeOfM(UndertaleInstruction instr)
{
    object res = calc.IsStatic
        ? calc.Invoke(null, new object[] { instr })
        : calc.Invoke(instr, Array.Empty<object>());
    return Convert.ToInt64(res);
}
long s0 = SizeOfM(code.Instructions[0]);
Console.WriteLine("instruction[0] size = " + s0 + " (" + code.Instructions[0] + ")");

// find call sites of font_add_sprite_ext
var sites = new List<int>();
for (int i = 0; i < code.Instructions.Count; i++)
{
    var instr = code.Instructions[i];
    if (instr.Kind == UndertaleInstruction.Opcode.Call &&
        instr.ValueFunction?.Name?.Content == "font_add_sprite_ext")
        sites.Add(i);
}
Console.WriteLine("font_add_sprite_ext call sites at instr indices: " + string.Join(", ", sites));

// cumulative byte offsets (original layout)
var cum = new long[code.Instructions.Count + 1];
for (int i = 0; i < code.Instructions.Count; i++) cum[i + 1] = cum[i] + SizeOfM(code.Instructions[i]);
Console.WriteLine($"total bytecode bytes: {cum[code.Instructions.Count]}");

foreach (int site in sites)
{
    Console.WriteLine($"\n=== site instr {site} (byte {cum[site]}) ===");
    for (int i = site - 12; i <= site + 3 && i < code.Instructions.Count; i++)
    {
        var instr = code.Instructions[i];
        Console.WriteLine($"  [{i}] byte {cum[i]:5} size {SizeOfM(instr):2}  {instr}");
    }
}

// children
Console.WriteLine("\n=== children of game_Create_0 ===");
foreach (var child in code.ChildEntries)
    Console.WriteLine($"  {child.Name?.Content}  Offset={child.Offset}  Length={child.Length}");

// other entries that share the same bytecode address? find code entries whose
// serialized record would point into game_Create_0 (none besides children, but check names)
int count = Data.Code.Count(c => c.Name?.Content?.Contains("game_Create_0") == true);
Console.WriteLine("code entries with 'game_Create_0' in name: " + count);

// branch span audit: any branch whose (source,target) span crosses the edit points?
// edit region: we plan to replace instructions [site-8 .. site-1] + call at 'site'
foreach (int site in sites.Take(2))
{
    long e1 = cum[site - 8];          // first replaced instruction byte
    long e2 = cum[site + 1];          // byte after the call (end of replaced span)
    int crossings = 0;
    for (int i = 0; i < code.Instructions.Count; i++)
    {
        var instr = code.Instructions[i];
        var k = instr.Kind;
        bool isBranch = k == UndertaleInstruction.Opcode.B || k == UndertaleInstruction.Opcode.Bt
                      || k == UndertaleInstruction.Opcode.Bf || k == UndertaleInstruction.Opcode.PushEnv
                      || k == UndertaleInstruction.Opcode.PopEnv;
        if (!isBranch) continue;
        long src = cum[i];
        // JumpOffset semantics: relative in 4-byte words (instruction "Index" units)
        long dstW = (src / 4) + instr.JumpOffset;
        long dst = dstW * 4;
        bool crosses = (src < e1 && dst >= e1 && dst < e2 + 400) || (dst < e1 && src >= e1);
        // conservative: check if span [min,max] intersects [e1, e2)
        long lo = Math.Min(src, dst), hi = Math.Max(src, dst);
        if (lo < e2 && hi >= e1)
        {
            crossings++;
            if (crossings <= 5) Console.WriteLine($"  BRANCH CROSSES edit: [{i}] byte {src} {instr} -> dst byte {dst} (edit [{e1},{e2}))");
        }
    }
    Console.WriteLine($"site {site}: branches crossing edit span [{e1},{e2}): {crossings}");
}

// example push.i (int16) and popz.v instructions for cloning
Console.WriteLine("\n=== example push.i-int16 / popz.v ===");
int shown = 0;
foreach (var c in Data.Code.Take(3000))
{
    if (c.ParentEntry is not null) continue;
    for (int i = 0; i + 1 < c.Instructions.Count && shown < 4; i++)
    {
        var a = c.Instructions[i]; var b = c.Instructions[i + 1];
        string sa = a.ToString(); string sb = b.ToString();
        if (sa.StartsWith("push.i") && SizeOfM(a) == 4 && sb.StartsWith("popz") && SizeOfM(b) == 4)
        {
            Console.WriteLine($"  {c.Name?.Content}: [{i}] {a} | [{i+1}] {b}");
            Console.WriteLine($"    a.Kind={a.Kind} a.Type1={a.Type1} a.ValueShort={a.ValueShort}  b.Kind={b.Kind} b.Type1={b.Type1}");
            shown++;
        }
    }
}
if (shown == 0) Console.WriteLine("  (no push.i/popz pair found in first 3000 entries)");
