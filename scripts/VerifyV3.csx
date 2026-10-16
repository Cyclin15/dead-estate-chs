using System;
using System.Text;
using System.Linq;
using System.Reflection;
using UndertaleModLib.Models;

var log = new StringBuilder();
log.AppendLine("fonts: " + Data.Fonts.Count);
for (int i = 34; i < Data.Fonts.Count; i++)
{
    var f = Data.Fonts[i];
    log.AppendLine($"font[{i}] {f.Name.Content}: glyphs={f.Glyphs.Count} em={f.EmSize} tex={f.Texture.SourceWidth}x{f.Texture.SourceHeight} range={f.RangeStart}-{f.RangeEnd} asc={f.Ascender} lh={f.LineHeight} sao={f.AscenderOffset} scale={f.ScaleX},{f.ScaleY}");
    foreach (var ch in new[] { 'A', '的', 'z' })
    {
        var g = f.Glyphs.FirstOrDefault(x => x.Character == ch);
        log.AppendLine("  " + (int)ch + " '" + ch + "': " + (g == null ? "MISSING" : $"src=({g.SourceX},{g.SourceY},{g.SourceWidth},{g.SourceHeight}) shift={g.Shift} off={g.Offset}"));
    }
}

var code = Data.Code.First(c => c.Name.Content == "gml_Object_game_Create_0");
var list = code.Instructions.ToList();
log.AppendLine("code instrs: " + list.Count);
// find the patch site: pushref of font assets
for (int i = 0; i < list.Count; i++)
{
    string s = list[i].ToString().Trim();
    if (s.StartsWith("pushref.i 10066333") )
        log.AppendLine("[" + i + "] " + s + "   [" + (i+1) + "] " + list[i+1].ToString());
}
// branch integrity on the loaded file
var addr = new uint[list.Count + 1];
var mi = typeof(UndertaleInstruction).GetMethod("CalculateInstructionSize", BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance);
for (int i = 0; i < list.Count; i++)
    addr[i+1] = addr[i] + (uint)mi.Invoke(list[i], null);
var boundaries = new System.Collections.Generic.HashSet<uint>(addr);
int onB = 0, offB = 0;
for (int i = 0; i < list.Count; i++)
{
    string s = list[i].ToString().Trim();
    if (!(s.StartsWith("b ") || s.StartsWith("bt ") || s.StartsWith("bf "))) continue;
    uint tgt = addr[i] + (uint)list[i].JumpOffset;
    if (boundaries.Contains(tgt)) onB++; else { offB++; log.AppendLine("OFFBOUNDARY i=" + i + " off=" + list[i].JumpOffset + " tgt=" + tgt); }
}
log.AppendLine("branches: on-boundary=" + onB + " off=" + offB);
// decompile check via disasm around the pops
int p = -1;
for (int i = 0; i < list.Count; i++) if (list[i].ToString().Trim() == "pop.v.v global.fntAnyaFancy") { p = i; break; }
for (int i = p - 2; i <= p + 5; i++) log.AppendLine("  " + list[i].ToString());
// child entries: Offset must land exactly on an instruction boundary of the parent
foreach (var child in code.ChildEntries)
{
    bool onBoundary = (child.Offset % 4 == 0) && Array.IndexOf(addr, child.Offset / 4) > 0;
    log.AppendLine($"child {child.Name.Content}: Offset={child.Offset} len={child.Length} boundary={(onBoundary ? "OK" : "BROKEN")}");
}
// sprite fonts must be untouched (55/87 frames, charmaps original)
var spr1 = Data.Sprites.ByName("sprAnyaFancyFont");
var spr2 = Data.Sprites.ByName("sprAnyaTypewriterFont");
log.AppendLine($"sprAnyaFancyFont frames={spr1.Textures.Count} sprAnyaTypewriterFont frames={spr2.Textures.Count}");
log.AppendLine("charmap7999 len=" + Data.Strings[7999].Content.Length + " charmap8001 len=" + Data.Strings[8001].Content.Length);
Console.WriteLine(log.ToString());
