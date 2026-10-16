// V2 assembly (pixel-crisp build):
//   1. install Chinese strings from dump/translations.json
//   2. install fontfinal2 fonts: glyphs rendered at logical size, Scale=1 (from CSV header)
//   3. extend the 3 Anya sprite fonts with CJK frames (sheet0.png) and patch their
//      charmap strings, so the runtime font_add_sprite_ext fonts cover Chinese
// Runs against the ORIGINAL backup data.win.
using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Text;
using UndertaleModLib;
using UndertaleModLib.Models;

string work = @"D:\Steam\steamapps\common\Dead Estate\_loc_work";
var log = new StringBuilder();

// ------------------------------------------------------------------ 3. sprite fonts
string sprDir = Path.Combine(work, "spritefonts2");
int sprFrames = 0;
foreach (string tsv in Directory.GetFiles(sprDir, "cjkframes.tsv", SearchOption.AllDirectories))
{
    string name = Path.GetFileName(Path.GetDirectoryName(tsv));
    var spr = Data.Sprites.ByName(name);
    if (spr == null) { log.AppendLine($"SKIP {name}: sprite not found"); continue; }

    var lines = File.ReadAllLines(tsv);
    string[] hdr = lines[0].Split('\t');
    int cellH = int.Parse(hdr[0]);
    int mapIdx = int.Parse(hdr[1]);

    var tex = new UndertaleEmbeddedTexture();
    tex.Name = new UndertaleString($"DEspr_{name}");
    tex.TextureData.Image = UndertaleModLib.Util.GMImage.FromPng(File.ReadAllBytes(Path.Combine(sprDir, name, "sheet0.png")));
    Data.EmbeddedTextures.Add(tex);

    int before = spr.Textures.Count;
    int added = 0;
    for (int i = 1; i < lines.Length; i++)
    {
        if (string.IsNullOrWhiteSpace(lines[i])) continue;
        string[] p = lines[i].Split('\t');
        ushort ch = ushort.Parse(p[0]);
        ushort x = ushort.Parse(p[1]), y = ushort.Parse(p[2]);
        ushort w = ushort.Parse(p[3]), h = ushort.Parse(p[4]);
        ushort ty = ushort.Parse(p[5]);

        var tpi = new UndertaleTexturePageItem();
        tpi.Name = new UndertaleString($"DEsprf_{name}_{ch}");
        tpi.SourceX = x; tpi.SourceY = y;
        tpi.SourceWidth = w; tpi.SourceHeight = h;
        tpi.TargetX = 0; tpi.TargetY = ty;
        tpi.TargetWidth = w; tpi.TargetHeight = h;
        tpi.BoundingWidth = (ushort)spr.Width;
        tpi.BoundingHeight = (ushort)spr.Height;
        tpi.TexturePage = tex;
        Data.TexturePageItems.Add(tpi);

        spr.Textures.Add(new UndertaleSprite.TextureEntry { Texture = tpi });
        added++;
    }


    sprFrames += added;
    log.AppendLine($"sprite {name}: +{added} frames ({before} -> {spr.Textures.Count}), (charmap unchanged)");
}
log.AppendLine($"sprite frames added: {sprFrames}");

// ------------------------------------------------------------------ 4. write
string outDir = Path.Combine(work, "out");
Directory.CreateDirectory(outDir);
string outFile = Path.Combine(outDir, "data_bisectZ.win");
using (var fs = File.Create(outFile)) UndertaleIO.Write(fs, Data);
log.AppendLine($"wrote {outFile} ({new FileInfo(outFile).Length} bytes)");

File.WriteAllText(Path.Combine(work, "dump", "build_bisectZ.txt"), log.ToString());
Console.WriteLine(log.ToString());
