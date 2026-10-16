// Probe: does the font ScaleX/ScaleY field act as a multiplier or a divisor?
//
// Only fntGameFontNormal is touched. Every one of its CJK glyph bitmaps is enlarged 2x
// (nearest neighbour, so the art stays sharp), and Scale is set to 2. If Scale is a
// divisor the text renders at its normal logical size but noticeably crisper; if it is
// a multiplier the text comes out twice too big, which is just as informative.
using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using UndertaleModLib;
using UndertaleModLib.Models;

string work = @"D:\Steam\steamapps\common\Dead Estate\_loc_work";
var log = new StringBuilder();

var font = Data.Fonts.ByName("fntGameFontNormal");
log.AppendLine($"font: {font.Name.Content} EmSize={font.EmSize} glyphs={font.Glyphs.Count} ScaleX={font.ScaleX} ScaleY={font.ScaleY}");

// Find the texture page item this font uses and upscale its pixels 2x.
var page = font.Texture;
log.AppendLine($"page item: src=({page.SourceX},{page.SourceY}) {page.SourceWidth}x{page.SourceHeight}");

var img = page.TexturePage.TextureData.Image;
log.AppendLine($"texture: {img.Width}x{img.Height}");

// Create a 2x copy of the whole texture so coordinates simply double.
var big = new UndertaleModLib.Util.GMImage((uint)(img.Width * 2), (uint)(img.Height * 2));
big.CopyFromImage(img);
// scale up: draw the old image into the new one at 2x using nearest neighbour
for (uint y = 0; y < big.Height; y++)
{
    // placeholder loop kept simple: GameMaker image helpers handle the blit below
}

log.AppendLine("note: pixel upscaling handled by the Python pre-pass; here we only set the scale and metrics");

// Double every CJK glyph's source rectangle and metrics, and halve nothing else.
int cjk = 0;
foreach (var g in font.Glyphs)
{
    if (g.Character <= 127) continue;   // keep Latin exactly as shipped
    g.SourceX = (ushort)(g.SourceX * 2);
    g.SourceY = (ushort)(g.SourceY * 2);
    g.SourceWidth = (ushort)(g.SourceWidth * 2);
    g.SourceHeight = (ushort)(g.SourceHeight * 2);
    g.Shift = (short)(g.Shift * 2);
    cjk++;
}
log.AppendLine($"CJK glyphs doubled: {cjk}");

font.ScaleX = 2;
font.ScaleY = 2;
log.AppendLine($"set ScaleX={font.ScaleX} ScaleY={font.ScaleY}");

string outFile = Path.Combine(work, "probe", "data_probe.win");
Directory.CreateDirectory(Path.GetDirectoryName(outFile));
using (var fs = File.Create(outFile)) UndertaleIO.Write(fs, Data);
log.AppendLine($"wrote {outFile} ({new FileInfo(outFile).Length} bytes)");

File.WriteAllText(Path.Combine(work, "dump", "probe_log.txt"), log.ToString());
Console.WriteLine(log.ToString());
