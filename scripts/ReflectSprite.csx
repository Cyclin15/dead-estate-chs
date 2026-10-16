using System;
using System.Text;
using System.Linq;

var log = new StringBuilder();
var spr = Data.Sprites.ByName("sprAnyaTypewriterFont");
log.AppendLine("== UndertaleSprite instance properties ==");
foreach (var p in spr.GetType().GetProperties())
{
    try
    {
        object v = p.GetValue(spr);
        string vs = v == null ? "null" : (v is System.Collections.IEnumerable && !(v is string) ? "(collection)" : v.ToString());
        log.AppendLine($"  {p.Name} = {vs}");
    }
    catch { log.AppendLine($"  {p.Name} = <err>"); }
}
var t = spr.Textures[0];
log.AppendLine("== TextureEntry properties ==");
foreach (var p in t.GetType().GetProperties())
{
    try { log.AppendLine($"  {p.Name} = {p.GetValue(t)}"); } catch { log.AppendLine($"  {p.Name} = <err>"); }
}
log.AppendLine("== TexturePageItem properties ==");
foreach (var p in t.Texture.GetType().GetProperties())
{
    try { log.AppendLine($"  {p.Name} = {p.GetValue(t.Texture)}"); } catch { log.AppendLine($"  {p.Name} = <err>"); }
}
File.WriteAllText(@"D:\Steam\steamapps\common\Dead Estate\_loc_work\dump\sprite_reflect.txt", log.ToString());
Console.WriteLine(log.ToString());
