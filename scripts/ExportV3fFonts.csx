// Export current file's font textures + glyph tables for pixel-level ink analysis.
using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using UndertaleModLib;
using UndertaleModLib.Models;

string outRoot = @"D:\Steam\steamapps\common\Dead Estate\_loc_work\dump\v3ffonts";
Directory.CreateDirectory(outRoot);
var log = new StringBuilder();

foreach (var f in Data.Fonts)
{
    if (f == null) continue;
    string dir = Path.Combine(outRoot, f.Name.Content);
    Directory.CreateDirectory(dir);

    var gsb = new StringBuilder();
    gsb.AppendLine("Character;SourceX;SourceY;SourceWidth;SourceHeight;Shift;Offset");
    foreach (var g in f.Glyphs)
        gsb.AppendLine($"{g.Character};{g.SourceX};{g.SourceY};{g.SourceWidth};{g.SourceHeight};{g.Shift};{g.Offset}");
    File.WriteAllText(Path.Combine(dir, "glyphs.csv"), gsb.ToString());

    var t = f.Texture;
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
    log.AppendLine($"{f.Name.Content}: glyphs={f.Glyphs.Count}");
}
Console.WriteLine(log.ToString());
