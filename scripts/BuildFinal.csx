// Final assembly: install the Chinese strings and the oversampled fonts.
//
// Font scale is read from each CSV header (columns 7/8) so the value can be flipped
// without editing this script.
using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Text;
using UndertaleModLib;
using UndertaleModLib.Models;

string work = @"D:\Steam\steamapps\common\Dead Estate\_loc_work";
string scaleOverride = Environment.GetEnvironmentVariable("FONT_SCALE") ?? "";
string tag = Environment.GetEnvironmentVariable("BUILD_TAG") ?? "final";
string byName = Path.Combine(work, "fontfinal");
var log = new StringBuilder();

// ------------------------------------------------------------------ strings
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
log.AppendLine($"strings replaced: {replaced}");

// ------------------------------------------------------------------ fonts
int fontsDone = 0, glyphsAdded = 0, sheetsCreated = 0;
var scaleUsed = new SortedSet<string>();

foreach (string fontDir in Directory.GetDirectories(byName))
{
    string fontName = Path.GetFileName(fontDir);
    string csvPath = Path.Combine(fontDir, $"glyphs_{fontName}.csv");
    if (!File.Exists(csvPath)) continue;
    var font = Data.Fonts.ByName(fontName);
    if (font == null) { log.AppendLine($"SKIP {fontName}: not in data.win"); continue; }

    // one texture page item per sheet PNG
    var pages = new Dictionary<int, UndertaleTexturePageItem>();
    foreach (string png in Directory.GetFiles(fontDir, "*.png"))
    {
        string bn = Path.GetFileNameWithoutExtension(png);
        int sheet = 0;
        int us = bn.LastIndexOf('_');
        if (us > 0) int.TryParse(bn[(us + 1)..], NumberStyles.Integer, CultureInfo.InvariantCulture, out sheet);

        var tex = new UndertaleEmbeddedTexture();
        tex.Name = new UndertaleString($"DEfont_{fontName}_{sheet}");
        tex.TextureData.Image = UndertaleModLib.Util.GMImage.FromPng(File.ReadAllBytes(png));
        Data.EmbeddedTextures.Add(tex);

        var tpi = new UndertaleTexturePageItem();
        tpi.Name = new UndertaleString($"DEfontpage_{fontName}_{sheet}");
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
        sheetsCreated++;
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
            // DisplayName;EmSize;Bold;Italic;Charset;AntiAliasing;ScaleX;ScaleY
            if (s.Length >= 8)
            {
                double.TryParse(s[6], NumberStyles.Float, CultureInfo.InvariantCulture, out headerScale);
            }
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

    double fscale;
    if (!string.IsNullOrEmpty(scaleOverride))
    {
        double.TryParse(scaleOverride, NumberStyles.Float, CultureInfo.InvariantCulture, out fscale);
    }
    else
    {
        // CSV stores the oversample factor (e.g. 2); default to its reciprocal.
        fscale = 1.0 / headerScale;
    }
    font.ScaleX = (float)fscale;
    font.ScaleY = (float)fscale;
    scaleUsed.Add($"{fontName}={fscale:0.####}(csv {headerScale})");

    fontsDone++;
    glyphsAdded += cjk;
    log.AppendLine($"font {fontName}: {glyphs.Count} glyphs ({cjk} CJK), {pages.Count} sheet(s), ScaleX={fscale:0.####}");
}

log.AppendLine();
log.AppendLine($"fontsDone={fontsDone} cjkGlyphs={glyphsAdded} sheets={sheetsCreated}");

string outDir = Path.Combine(work, "out");
Directory.CreateDirectory(outDir);
string outFile = Path.Combine(outDir, $"data_{tag}.win");
using (var fs = File.Create(outFile)) UndertaleIO.Write(fs, Data);
log.AppendLine($"wrote {outFile} ({new FileInfo(outFile).Length} bytes)");

File.WriteAllText(Path.Combine(work, "dump", $"build_{tag}.txt"), log.ToString());
Console.WriteLine(log.ToString());
