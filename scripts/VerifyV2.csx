// Sanity-check the built data_v2.win: reload it and verify fonts/sprites/strings.
using System;
using System.IO;
using System.Text;
using System.Linq;

var log = new StringBuilder();

var gf = Data.Fonts.ByName("fntGameFont");
log.AppendLine($"fntGameFont: glyphs={gf.Glyphs.Count} scale=({gf.ScaleX},{gf.ScaleY}) em={gf.EmSize}");
foreach (var code in new ushort[] { 65, 27704, 20154 })  // A, 永, 人
{
    var g = gf.Glyphs.FirstOrDefault(x => x.Character == code);
    if (g == null) { log.AppendLine($"  {code}: MISSING"); continue; }
    log.AppendLine($"  {(char)code}: src=({g.SourceX},{g.SourceY}) {g.SourceWidth}x{g.SourceHeight} shift={g.Shift} off={g.Offset}");
}
var tiny = Data.Fonts.ByName("fntTiny");
var t98 = tiny.Glyphs.FirstOrDefault(x => x.Character == 27704);
log.AppendLine($"fntTiny: glyphs={tiny.Glyphs.Count} scale=({tiny.ScaleX},{tiny.ScaleY}) 永 {t98.SourceWidth}x{t98.SourceHeight}");

foreach (var name in new[] { "sprAnyaTypewriterFont", "sprAnyaFancyFont", "sprAnyaReviewFont" })
{
    var spr = Data.Sprites.ByName(name);
    log.AppendLine($"{name}: textures={spr.Textures.Count}");
    var last = spr.Textures[spr.Textures.Count - 1].Texture;
    log.AppendLine($"  last frame: src=({last.SourceX},{last.SourceY}) {last.SourceWidth}x{last.SourceHeight} tgt=({last.TargetX},{last.TargetY}) bbox={last.BoundingWidth}x{last.BoundingHeight}");
}

log.AppendLine($"charmap[8001] len={Data.Strings[8001].Content.Length} head={Data.Strings[8001].Content.Substring(0, 10)} tail={Data.Strings[8001].Content.Substring(Data.Strings[8001].Content.Length - 5)}");
var s = Data.Strings.Where(x => x.Content.Contains("开始") || x.Content.Contains("游戏")).Take(3);
foreach (var str in s) log.AppendLine($"sample CN string: {str.Content.Substring(0, Math.Min(40, str.Content.Length)).Replace("\n", "\\n")}");

Console.WriteLine(log.ToString());
