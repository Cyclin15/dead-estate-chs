using System;
using System.Text;
using System.Linq;
var log = new StringBuilder();
var t = typeof(UndertaleModLib.Models.UndertaleCode);
foreach (var m in t.GetMethods())
{
    if (m.Name == "Replace" || m.Name == "Append" || m.Name == "GetInstruction")
    {
        var ps = string.Join(", ", m.GetParameters().Select(p => p.ParameterType.Name + " " + p.Name));
        log.AppendLine($"{m.Name}({ps})");
    }
}
// branch scan: any jump whose target index crosses 6001..6018?
var code = Data.Code.ByName("gml_Object_game_Create_0");
var instrs = code.Instructions;
var kinds = new HashSet<string> { "b", "bf", "bt", "bnot" };
for (int i = 0; i < instrs.Count; i++)
{
    var s = instrs[i].ToString();
    var parts = s.Split(' ');
    string kind = parts[0];
    if (kind.StartsWith("b") || kind.Contains("env"))
    {
        // parse jump target if numeric
        var m = System.Text.RegularExpressions.Regex.Match(s, @"[b].*?(-?\d+)(\s|$)");
        if (int.TryParse(m.Groups[1].Value, out int off))
        {
            // jump targets are byte offsets, not indices — log raw
            if (i < 6021 && i > 5980) log.AppendLine($"near-edit [{i}]: {s.Trim()}");
        }
    }
}
// simpler: log all branch-like instructions in 5950..6060 and the LAST 40 instrs
for (int i = 5950; i < 6060 && i < instrs.Count; i++)
{
    var s = instrs[i].ToString().Trim();
    if (s.StartsWith("b") || s.StartsWith("pop") && s.Contains("env") || s.StartsWith("pushenv") || s.StartsWith("popenv"))
        log.AppendLine($"BRANCH [{i}]: {s}");
}
log.AppendLine("last instr index: " + (instrs.Count - 1));
Console.WriteLine(log.ToString());
