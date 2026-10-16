// Export each font's original texture region, its glyph table, and its metadata.
// Output goes to _loc_work/origfonts/<FontName>/{page.png,glyphs.csv,meta.tsv}
using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using UndertaleModLib;
using UndertaleModLib.Models;

string outRoot = @"D:\Steam\steamapps\common\Dead Estate\_loc_work\origfonts";
Directory.CreateDirectory(outRoot);
var log = new StringBuilder();

foreach (var f in Data.Fonts)
{
    if (f == null) continue;
    string dir = Path.Combine(outRoot, f.Name.Content);
    Directory.CreateDirectory(dir);

    // --- glyph table ---
    var gsb = new StringBuilder();
    gsb.AppendLine("Character;SourceX;SourceY;SourceWidth;SourceHeight;Shift;Offset");
    foreach (var g in f.Glyphs)
        gsb.AppendLine($"{g.Character};{g.SourceX};{g.SourceY};{g.SourceWidth};{g.SourceHeight};{g.Shift};{g.Offset}");
    File.WriteAllText(Path.Combine(dir, "glyphs.csv"), gsb.ToString());

    // --- metadata ---
    var t = f.Texture;
    int pw = 0, ph = 0;
    if (t != null && t.TexturePage != null && t.TexturePage.TextureData != null && t.TexturePage.TextureData.Image != null)
    {
        pw = (int)t.TexturePage.TextureData.Image.Width;
        ph = (int)t.TexturePage.TextureData.Image.Height;
    }
    var msb = new StringBuilder();
    msb.AppendLine("key\tvalue");
    msb.AppendLine($"DisplayName\t{(f.DisplayName != null ? f.DisplayName.Content : "")}");
    msb.AppendLine($"EmSize\t{f.EmSize}");
    msb.AppendLine($"Bold\t{f.Bold}");
    msb.AppendLine($"Italic\t{f.Italic}");
    msb.AppendLine($"RangeStart\t{f.RangeStart}");
    msb.AppendLine($"RangeEnd\t{f.RangeEnd}");
    msb.AppendLine($"PageWidth\t{pw}");
    msb.AppendLine($"PageHeight\t{ph}");
    msb.AppendLine($"ItemSourceX\t{(t != null ? t.SourceX : 0)}");
    msb.AppendLine($"ItemSourceY\t{(t != null ? t.SourceY : 0)}");
    msb.AppendLine($"ItemSourceWidth\t{(t != null ? t.SourceWidth : 0)}");
    msb.AppendLine($"ItemSourceHeight\t{(t != null ? t.SourceHeight : 0)}");
    File.WriteAllText(Path.Combine(dir, "meta.tsv"), msb.ToString());

    // --- texture region as PNG ---
    if (t != null)
    {
        try
        {
            var worker = new UndertaleModLib.Util.TextureWorker();
            worker.ExportAsPNG(t, Path.Combine(dir, "page.png"));
        }
        catch (Exception e)
        {
            log.AppendLine($"WARN {f.Name.Content}: page export failed: {e.Message}");
        }
    }
    log.AppendLine($"{f.Name.Content}: glyphs={f.Glyphs.Count} page={pw}x{ph} item={t?.SourceWidth}x{t?.SourceHeight} em={f.EmSize}");
}

File.WriteAllText(@"D:\Steam\steamapps\common\Dead Estate\_loc_work\dump\origfonts_log.txt", log.ToString());
Console.WriteLine(log.ToString());
