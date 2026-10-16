// Verify the built localized data.win: strings, CJK glyph coverage, and atlas wiring.
using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using UndertaleModLib;
using UndertaleModLib.Models;

string work = @"D:\Steam\steamapps\common\Dead Estate\_loc_work";
string outFile = Path.Combine(work, "out", "data.win");
var sb = new StringBuilder();

sb.AppendLine($"file: {outFile} ({new FileInfo(outFile).Length} bytes)");
sb.AppendLine($"strings: {Data.Strings.Count}  fonts: {Data.Fonts.Count}  textures: {Data.EmbeddedTextures.Count}");

// --- strings: spot-check that translations landed ---
string[] probes = { "死亡庄园", "安雅", "道具", "武器" };
foreach (string p in probes)
{
    bool found = false;
    foreach (var s in Data.Strings)
        if (s.Content != null && s.Content.Contains(p)) { found = true; break; }
    sb.AppendLine($"  string contains \"{p}\": {found}");
}

// --- fonts: CJK coverage ---
sb.AppendLine();
sb.AppendLine("font CJK coverage:");
int totalCjk = 0;
foreach (var f in Data.Fonts)
{
    if (f == null) continue;
    int cjk = 0;
    foreach (var g in f.Glyphs) if (g.Character > 127) cjk++;
    totalCjk += cjk;
    string tex = (f.Texture != null && f.Texture.TexturePage != null && f.Texture.TexturePage.TextureData != null)
        ? $"{f.Texture.TexturePage.TextureData.Image.Width}x{f.Texture.TexturePage.TextureData.Image.Height}" : "none";
    sb.AppendLine($"  {f.Name.Content,-32} glyphs={f.Glyphs.Count,5} cjk={cjk,5} atlas={tex}");
}
sb.AppendLine($"total CJK glyph mappings: {totalCjk}");

// --- verify a few specific codepoints resolve with sane metrics ---
sb.AppendLine();
sb.AppendLine("sample glyph lookups (fntGameFontNormal):");
var font = Data.Fonts.ByName("fntGameFontNormal");
if (font != null)
{
    foreach (char c in "死亡庄园安雅武器")
    {
        UndertaleFont.Glyph hit = null;
        foreach (var g in font.Glyphs) if (g.Character == c) { hit = g; break; }
        sb.AppendLine(hit != null
            ? $"  '{c}' U+{(int)c:X4} -> src=({hit.SourceX},{hit.SourceY}) {hit.SourceWidth}x{hit.SourceHeight} shift={hit.Shift}"
            : $"  '{c}' U+{(int)c:X4} -> MISSING");
    }
}

File.WriteAllText(Path.Combine(work, "dump", "verify_patch.txt"), sb.ToString());
Console.WriteLine(sb.ToString());
