// Inspect each font's texture page geometry so we can composite rather than replace.
using System;
using System.IO;
using System.Text;
using UndertaleModLib;
using UndertaleModLib.Models;

string outPath = @"D:\Steam\steamapps\common\Dead Estate\_loc_work\dump\font_textures.txt";
var sb = new StringBuilder();

foreach (var f in Data.Fonts)
{
    if (f == null) continue;
    var t = f.Texture;
    string info = "none";
    if (t != null)
    {
        var tex = t.TexturePage;
        string pageSize = tex != null && tex.TextureData != null && tex.TextureData.Image != null
            ? $"{tex.TextureData.Image.Width}x{tex.TextureData.Image.Height}" : "?";
        info = $"item(src={t.SourceX},{t.SourceY} {t.SourceWidth}x{t.SourceHeight} tgt={t.TargetWidth}x{t.TargetHeight} bounds={t.BoundingWidth}x{t.BoundingHeight}) page={pageSize}";
    }
    sb.AppendLine($"{f.Name.Content}\ttexture={info}\tglyphs={f.Glyphs.Count}\trange={f.RangeStart}..{f.RangeEnd}");

    // max glyph extents
    int maxX = 0, maxY = 0, maxW = 0, maxH = 0, maxShift = 0;
    foreach (var g in f.Glyphs)
    {
        if (g.SourceX + g.SourceWidth > maxX) maxX = g.SourceX + g.SourceWidth;
        if (g.SourceY + g.SourceHeight > maxY) maxY = g.SourceY + g.SourceHeight;
        if (g.SourceWidth > maxW) maxW = g.SourceWidth;
        if (g.SourceHeight > maxH) maxH = g.SourceHeight;
        if (g.Shift > maxShift) maxShift = g.Shift;
    }
    sb.AppendLine($"    used extent: {maxX}x{maxY}  maxGlyph={maxW}x{maxH}  maxShift={maxShift}");
}

// how many distinct texture pages do the fonts share?
var seen = new System.Collections.Generic.Dictionary<int, int>();
foreach (var f in Data.Fonts)
{
    if (f?.Texture?.TexturePage == null) continue;
    int id = f.Texture.TexturePage.TextureData != null ? f.Texture.TexturePage.TextureData.GetHashCode() : 0;
    seen.TryGetValue(id, out int c);
    seen[id] = c + 1;
}
sb.AppendLine();
sb.AppendLine($"distinct font texture pages: {seen.Count}");

File.WriteAllText(outPath, sb.ToString());
Console.WriteLine(sb.ToString());
