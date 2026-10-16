using System;
using System.Text;
using System.Linq;
using System.Collections.Generic;
var log = new StringBuilder();
var spr = Data.Sprites.ByName("sprAnyaFancyFont");
log.AppendLine("sprAnyaFancyFont sprite index: " + Data.Sprites.IndexOf(spr));
var spr2 = Data.Sprites.ByName("sprAnyaTypewriterFont");
log.AppendLine("sprAnyaTypewriterFont index: " + Data.Sprites.IndexOf(spr2));
var spr3 = Data.Sprites.ByName("sprDigitalDisplayFont");
log.AppendLine("sprDigitalDisplayFont index: " + Data.Sprites.IndexOf(spr3));
log.AppendLine("font count: " + Data.Fonts.Count + " sprite count: " + Data.Sprites.Count);
// scan all code for pushref.i values, tally high bytes
var tally = new Dictionary<uint, int>();
var samples = new Dictionary<uint, string>();
foreach (var c in Data.Code)
{
    foreach (var ins in c.Instructions)
    {
        var s = ins.ToString();
        if (s.Contains("pushref.i "))
        {
            uint v = uint.Parse(s.Substring(s.IndexOf("pushref.i ") + 10).Trim());
            uint hi = v >> 24;
            tally[hi] = tally.GetValueOrDefault(hi) + 1;
            if (!samples.ContainsKey(hi)) samples[hi] = c.Name.Content + ": " + s.Trim();
        }
    }
}
foreach (var kv in tally.OrderBy(x => x.Key))
    log.AppendLine($"pushref high byte 0x{kv.Key:X}: count={kv.Value}  e.g. {samples[kv.Key]}");
Console.WriteLine(log.ToString());
