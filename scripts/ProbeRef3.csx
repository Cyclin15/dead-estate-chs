using System;
using System.Text;
using System.Linq;
using System.Collections.Generic;
var log = new StringBuilder();
var sprIdx = new Dictionary<string, int>();
log.AppendLine("sprAnyaFancyFont idx=" + Data.Sprites.IndexOf(Data.Sprites.ByName("sprAnyaFancyFont")));
log.AppendLine("sprAnyaTypewriterFont idx=" + Data.Sprites.IndexOf(Data.Sprites.ByName("sprAnyaTypewriterFont")));
log.AppendLine("sprDigitalDisplayFont idx=" + Data.Sprites.IndexOf(Data.Sprites.ByName("sprDigitalDisplayFont")));
log.AppendLine("oGameLoader obj idx=" + Data.GameObjects.IndexOf(Data.GameObjects.ByName("oGameLoader")));
log.AppendLine("bgmAnyaTitle sound idx=" + Data.Sounds.IndexOf(Data.Sounds.ByName("bgmAnyaTitle")));
log.AppendLine("rmAnyaTitle room idx=" + Data.Rooms.IndexOf(Data.Rooms.ByName("rmAnyaTitle")));
log.AppendLine("counts: sprites=" + Data.Sprites.Count + " objs=" + Data.GameObjects.Count + " sounds=" + Data.Sounds.Count + " rooms=" + Data.Rooms.Count + " fonts=" + Data.Fonts.Count + " scripts=" + Data.Scripts.Count + " code=" + Data.Code.Count);
// collect pushref raw values with printed names
var seen = new SortedDictionary<uint, string>();
int n = 0;
foreach (var c in Data.Code)
{
    foreach (var ins in c.Instructions)
    {
        var s = ins.ToString();
        if (s.StartsWith("pushref.i ") && n < 400000)
        {
            n++;
            var rest = s.Substring(10).Trim();
            if (!uint.TryParse(rest, out uint v)) continue; // named ones skip
            if (!seen.ContainsKey(v)) seen[v] = c.Name.Content;
        }
    }
}
log.AppendLine("pushref numeric values: " + seen.Count + " distinct");
foreach (var kv in seen.Take(12)) log.AppendLine($"  {kv.Key} (0x{kv.Key:X}) hi=0x{kv.Key >> 24:X} lo={kv.Key & 0xFFFFFF} in {kv.Value}");
// distinct high bytes
var his = new Dictionary<uint, int>();
foreach (var kv in seen) { uint h = kv.Key >> 24; his[h] = his.GetValueOrDefault(h) + 1; }
foreach (var kv in his) log.AppendLine($"high 0x{kv.Key:X}: {kv.Value}");
Console.WriteLine(log.ToString());
