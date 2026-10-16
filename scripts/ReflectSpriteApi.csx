// Reflect the UTMT model API surface needed to append sprite frames,
// and dump the current geometry of the three Anya sprite fonts.
using System;
using System.IO;
using System.Text;
using System.Reflection;

var log = new StringBuilder();

void DumpType(Type t)
{
    log.AppendLine($"== {t.FullName}");
    foreach (var p in t.GetProperties(BindingFlags.Public | BindingFlags.Instance))
        log.AppendLine($"   prop {p.PropertyType.Name} {p.Name} {{ get={(p.CanRead)} set={(p.CanWrite)} }}");
    foreach (var f in t.GetFields(BindingFlags.Public | BindingFlags.Instance))
        log.AppendLine($"   field {f.FieldType.Name} {f.Name}");
}

DumpType(typeof(UndertaleModLib.Models.UndertaleSprite));
DumpType(typeof(UndertaleModLib.Models.UndertaleSprite.TextureEntry));
DumpType(typeof(UndertaleModLib.Models.UndertaleTexturePageItem));
DumpType(typeof(UndertaleModLib.Models.UndertaleEmbeddedTexture));
DumpType(typeof(UndertaleModLib.Models.UndertaleFont));

foreach (var name in new[] { "sprAnyaTypewriterFont", "sprAnyaFancyFont", "sprAnyaReviewFont" })
{
    var spr = Data.Sprites.ByName(name);
    log.AppendLine($"-- {name}: W={spr.Width} H={spr.Height} textures={spr.Textures.Count} masks={spr.CollisionMasks.Count}");
    for (int i = 0; i < 3; i++)
    {
        var te = spr.Textures[i];
        var t = te.Texture;
        log.AppendLine($"   frame {i}: src=({t.SourceX},{t.SourceY}) {t.SourceWidth}x{t.SourceHeight} tgt=({t.TargetX},{t.TargetY}) {t.TargetWidth}x{t.TargetHeight} bbox={t.BoundingWidth}x{t.BoundingHeight} page={t.TexturePage.Name.Content}");
    }
}

var tiny = Data.Fonts.ByName("fntTiny");
log.AppendLine($"fntTiny: EmSize={tiny.EmSize} LineHeight={tiny.LineHeight} Scale=({tiny.ScaleX},{tiny.ScaleY}) glyphs={tiny.Glyphs.Count}");
var gf = Data.Fonts.ByName("fntGameFont");
log.AppendLine($"fntGameFont: EmSize={gf.EmSize} LineHeight={gf.LineHeight} Scale=({gf.ScaleX},{gf.ScaleY})");

File.WriteAllText(Path.Combine(@"D:\Steam\steamapps\common\Dead Estate\_loc_work", "dump", "reflect_spriteapi.txt"), log.ToString());
Console.WriteLine(log.ToString());
