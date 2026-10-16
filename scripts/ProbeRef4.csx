using System;
using System.Text;
using System.Linq;
using System.Collections.Generic;
var log = new StringBuilder();
// named pushrefs: capture name + underlying ValueInt
var named = new Dictionary<string, uint>();
foreach (var c in Data.Code)
{
    foreach (var ins in c.Instructions)
    {
        var s = ins.ToString();
        if (s.StartsWith("pushref.i "))
        {
            var rest = s.Substring(10).Trim();
            if (!uint.TryParse(rest, out uint v))
            {
                if (!named.ContainsKey(rest)) named[rest] = (uint)ins.ValueInt;
            }
        }
    }
}
log.AppendLine("named pushrefs: " + named.Count);
// classify: script? sound? object? sprite?
int shown = 0;
foreach (var kv in named)
{
    string kind = "?";
    if (Data.Scripts.ByName(kv.Key) != null) kind = "script";
    else if (Data.Sounds.ByName(kv.Key) != null) kind = "sound";
    else if (Data.GameObjects.ByName(kv.Key) != null) kind = "object";
    else if (Data.Sprites.ByName(kv.Key) != null) kind = "sprite";
    else if (Data.Rooms.ByName(kv.Key) != null) kind = "room";
    else if (Data.Fonts.ByName(kv.Key) != null) kind = "FONT";
    log.AppendLine($"{kind,-8} {kv.Key} -> 0x{kv.Value:X} (hi=0x{kv.Value >> 24:X} lo={kv.Value & 0xFFFFFF})");
    if (++shown > 40) break;
}
Console.WriteLine(log.ToString());
