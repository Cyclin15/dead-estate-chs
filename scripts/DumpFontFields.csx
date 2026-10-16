using System;
using System.Text;
using System.Linq;
var log = new StringBuilder();
foreach (var n in new[] { "fntGameFont", "fntTiny" })
{
    var f = Data.Fonts.ByName(n);
    log.AppendLine($"{n}: em={f.EmSize} asc={f.Ascender} lineHeight={f.LineHeight} ascOff={f.AscenderOffset} range={f.RangeStart}-{f.RangeEnd} charset={f.Charset} aa={f.AntiAliasing} scale=({f.ScaleX},{f.ScaleY}) glyphs={f.Glyphs.Count} tex={f.Texture?.Name?.Content} texWH=({f.Texture?.SourceWidth},{f.Texture?.SourceHeight})");
    foreach (var ch in new ushort[] { 72, 103, 120, 32 })
    {
        var g = f.Glyphs.FirstOrDefault(x => x.Character == ch);
        if (g != null) log.AppendLine($"  '{(char)ch}': src=({g.SourceX},{g.SourceY}) {g.SourceWidth}x{g.SourceHeight} shift={g.Shift} off={g.Offset}");
    }
}
foreach (var sn in new[] { "sprAnyaFancyFont", "sprAnyaTypewriterFont", "sprAnyaReviewFont" })
{
    var s = Data.Sprites.ByName(sn);
    log.AppendLine($"{sn}: W={s.Width} H={s.Height} bboxMode={s.BBoxMode} mrg=({s.MarginLeft},{s.MarginTop},{s.MarginRight},{s.MarginBottom}) origin=({s.OriginX},{s.OriginY}) frames={s.Textures.Count}");
    for (int i = 0; i < Math.Min(6, s.Textures.Count); i++)
    {
        var t = s.Textures[i].Texture;
        log.AppendLine($"  FRM {i}: src=({t.SourceX},{t.SourceY}) {t.SourceWidth}x{t.SourceHeight} tgt=({t.TargetX},{t.TargetY}) bbox={t.BoundingWidth}x{t.BoundingHeight}");
    }
    var tl = s.Textures[s.Textures.Count - 1].Texture;
    log.AppendLine($"  FRM {s.Textures.Count - 1}: src=({tl.SourceX},{tl.SourceY}) {tl.SourceWidth}x{tl.SourceHeight} tgt=({tl.TargetX},{tl.TargetY}) bbox={tl.BoundingWidth}x{tl.BoundingHeight}");
}
Console.WriteLine(log.ToString());
