using System;
using System.Text;
using System.Linq;
var log = new StringBuilder();
var code = Data.Code.ByName("gml_Object_game_Create_0");
var instrs = code.Instructions;
log.AppendLine("code.Length (bytes) = " + code.Length + " instrs = " + instrs.Count);
var branches = new StringBuilder();
int maxTarget = 0;
for (int i = 0; i < instrs.Count; i++)
{
    var s = instrs[i].ToString().Trim();
    if (s.StartsWith("b ") || s.StartsWith("bf ") || s.StartsWith("bt ") || s.StartsWith("bnot "))
    {
        branches.AppendLine($"[{i}] {s}");
        var m = System.Text.RegularExpressions.Regex.Match(s, @"(\d+)$");
        if (m.Success) maxTarget = Math.Max(maxTarget, int.Parse(m.Groups[1].Value));
    }
}
log.AppendLine("branch count: " + branches.ToString().Count(c => c == '\n'));
log.AppendLine("max branch target: " + maxTarget);
log.Append(branches);
File.WriteAllText(@"D:\Steam\steamapps\common\Dead Estate\_loc_work\dump\create0_branches.txt", log.ToString());
Console.WriteLine(log.ToString(0, Math.Min(2500, log.Length)));
