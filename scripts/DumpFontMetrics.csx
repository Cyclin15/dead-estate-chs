using System;
using System.Text;
using System.Linq;
var log = new StringBuilder();
foreach (var f in Data.Fonts)
{
    log.AppendLine($"{f.Name.Content}: em={f.EmSize} asc={f.Ascender} lineH={f.LineHeight} ascOff={f.AscenderOffset} scale=({f.ScaleX},{f.ScaleY}) glyphs={f.Glyphs.Count}");
    // sample CJK glyph metrics (a few common chars) + widest/tallest CJK
    var cjk = f.Glyphs.Where(g => g.Character >= 0x4E00 && g.Character <= 0x9FFF).ToList();
    if (cjk.Count > 0)
    {
        var maxH = cjk.Max(g => g.SourceHeight);
        var maxW = cjk.Max(g => g.SourceWidth);
        var shifts = cjk.Select(g => g.Shift).Distinct().ToList();
        var sample = cjk.FirstOrDefault(g => g.Character == 0x6E38); // 游
        log.AppendLine($"  CJK n={cjk.Count} maxGlyphH={maxH} maxGlyphW={maxW} shifts=[{string.Join(",", shifts.Take(8))}] sample游=({sample?.SourceWidth}x{sample?.SourceHeight},shift={sample?.Shift},off={sample?.Offset})");
    }
    var lat = f.Glyphs.FirstOrDefault(g => g.Character == 72); // 'H'
    if (lat != null) log.AppendLine($"  'H': {lat.SourceWidth}x{lat.SourceHeight} shift={lat.Shift} off={lat.Offset}");
}
Console.WriteLine(log.ToString());
