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

// ------------------------------------------------------------------ 1. strings
string transJson = File.ReadAllText(Path.Combine(work, "dump", "translations.json"));
var trans = new Dictionary<int, string>();
{
    int pos = 0;
    while (true)
    {
        int q1 = transJson.IndexOf('"', pos);
        if (q1 < 0) break;
        int q2 = transJson.IndexOf('"', q1 + 1);
        if (q2 < 0) break;
        string key = transJson.Substring(q1 + 1, q2 - q1 - 1);
        int colon = transJson.IndexOf(':', q2);
        int v1 = transJson.IndexOf('"', colon + 1);
        int v2 = v1 + 1;
        var sbv = new StringBuilder();
        while (v2 < transJson.Length)
        {
            char c = transJson[v2];
            if (c == '\\')
            {
                char e = transJson[v2 + 1];
                switch (e)
                {
                    case 'n': sbv.Append('\n'); break;
                    case 'r': sbv.Append('\r'); break;
                    case 't': sbv.Append('\t'); break;
                    case '"': sbv.Append('"'); break;
                    case '\\': sbv.Append('\\'); break;
                    case 'u':
                        int code = int.Parse(transJson.Substring(v2 + 2, 4), NumberStyles.HexNumber, CultureInfo.InvariantCulture);
                        sbv.Append((char)code);
                        v2 += 4;
                        break;
                    default: sbv.Append(e); break;
                }
                v2 += 2;
                continue;
            }
            if (c == '"') break;
            sbv.Append(c);
            v2++;
        }
        if (int.TryParse(key, out int idx)) trans[idx] = sbv.ToString();
        pos = v2 + 1;
    }
}
int replaced = 0;
foreach (var kv in trans)
    if (kv.Key >= 0 && kv.Key < Data.Strings.Count) { Data.Strings[kv.Key].Content = kv.Value; replaced++; }
log.AppendLine($"strings replaced: {replaced}/{trans.Count}");

// ------------------------------------------------------------------ 2. fonts
string byName = Path.Combine(work, "fontfinal2");
int fontsDone = 0, glyphsAdded = 0;
foreach (string fontDir in Directory.GetDirectories(byName))
{
    string fontName = Path.GetFileName(fontDir);
    string csvPath = Path.Combine(fontDir, $"glyphs_{fontName}.csv");
    if (!File.Exists(csvPath)) continue;
    var font = Data.Fonts.ByName(fontName);
    if (font == null) { log.AppendLine($"SKIP {fontName}: not in data.win"); continue; }

    var pages = new Dictionary<int, UndertaleTexturePageItem>();
    foreach (string png in Directory.GetFiles(fontDir, "*.png"))
    {
        string bn = Path.GetFileNameWithoutExtension(png);
        int sheet = 0;
        int us = bn.LastIndexOf('_');
        if (us > 0) int.TryParse(bn[(us + 1)..], NumberStyles.Integer, CultureInfo.InvariantCulture, out sheet);

        var tex = new UndertaleEmbeddedTexture();
        tex.Name = new UndertaleString($"DEf2_{fontName}_{sheet}");
        tex.TextureData.Image = UndertaleModLib.Util.GMImage.FromPng(File.ReadAllBytes(png));
        Data.EmbeddedTextures.Add(tex);

        var tpi = new UndertaleTexturePageItem();
        tpi.Name = new UndertaleString($"DEf2page_{fontName}_{sheet}");
        tpi.SourceX = 0; tpi.SourceY = 0;
        tpi.SourceWidth = (ushort)tex.TextureData.Image.Width;
        tpi.SourceHeight = (ushort)tex.TextureData.Image.Height;
        tpi.TargetX = 0; tpi.TargetY = 0;
        tpi.TargetWidth = (ushort)tex.TextureData.Image.Width;
        tpi.TargetHeight = (ushort)tex.TextureData.Image.Height;
        tpi.BoundingWidth = (ushort)tex.TextureData.Image.Width;
        tpi.BoundingHeight = (ushort)tex.TextureData.Image.Height;
        tpi.TexturePage = tex;
        Data.TexturePageItems.Add(tpi);
        pages[sheet] = tpi;
    }

    var glyphs = new List<UndertaleFont.Glyph>();
    int head = 0, cjk = 0;
    double headerScale = 1;
    foreach (string raw in File.ReadLines(csvPath))
    {
        if (string.IsNullOrWhiteSpace(raw)) continue;
        string[] s = raw.Split(';');
        if (head == 0)
        {
            // DisplayName;EmSize;Bold;Italic;Charset;AA;ScaleX;ScaleY  (scale = value to install)
            if (s.Length >= 8)
                double.TryParse(s[6], NumberStyles.Float, CultureInfo.InvariantCulture, out headerScale);
            head++;
            continue;
        }
        if (s.Length < 7) continue;
        var g = new UndertaleFont.Glyph();
        g.Character = ushort.Parse(s[0], CultureInfo.InvariantCulture);
        g.SourceX = ushort.Parse(s[1], CultureInfo.InvariantCulture);
        g.SourceY = ushort.Parse(s[2], CultureInfo.InvariantCulture);
        g.SourceWidth = ushort.Parse(s[3], CultureInfo.InvariantCulture);
        g.SourceHeight = ushort.Parse(s[4], CultureInfo.InvariantCulture);
        g.Shift = short.Parse(s[5], CultureInfo.InvariantCulture);
        g.Offset = short.Parse(s[6], CultureInfo.InvariantCulture);
        glyphs.Add(g);
        if (g.Character > 127) cjk++;
    }

    font.Glyphs.Clear();
    foreach (var g in glyphs) font.Glyphs.Add(g);
    if (pages.ContainsKey(0)) font.Texture = pages[0];
    font.ScaleX = (float)headerScale;
    font.ScaleY = (float)headerScale;

    fontsDone++;
    glyphsAdded += cjk;
}
log.AppendLine($"fonts: {fontsDone} rebuilt, {glyphsAdded} CJK glyphs (Scale=1, logical size)");

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

    string newMap = File.ReadAllText(Path.Combine(sprDir, name, "charmap.txt")).TrimEnd('\r', '\n');
    Data.Strings[mapIdx].Content = newMap;

    sprFrames += added;
    log.AppendLine($"sprite {name}: +{added} frames ({before} -> {spr.Textures.Count}), charmap[{mapIdx}] len {newMap.Length}");
}
log.AppendLine($"sprite frames added: {sprFrames}");

// ------------------------------------------------------------------ 4. write
string outDir = Path.Combine(work, "out");
Directory.CreateDirectory(outDir);
string outFile = Path.Combine(outDir, "data_v2.win");
using (var fs = File.Create(outFile)) UndertaleIO.Write(fs, Data);
log.AppendLine($"wrote {outFile} ({new FileInfo(outFile).Length} bytes)");

File.WriteAllText(Path.Combine(work, "dump", "build_v2.txt"), log.ToString());
Console.WriteLine(log.ToString());
