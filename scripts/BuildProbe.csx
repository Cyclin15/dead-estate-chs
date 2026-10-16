// Probe builder: compose one font (fntGameFontNormal) with 2x CJK art and set the font
// scale, then save. Run once per scale interpretation so a single in-game look decides
// whether ScaleX acts as a downward divisor or an upward multiplier.
//
// Env var PROBE_SCALE selects the value written into ScaleX/ScaleY.
using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Text;
using UndertaleModLib;
using UndertaleModLib.Models;

string work = @"D:\Steam\steamapps\common\Dead Estate\_loc_work";
float scale = float.Parse(Environment.GetEnvironmentVariable("PROBE_SCALE") ?? "2",
                          CultureInfo.InvariantCulture);
string tag = Environment.GetEnvironmentVariable("PROBE_TAG") ?? "x";
var log = new StringBuilder();

string atlasDir = Path.Combine(work, "probe_fonts", "fntGameFontNormal");
string cjkPng = Path.Combine(atlasDir, "cjk.png");
string cjkCsv = Path.Combine(atlasDir, "cjk_glyphs.csv");
string origDir = Path.Combine(work, "origfonts", "fntGameFontNormal");
string origPng = Path.Combine(origDir, "page.png");

var font = Data.Fonts.ByName("fntGameFontNormal");
log.AppendLine($"font {font.Name.Content}: EmSize={font.EmSize} glyphs={font.Glyphs.Count} " +
               $"ScaleX={font.ScaleX} ScaleY={font.ScaleY} Ascender={font.Ascender} " +
               $"LineHeight={font.LineHeight} AscenderOffset={font.AscenderOffset} " +
               $"Range={font.RangeStart}..{font.RangeEnd}");

// --- compose: original Latin region at (0,0), CJK band below ---
// UndertaleModLib's GMImage can load PNGs; we build the composite on the .NET side so the
// glyph table and the pixels come from one source of truth.
var latinImg = UndertaleModLib.Util.GMImage.FromPng(File.ReadAllBytes(origPng));
var cjkImg = UndertaleModLib.Util.GMImage.FromPng(File.ReadAllBytes(cjkPng));
log.AppendLine($"latin atlas {latinImg.Width}x{latinImg.Height}, cjk atlas {cjkImg.Width}x{cjkImg.Height}");

// Start from the CJK atlas size, then make room for the Latin region on top by using a
// canvas of max(width) x (latinHeight + cjkHeight). GameMaker reads pixels from the
// texture page, so we must actually produce that combined image.
uint cw = Math.Max(latinImg.Width, cjkImg.Width);
uint ch = latinImg.Height + cjkImg.Height;

// Build the combined PNG with ImageMagick (already referenced by UTMT).
var combined = new ImageMagick.MagickImage(ImageMagick.MagickColors.Transparent, cw, ch);
using (var src = new ImageMagick.MagickImage(origPng))
    combined.Composite(src, 0, 0, ImageMagick.CompositeOperator.Over);
using (var src2 = new ImageMagick.MagickImage(cjkPng))
    combined.Composite(src2, 0, (int)latinImg.Height, ImageMagick.CompositeOperator.Over);
string combinedPng = Path.Combine(work, "probe", $"combined_{tag}.png");
Directory.CreateDirectory(Path.GetDirectoryName(combinedPng));
combined.Write(combinedPng, ImageMagick.MagickFormat.Png);
log.AppendLine($"combined atlas {cw}x{ch} -> {combinedPng}");

// --- new embedded texture + page item ---
var tex = new UndertaleEmbeddedTexture();
tex.Name = new UndertaleString($"DEprobe_{tag}");
tex.TextureData.Image = UndertaleModLib.Util.GMImage.FromPng(File.ReadAllBytes(combinedPng));
Data.EmbeddedTextures.Add(tex);

var tpi = new UndertaleTexturePageItem();
tpi.Name = new UndertaleString($"DEprobepage_{tag}");
tpi.SourceX = 0; tpi.SourceY = 0;
tpi.SourceWidth = (ushort)cw; tpi.SourceHeight = (ushort)ch;
tpi.TargetX = 0; tpi.TargetY = 0;
tpi.TargetWidth = (ushort)cw; tpi.TargetHeight = (ushort)ch;
tpi.BoundingWidth = (ushort)cw; tpi.BoundingHeight = (ushort)ch;
tpi.TexturePage = tex;
Data.TexturePageItems.Add(tpi);

// --- glyph table: keep Latin as shipped, append CJK shifted by the Latin band height ---
int latinCount = 0, cjkCount = 0;
foreach (string raw in File.ReadLines(cjkCsv))
{
    if (string.IsNullOrWhiteSpace(raw)) continue;
    string[] s = raw.Split(';');
    if (s.Length < 6) continue;
    var g = new UndertaleFont.Glyph();
    g.Character = ushort.Parse(s[0], CultureInfo.InvariantCulture);
    g.SourceX = ushort.Parse(s[1], CultureInfo.InvariantCulture);
    g.SourceY = (ushort)(ushort.Parse(s[2], CultureInfo.InvariantCulture) + latinImg.Height);
    g.SourceWidth = ushort.Parse(s[3], CultureInfo.InvariantCulture);
    g.SourceHeight = ushort.Parse(s[4], CultureInfo.InvariantCulture);
    // Shift must stay the LOGICAL advance so the engine's layout is unaffected.
    g.Shift = (short)(ushort.Parse(s[5], CultureInfo.InvariantCulture) / 2);
    g.Offset = 0;
    font.Glyphs.Add(g);
    cjkCount++;
}
foreach (var g in font.Glyphs) { if (g.Character <= 127) latinCount++; }
log.AppendLine($"glyphs: latin={latinCount} cjk={cjkCount} total={font.Glyphs.Count}");

font.Texture = tpi;
font.ScaleX = scale;
font.ScaleY = scale;
log.AppendLine($"ScaleX/ScaleY set to {scale}");

string outFile = Path.Combine(work, "probe", $"data_{tag}.win");
using (var fs = File.Create(outFile)) UndertaleIO.Write(fs, Data);
log.AppendLine($"wrote {outFile} ({new FileInfo(outFile).Length} bytes)");

File.WriteAllText(Path.Combine(work, "dump", $"probe_{tag}.txt"), log.ToString());
Console.WriteLine(log.ToString());
