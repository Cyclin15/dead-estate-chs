// Transplant the 34 rebuilt fonts (glyph tables + textures + scalar fields)
// from out/data_v2.win into the currently loaded file (v3f).
// Keeps: current strings/translations, Anya CN fonts, bytecode patch, breakString fix.
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using UndertaleModLib;
using UndertaleModLib.Models;

string work = @"D:\Steam\steamapps\common\Dead Estate\_loc_work";
string outName = Environment.GetEnvironmentVariable("OUTNAME") ?? "data_v3g.win";

var v2 = UndertaleData.CreateNew();
using (var fs = new FileStream(Path.Combine(work, "out", "data_v2.win"), FileMode.Open, FileAccess.Read))
    v2 = UndertaleIO.Read(fs, (m, e) => { });

var log = new StringBuilder();
int swapped = 0;
foreach (var font in Data.Fonts)
{
    var src = v2.Fonts.ByName(font.Name.Content);
    if (src == null) { log.AppendLine("KEEP " + font.Name.Content + " (not in v2)"); continue; }

    // scalar fields
    font.EmSize = src.EmSize;
    font.Bold = src.Bold;
    font.Italic = src.Italic;
    font.RangeStart = src.RangeStart;
    font.RangeEnd = src.RangeEnd;
    font.Charset = src.Charset;
    font.AntiAliasing = src.AntiAliasing;
    font.ScaleX = src.ScaleX;
    font.ScaleY = src.ScaleY;
    font.Ascender = src.Ascender;
    font.LineHeight = src.LineHeight;
    font.AscenderOffset = src.AscenderOffset;
    font.SDFSpread = src.SDFSpread;
    // NOTE: do NOT copy Name/DisplayName (they reference v2's string table)

    // glyphs (fresh objects, do not share instances across files)
    font.Glyphs.Clear();
    foreach (var g in src.Glyphs)
    {
        var ng = new UndertaleFont.Glyph();
        ng.Character = g.Character;
        ng.SourceX = g.SourceX;
        ng.SourceY = g.SourceY;
        ng.SourceWidth = g.SourceWidth;
        ng.SourceHeight = g.SourceHeight;
        ng.Shift = g.Shift;
        ng.Offset = g.Offset;
        ng.Kerning = g.Kerning;
        font.Glyphs.Add(ng);
    }

    // texture page: new entries in THIS file carrying v2's image
    var st = src.Texture;
    var tex = new UndertaleEmbeddedTexture();
    tex.Name = new UndertaleString("DEv2_" + font.Name.Content);
    tex.TextureData.Image = st.TexturePage.TextureData.Image;
    Data.EmbeddedTextures.Add(tex);
    var tpi = new UndertaleTexturePageItem();
    tpi.Name = new UndertaleString("DEv2page_" + font.Name.Content);
    tpi.SourceX = st.SourceX; tpi.SourceY = st.SourceY;
    tpi.SourceWidth = st.SourceWidth; tpi.SourceHeight = st.SourceHeight;
    tpi.TargetX = st.TargetX; tpi.TargetY = st.TargetY;
    tpi.TargetWidth = st.TargetWidth; tpi.TargetHeight = st.TargetHeight;
    tpi.BoundingWidth = st.BoundingWidth; tpi.BoundingHeight = st.BoundingHeight;
    tpi.TexturePage = tex;
    Data.TexturePageItems.Add(tpi);
    font.Texture = tpi;

    swapped++;
    log.AppendLine("SWAP " + font.Name.Content + ": glyphs=" + font.Glyphs.Count);
}

string outFile = Path.Combine(work, "out", outName);
using (var fs = File.Create(outFile)) UndertaleIO.Write(fs, Data);
Console.WriteLine("swapped " + swapped + " fonts; wrote " + outFile + " (" + new FileInfo(outFile).Length + " bytes)");
Console.WriteLine(log.ToString());
