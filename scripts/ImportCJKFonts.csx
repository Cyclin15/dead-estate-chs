// CLI font importer: replaces each font with a fully repacked atlas that contains
// both the original Latin set and the new CJK glyphs. No prompts.
//
// Input: _loc_work/fontbuild/<FontName>/ containing atlas PNG(s) + glyphs_<FontName>.csv
// CSV format (8 columns): Character;SrcX;SrcY;SrcW;SrcH;Shift;Offset;Sheet
// One sheet == one PNG, and GameMaker fonts hold a single texture, so a font must
// fit on sheet 0; extra sheets are reported as an error rather than silently broken.
using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Text;
using UndertaleModLib;
using UndertaleModLib.Models;

string buildDir = @"D:\Steam\steamapps\common\Dead Estate\_loc_work\fontbuild";
var log = new StringBuilder();
int fontsUpdated = 0, glyphsTotal = 0, texturesAdded = 0;

foreach (string fontDir in Directory.GetDirectories(buildDir))
{
    string fontName = Path.GetFileName(fontDir);
    string csvPath = Path.Combine(fontDir, $"glyphs_{fontName}.csv");
    if (!File.Exists(csvPath)) { log.AppendLine($"SKIP {fontName}: no CSV"); continue; }

    UndertaleFont font = Data.Fonts.ByName(fontName);
    if (font == null) { log.AppendLine($"SKIP {fontName}: font asset not in data.win"); continue; }

    string basePng = Path.Combine(fontDir, $"{fontName}.png");
    if (!File.Exists(basePng)) { log.AppendLine($"SKIP {fontName}: no {fontName}.png"); continue; }
    if (Directory.GetFiles(fontDir, $"{fontName}_*.png").Length > 0)
        log.AppendLine($"WARN {fontName}: multiple sheets present; only sheet 0 is used (split the font instead)");

    var tex = new UndertaleEmbeddedTexture();
    tex.Name = new UndertaleString($"DEfont_{fontName}");
    tex.TextureData.Image = UndertaleModLib.Util.GMImage.FromPng(File.ReadAllBytes(basePng));
    Data.EmbeddedTextures.Add(tex);
    texturesAdded++;

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

    // Parse the CSV into a fresh glyph set (the atlas already contains the Latin set).
    var glyphs = new List<UndertaleFont.Glyph>();
    int head = 0, cjk = 0;
    foreach (string raw in File.ReadLines(csvPath))
    {
        if (string.IsNullOrWhiteSpace(raw)) continue;
        string[] s = raw.Split(';');
        if (head == 0) { head++; continue; }
        if (s.Length < 7) continue;
        int sheet = 0;
        if (s.Length > 7) int.TryParse(s[7], NumberStyles.Integer, CultureInfo.InvariantCulture, out sheet);
        if (sheet != 0) continue; // only sheet 0 is attached to the font object

        ushort cp = ushort.Parse(s[0], CultureInfo.InvariantCulture);
        short shift = short.Parse(s[5], CultureInfo.InvariantCulture);
        short off = short.Parse(s[6], CultureInfo.InvariantCulture);
        var gl = new UndertaleFont.Glyph();
        gl.Character = cp;
        gl.SourceX = ushort.Parse(s[1], CultureInfo.InvariantCulture);
        gl.SourceY = ushort.Parse(s[2], CultureInfo.InvariantCulture);
        gl.SourceWidth = ushort.Parse(s[3], CultureInfo.InvariantCulture);
        gl.SourceHeight = ushort.Parse(s[4], CultureInfo.InvariantCulture);
        gl.Shift = shift;
        gl.Offset = off;
        glyphs.Add(gl);
        if (cp > 126) cjk++;
    }

    font.Glyphs.Clear();
    foreach (var g in glyphs) font.Glyphs.Add(g);
    font.Texture = tpi;
    font.RangeStart = 32;
    font.RangeEnd = 0xFFFF;

    fontsUpdated++;
    glyphsTotal += glyphs.Count;
    log.AppendLine($"OK   {fontName}: {glyphs.Count} glyphs ({cjk} CJK), atlas {(int)tex.TextureData.Image.Width}x{(int)tex.TextureData.Image.Height}, total glyphs={font.Glyphs.Count}");
}

log.AppendLine();
log.AppendLine($"fontsUpdated={fontsUpdated} glyphsTotal={glyphsTotal} texturesAdded={texturesAdded}");
File.WriteAllText(@"D:\Steam\steamapps\common\Dead Estate\_loc_work\dump\font_import_log.txt", log.ToString());
Console.WriteLine(log.ToString());
