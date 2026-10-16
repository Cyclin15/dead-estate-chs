using System;
using System.Text;
using System.Linq;
var log = new StringBuilder();
int found = 0;
foreach (var c in Data.Code)
{
    var ins2 = c.Instructions;
    for (int i = 0; i < ins2.Count && found < 14; i++)
    {
        var s = ins2[i].ToString();
        if (s.StartsWith("pushref.i ") && uint.TryParse(s.Substring(10).Trim(), out uint v))
        {
            uint hi = v >> 24;
            if (hi == 6 || hi == 9)
            {
                for (int j = Math.Max(0, i - 3); j <= Math.Min(ins2.Count - 1, i + 3); j++)
                    log.AppendLine($"HI{hi} {c.Name.Content}[{j}]: {ins2[j]}");
                log.AppendLine("---");
                found++;
            }
        }
    }
}
Console.WriteLine(log.ToString());
