// Build the localized data.win in one pass:
//   1. replace the translatable string-table entries with their Chinese translations
//   2. swap each font's texture for the composed atlas and append the CJK glyphs
//
// Inputs (all under _loc_work):
//   dump/translations.json  -> { "<string index>": "<chinese>" }
//   fontbuild2/<FontName>/  -> <FontName>.png + glyphs_<FontName>.csv
using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Text;
using UndertaleModLib;
using UndertaleModLib.Models;

string work = @"D:\Steam\steamapps\common\Dead Estate\_loc_work";
string byName = Path.Combine(work, "fontbuild2");
var log = new StringBuilder();

// ---------------------------------------------------------------- 1. strings
string transJson = File.ReadAllText(Path.Combine(work, "dump", "translations.json"));
var trans = new Dictionary<int, string>();
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
    // walk to the closing quote, honouring backslash escapes
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
                case '/': sbv.Append('/'); break;
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

int replaced = 0;
foreach (var kv in trans)
{
    if (kv.Key >= 0 && kv.Key < Data.Strings.Count)
    {
        Data.Strings[kv.Key].Content = kv.Value;
        replaced++;
    }
}
log.AppendLine($"strings replaced: {replaced} / {trans.Count}");

// ---------------------------------------------------------------- 2. fonts
int fontsDone = 0, glyphsAdded = 0;
foreach (string fontDir in Directory.GetDirectories(byName))
{
    string fontName = Path.GetFileName(fontDir);
    string csvPath = Path.Combine(fontDir, $"glyphs_{fontName}.csv");
    string pngPath = Path.Combine(fontDir, $"{fontName}.png");
    if (!File.Exists(csvPath) || !File.Exists(pngPath))
    {
        log.AppendLine($"SKIP {fontName}: missing input");
        continue;
    }
    var font = Data.Fonts.ByName(fontName);
    if (font == null) { log.AppendLine($"SKIP {fontName}: font not found"); continue; }

    // new embedded texture holding original Latin art + the CJK additions
    var tex = new UndertaleEmbeddedTexture();
    tex.Name = new UndertaleString($"DEfont_{fontName}");
    tex.TextureData.Image = UndertaleModLib.Util.GMImage.FromPng(File.ReadAllBytes(pngPath));
    Data.EmbeddedTextures.Add(tex);

    var tpi = new UndertaleTexturePageItem();
    tpi.Name = new UndertaleString($"DEfontpage_{fontName}");
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

    var glyphs = new List<UndertaleFont.Glyph>();
    int head = 0, cjk = 0;
    foreach (string raw in File.ReadLines(csvPath))
    {
        if (string.IsNullOrWhiteSpace(raw)) continue;
        string[] s = raw.Split(';');
        if (head == 0) { head++; continue; }
        if (s.Length < 7) continue;
        ushort cp = ushort.Parse(s[0], CultureInfo.InvariantCulture);
        var gl = new UndertaleFont.Glyph();
        gl.Character = cp;
        gl.SourceX = ushort.Parse(s[1], CultureInfo.InvariantCulture);
        gl.SourceY = ushort.Parse(s[2], CultureInfo.InvariantCulture);
        gl.SourceWidth = ushort.Parse(s[3], CultureInfo.InvariantCulture);
        gl.SourceHeight = ushort.Parse(s[4], CultureInfo.InvariantCulture);
        gl.Shift = short.Parse(s[5], CultureInfo.InvariantCulture);
        gl.Offset = short.Parse(s[6], CultureInfo.InvariantCulture);
        glyphs.Add(gl);
        if (cp > 127) cjk++;
    }

    font.Glyphs.Clear();
    foreach (var g in glyphs) font.Glyphs.Add(g);
    font.Texture = tpi;

    fontsDone++;
    glyphsAdded += cjk;
    log.AppendLine($"font {fontName}: {glyphs.Count} glyphs ({cjk} CJK), atlas {(int)tex.TextureData.Image.Width}x{(int)tex.TextureData.Image.Height}");
}

log.AppendLine();
log.AppendLine($"fontsDone={fontsDone} cjkGlyphsAdded={glyphsAdded}");

// ---------------------------------------------------------------- 3. save
string outFile = Path.Combine(work, "out", "data.win");
Directory.CreateDirectory(Path.GetDirectoryName(outFile));
using (var fs = File.Create(outFile))
    UndertaleIO.Write(fs, Data);

log.AppendLine($"saved {outFile} ({new FileInfo(outFile).Length} bytes)");
File.WriteAllText(Path.Combine(work, "dump", "build_log.txt"), log.ToString());
Console.WriteLine(log.ToString());
