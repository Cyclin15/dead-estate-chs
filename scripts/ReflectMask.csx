using System;
using System.Text;
var log = new StringBuilder();
var spr = Data.Sprites.ByName("sprAnyaTypewriterFont");
log.AppendLine($"Textures={spr.Textures.Count} Masks={spr.CollisionMasks.Count}");
var m = spr.CollisionMasks[0];
foreach (var p in m.GetType().GetProperties())
{
    try { log.AppendLine($"  {p.Name} = {p.GetValue(m)}"); } catch { log.AppendLine($"  {p.Name} = <err>"); }
}
foreach (var f in m.GetType().GetFields())
{
    try { log.AppendLine($"  field {f.Name} = {f.GetValue(m)}"); } catch { log.AppendLine($"  field {f.Name} = <err>"); }
}
File.WriteAllText(@"D:\Steam\steamapps\common\Dead Estate\_loc_work\dump\mask_reflect.txt", log.ToString());
Console.WriteLine(log.ToString());
