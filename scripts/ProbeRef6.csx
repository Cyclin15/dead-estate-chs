using System;
using System.Text;
using System.Linq;
using System.Collections.Generic;
var log = new StringBuilder();
var code = Data.Code.ByName("gml_Object_oAnyaTitleScreen_Create_0");
var instrs = code.Instructions;
for (int i = 0; i < instrs.Count; i++)
{
    var s = instrs[i].ToString();
    if (s.StartsWith("pushref.i ") && uint.TryParse(s.Substring(10).Trim(), out uint v) && (v >> 24) == 3)
    {
        for (int j = Math.Max(0, i - 3); j <= Math.Min(instrs.Count - 1, i + 3); j++)
            log.AppendLine($"TITLE[{j}]: {instrs[j]}");
        log.AppendLine("---");
    }
}
// collect hi=6,8,9 samples with context across code
int found = 0;
foreach (var c in Data.Code)
{
    var ins2 = c.Instructions;
    for (int i = 0; i < ins2.Count && found < 10; i++)
    {
        var s = ins2[i].ToString();
        if (s.StartsWith("pushref.i ") && uint.TryParse(s.Substring(10).Trim(), out uint v))
        {
            uint hi = v >> 24;
            if (hi == 6 || hi == 8 || hi == 9)
            {
                for (int j = Math.Max(0, i - 2); j <= Math.Min(ins2.Count - 1, i + 2); j++)
                    log.AppendLine($"HI{hi} {c.Name.Content}[{j}]: {ins2[j]}");
                log.AppendLine("---");
                found++;
            }
        }
    }
}
Console.WriteLine(log.ToString());
