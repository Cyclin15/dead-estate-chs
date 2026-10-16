using System;
using System.Text;
using System.Linq;
var log = new StringBuilder();
var code = Data.Code.ByName("gml_Object_game_Create_0");
var instrs = code.Instructions;
// find instance_create_depth call and audio calls to see how objects/sounds are pushed
for (int i = 0; i < instrs.Count; i++)
{
    var s = instrs[i].ToString();
    if (s.Contains("instance_create_depth") || s.Contains("audio_play_sound"))
    {
        for (int j = Math.Max(0, i - 6); j <= i; j++)
            log.AppendLine($"{j}: {instrs[j]}");
        log.AppendLine("---");
        if (log.Length > 3000) break;
    }
}
// also: hi=0x2 samples in other code
int found = 0;
foreach (var c in Data.Code)
{
    if (c.Name.Content == "gml_Object_game_Create_0") continue;
    var ins2 = c.Instructions;
    for (int i = 0; i < ins2.Count && found < 6; i++)
    {
        var s = ins2[i].ToString();
        if (s.StartsWith("pushref.i "))
        {
            if (uint.TryParse(s.Substring(10).Trim(), out uint v) && (v >> 24) == 2)
            {
                for (int j = Math.Min(ins2.Count - 1, i + 2); j >= Math.Max(0, i - 1); j--)
                    log.AppendLine($"{c.Name.Content}[{j}]: {ins2[j]}");
                log.AppendLine("---");
                found++;
            }
        }
    }
}
Console.WriteLine(log.ToString());
