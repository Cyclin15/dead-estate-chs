// TESTS
// (A) Which string-table entries are actually used as literals in game code?
//     For every code entry, walk the instructions and record the string indices referenced.
// (B) Does a GML re-import round-trip cleanly for this game?
using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using UndertaleModLib;
using UndertaleModLib.Models;

string outPath = @"D:\Steam\steamapps\common\Dead Estate\_loc_work\dump\used_strings.txt";
var sb = new StringBuilder();

var used = new HashSet<int>();
int codeEntries = 0, totalRefs = 0;

int IdxOf(UndertaleString s)
{
    if (s == null) return -1;
    for (int i = 0; i < Data.Strings.Count; i++)
        if (ReferenceEquals(Data.Strings[i], s)) return i;
    return -1;
}

foreach (var code in Data.Code)
{
    codeEntries++;
    if (code?.Instructions == null) continue;
    foreach (var ins in code.Instructions)
    {
        // GameMaker pushes string references as instruction arguments.
        if (ins.Value is UndertaleString us)
        {
            int k = IdxOf(us);
            if (k >= 0) { used.Add(k); totalRefs++; }
        }
        if (ins.Value is UndertaleResourceById<UndertaleString, UndertaleString> r)
        {
            try { int k = IdxOf(r.Resource); if (k >= 0) { used.Add(k); totalRefs++; } } catch { }
        }
        foreach (var arg in ins.ValueArguments)
        {
            if (arg is UndertaleString s2)
            {
                int k = IdxOf(s2);
                if (k >= 0) { used.Add(k); totalRefs++; }
            }
            else if (arg is UndertaleResourceById<UndertaleString, UndertaleString> r2)
            {
                try { int k = IdxOf(r2.Resource); if (k >= 0) { used.Add(k); totalRefs++; } } catch { }
            }
        }
    }
}

sb.AppendLine($"codeEntries={codeEntries} totalStringRefs={totalRefs} distinctStringsUsed={used.Count} totalStrings={Data.Strings.Count}");

var sorted = new List<int>(used);
sorted.Sort();
var w = new StreamWriter(outPath);
w.WriteLine(string.Join(",", sorted));
w.Close();
sb.AppendLine($"wrote index list to {outPath}");

// Intersect with the prose candidates to build the authoritative translate list.
string unitsPath = @"D:\Steam\steamapps\common\Dead Estate\_loc_work\dump\units.json";
if (File.Exists(unitsPath))
{
    string raw = File.ReadAllText(unitsPath);
    // lightweight scan for "idx":N  (avoids a JSON dependency)
    var rx = new System.Text.RegularExpressions.Regex("\"idx\":(\\d+)");
    var unitIdx = new List<int>();
    foreach (System.Text.RegularExpressions.Match m in rx.Matches(raw))
        unitIdx.Add(int.Parse(m.Groups[1].Value));

    var keep = new List<int>();
    var drop = new List<int>();
    foreach (int k in unitIdx) { if (used.Contains(k)) keep.Add(k); else drop.Add(k); }
    sb.AppendLine($"prose candidates={unitIdx.Count}  used-in-code={keep.Count}  unused(dropped)={drop.Count}");
    var w2 = new StreamWriter(@"D:\Steam\steamapps\common\Dead Estate\_loc_work\dump\translate_indices.txt");
    w2.WriteLine(string.Join(",", keep));
    w2.Close();
    var w3 = new StreamWriter(@"D:\Steam\steamapps\common\Dead Estate\_loc_work\dump\dropped_indices.txt");
    w3.WriteLine(string.Join(",", drop));
    w3.Close();
    sb.AppendLine("wrote translate_indices.txt and dropped_indices.txt");
}

Console.WriteLine(sb.ToString());
