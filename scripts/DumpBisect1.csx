using System;
using System.IO;
using System.Text;
using System.Linq;
var log = new StringBuilder();
foreach (var name in new[] { "sprAnyaFancyFont", "sprAnyaTypewriterFont", "sprAnyaReviewFont" })
{
    var spr = Data.Sprites.ByName(name);
    log.AppendLine($"{name}: frames={spr.Textures.Count} W={spr.Width} H={spr.Height} bbox={spr.BBoxMode}");
    // frame 0 (original) and frame 55/56 (first appended)
    foreach (int i in new[] { 0, spr.Textures.Count - 1 })
    {
        var t = spr.Textures[i].Texture;
        var img = t.TexturePage.TextureData.Image;
        log.AppendLine($"  frame {i}: src=({t.SourceX},{t.SourceY}) {t.SourceWidth}x{t.SourceHeight} tgt=({t.TargetX},{t.TargetY}) {t.TargetWidth}x{t.TargetHeight} bbox={t.BoundingWidth}x{t.BoundingHeight} page={img.Width}x{img.Height}");
    }
    // count distinct texture pages
    int pages = spr.Textures.Select(x => x.Texture.TexturePage).Distinct().Count();
    log.AppendLine($"  distinct pages: {pages}");
}
log.AppendLine($"embedded textures total: {Data.EmbeddedTextures.Count}");
log.AppendLine($"texture page items total: {Data.TexturePageItems.Count}");
var s7999 = Data.Strings[7999].Content;
log.AppendLine($"charmap[7999] len={s7999.Length} first55match={s7999.Substring(0,55) == "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ?' "}");
Console.WriteLine(log.ToString());
