// Probe how ScaleX/ScaleY are stored for a font in this data format version.
using System;
using System.IO;
using System.Text;
using UndertaleModLib;
using UndertaleModLib.Models;

var outPath = @"D:\Steam\steamapps\common\Dead Estate\_loc_work\dump\scale_probe.txt";
var sb = new StringBuilder();

// Leave the data untouched except for a unique marker in one font's scale fields.
var f = Data.Fonts.ByName("fntGameFontNormal");
sb.AppendLine($"original: ScaleX={f.ScaleX} ScaleY={f.ScaleY} EmSize={f.EmSize} glyphs={f.Glyphs.Count}");

// Use an unusual-but-valid pair so it is unmistakable in the byte stream.
f.ScaleX = 4;
f.ScaleY = 8;
sb.AppendLine($"set: ScaleX={f.ScaleX} ScaleY={f.ScaleY}");

string outFile = @"D:\Steam\steamapps\common\Dead Estate\_loc_work\dump\scale_probe.win";
using (var fs = File.Create(outFile)) UndertaleIO.Write(fs, Data);
sb.AppendLine("wrote " + outFile);

File.WriteAllText(outPath, sb.ToString());
Console.WriteLine(sb.ToString());
