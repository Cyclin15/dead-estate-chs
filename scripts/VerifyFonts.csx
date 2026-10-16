// Verify the font import: check glyph counts, the atlas texture, and that CJK codepoints exist.
using System;
using System.IO;
using System.Text;
using UndertaleModLib;
using UndertaleModLib.Models;

string outPath = @"D:\Steam\steamapps\common\Dead Estate\_loc_work\dump\font_verify.txt";
var sb = new StringBuilder();

foreach (var name in new[] { "fntGameFontNormal", "fntGameFontBigger", "fntGameFontBiggest", "fntSmall" })
{
    var f = Data.Fonts.ByName(name);
    if (f == null) { sb.AppendLine($"{name}: MISSING"); continue; }
    int cjk = 0, latin = 0, over255 = 0;
    foreach (var g in f.Glyphs)
    {
        if (g.Character > 126) cjk++; else latin++;
        if (g.Character > 255) over255++;
    }
    string texInfo = f.Texture != null && f.Texture.TexturePage != null && f.Texture.TexturePage.TextureData != null
        ? $"{f.Texture.TexturePage.TextureData.Image.Width}x{f.Texture.TexturePage.TextureData.Image.Height}" : "none";
    sb.AppendLine($"{name}: total={f.Glyphs.Count} latin={latin} cjk={cjk} over255={over255} RangeStart={f.RangeStart} RangeEnd={f.RangeEnd} atlas={texInfo}");

    // sample a few CJK glyph mappings
    int shown = 0;
    foreach (var g in f.Glyphs)
    {
        if (g.Character > 126 && shown < 4)
        {
            sb.AppendLine($"    U+{g.Character:X4} '{char.ConvertFromUtf32(g.Character)}' src=({g.SourceX},{g.SourceY}) size={g.SourceWidth}x{g.SourceHeight} shift={g.Shift} off={g.Offset}");
            shown++;
        }
    }
}

File.WriteAllText(outPath, sb.ToString());
Console.WriteLine(sb.ToString());
