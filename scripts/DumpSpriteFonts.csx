// Dump the 4 sprite-based fonts: metadata, UNIQUE texture pages (deduped), per-frame coords,
// and locate the char-map strings. Log is written incrementally.
using System;
using System.IO;
using System.Text;
using System.Linq;
using System.Collections.Generic;
using UndertaleModLib;
using UndertaleModLib.Models;

string work = @"D:\Steam\steamapps\common\Dead Estate\_loc_work";
string logPath = Path.Combine(work, "dump", "spritefonts_info.txt");
var log = new StringBuilder();
void Flush()
{
    File.WriteAllText(logPath, log.ToString());
}
string[] names = { "sprAnyaTypewriterFont", "sprAnyaFancyFont", "sprDigitalDisplayFont", "sprAnyaReviewFont" };

foreach (string n in names)
{
    var spr = Data.Sprites.ByName(n);
    if (spr == null) { log.AppendLine($"MISSING sprite {n}"); Flush(); continue; }
    log.AppendLine($"SPRITE\t{n}\t{spr.Width}x{spr.Height}\tframes={spr.Textures.Count}\torigin=({spr.OriginX},{spr.OriginY})\tbboxMode={spr.BBoxMode}\tsepMasks={spr.SepMasks}\tsmooth={spr.Smooth}\tpreload={spr.Preload}");
    Flush();
    string dir = Path.Combine(work, "dump", "spritefonts", n);
    Directory.CreateDirectory(dir);
    var savedPages = new Dictionary<UndertaleEmbeddedTexture, int>();
    int pageNo = 0;
    for (int i = 0; i < spr.Textures.Count; i++)
    {
        var tex = spr.Textures[i].Texture;
        if (tex == null) { log.AppendLine($"FRAME\t{n}\t{i}\tNONE"); continue; }
        int tpiIdx = Data.TexturePageItems.IndexOf(tex);
        var page = tex.TexturePage;
        int p;
        if (!savedPages.TryGetValue(page, out p))
        {
            p = pageNo++;
            var img = page.TextureData.Image;
            using (var ms = new MemoryStream())
            {
                img.SavePng(ms);
                File.WriteAllBytes(Path.Combine(dir, $"page{p}.png"), ms.ToArray());
            }
            savedPages[page] = p;
            log.AppendLine($"PAGE\t{n}\t{p}\ttexsize={img.Width}x{img.Height}");
        }
        log.AppendLine($"FRAME\t{n}\t{i}\tlocalpage={savedPages[page]}\ttpi={tpiIdx}\tsrc=({tex.SourceX},{tex.SourceY})\t{tex.SourceWidth}x{tex.SourceHeight}\ttgt=({tex.TargetX},{tex.TargetY})\t{tex.TargetWidth}x{tex.TargetHeight}");
        if (i % 20 == 0) Flush();
    }
    Flush();
}

// locate char-map strings
log.AppendLine("== char-map strings ==");
string[] probes = {
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.!?,'\"-:;()[]/\\<>+-=*_1234567890%& ",
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ?' ",
    "0123456789secABCDEFGHIJKLMNOPQRSTUVWXYZ.",
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,-!?:;'\"1234567890 /"
};
for (int i = 0; i < Data.Strings.Count; i++)
{
    string c = Data.Strings[i].Content;
    foreach (var p in probes)
        if (c == p) { log.AppendLine($"CHARMAP\t[{i}]\tlen={c.Length}"); }
}
log.AppendLine("DONE");
Flush();
Console.WriteLine(log.ToString());
