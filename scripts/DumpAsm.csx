using System;
using System.Text;
using System.Linq;
var log = new StringBuilder();
var code = Data.Code.ByName("gml_Object_game_Create_0");
var instrs = code.Instructions;
log.AppendLine("total instructions: " + instrs.Count);
// find the call to font_add_sprite_ext
for (int i = 0; i < instrs.Count; i++)
{
    var s = instrs[i].ToString();
    if (s.Contains("font_add_sprite_ext"))
    {
        for (int j = Math.Max(0, i - 8); j <= Math.Min(instrs.Count - 1, i + 3); j++)
            log.AppendLine($"{j}: {instrs[j]}");
        log.AppendLine("---");
    }
}
Console.WriteLine(log.ToString());
File.WriteAllText(@"D:\Steam\steamapps\common\Dead Estate\_loc_work\dump\fontcall_asm.txt", log.ToString());
