using System;
using System.Text;
using System.Linq;
var log = new StringBuilder();
int[] probes = { 0xFF01, 0xFF1F, 0xFF0C, 0x3002, 0x3001, 0xFF1A, 0xFF1B, 0x2026, 0x2014, 0x00B7, 0x2666, 0x266A, 0x2022, 0x2192, 0xFF08, 0xFF09, 0x201C, 0x201D, 0x300A, 0x300B };
foreach (var f in Data.Fonts)
{
    var have = f.Glyphs.GroupBy(g => (int)g.Character).ToDictionary(g => g.Key, g => g.First());
    var dup = f.Glyphs.GroupBy(g => (int)g.Character).Where(g => g.Count() > 1).Select(g => g.Key).ToList();
    var missing = new StringBuilder();
    var zero = new StringBuilder();
    foreach (var c in probes)
    {
        if (!have.ContainsKey(c)) { missing.Append(char.ConvertFromUtf32(c) + "(U+" + c.ToString("X4") + ") "); }
        else if (have[c].SourceWidth == 0 || have[c].SourceHeight == 0) { zero.Append(char.ConvertFromUtf32(c) + "(U+" + c.ToString("X4") + ") "); }
    }
    if (missing.Length > 0 || zero.Length > 0 || dup.Count > 0)
        log.AppendLine(f.Name.Content + ": MISSING[" + missing + "] ZERO[" + zero + "] DUP[" + string.Join(",", dup.Select(d => "U+" + d.ToString("X4"))) + "]");
}
log.AppendLine("--- fonts total: " + Data.Fonts.Count);
Console.WriteLine(log.ToString());
