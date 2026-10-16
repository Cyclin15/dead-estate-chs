// Confirm the two scale variants differ only in the font scale fields, and report the
// actual font/string state of each.
using System;
using System.IO;
using System.Text;
using UndertaleModLib;

string work = @"D:\Steam\steamapps\common\Dead Estate\_loc_work";
var sb = new StringBuilder();

sb.AppendLine($"file: {Data.GeneralInfo?.Name?.Content}  strings={Data.Strings.Count} fonts={Data.Fonts.Count} textures={Data.EmbeddedTextures.Count}");

int nonAscii = 0;
foreach (var s in Data.Strings)
{
    if (s.Content == null) continue;
    foreach (char c in s.Content) if (c > 127) { nonAscii++; break; }
}
sb.AppendLine($"strings with Chinese: {nonAscii}");

sb.AppendLine();
sb.AppendLine("font / scale / glyphs:");
foreach (var f in Data.Fonts)
{
    if (f == null) continue;
    int cjk = 0; int maxW = 0, maxH = 0;
    foreach (var g in f.Glyphs)
    {
        if (g.Character > 127)
        {
            cjk++;
            if (g.SourceWidth > maxW) maxW = g.SourceWidth;
            if (g.SourceHeight > maxH) maxH = g.SourceHeight;
        }
    }
    sb.AppendLine($"  {f.Name.Content,-32} Em={f.EmSize,-3} Scale={f.ScaleX:0.####} cjk={cjk,5} maxGlyph={maxW}x{maxH}");
}

File.WriteAllText(Path.Combine(work, "dump", "verify_variants.txt"), sb.ToString());
Console.WriteLine(sb.ToString());
