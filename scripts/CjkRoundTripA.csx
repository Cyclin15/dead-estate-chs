// Proof-of-concept: verify the data format can carry CJK text and CJK glyph codes.
// 1) inject a Chinese string, 2) add a CJK glyph code to a font, 3) save, 4) reload and verify.
using System;
using System.IO;
using System.Text;
using UndertaleModLib;
using UndertaleModLib.Models;

string outFile = @"D:\Steam\steamapps\common\Dead Estate\_loc_work\dump\cjk_roundtrip.win";
var log = new StringBuilder();

// --- 1. inject a CJK string into an unused string slot ---
string cjk = "死亡庄园：汉化测试——简体中文";
int slot = -1;
for (int i = 0; i < Data.Strings.Count; i++)
{
    if (string.IsNullOrEmpty(Data.Strings[i].Content)) { slot = i; break; }
}
if (slot < 0) { slot = Data.Strings.Count - 1; }
string before = Data.Strings[slot].Content;
Data.Strings[slot].Content = cjk;
log.AppendLine($"string slot {slot}: '{before}' -> '{cjk}'  (len={cjk.Length})");

// --- 2. add CJK glyph codes to the first font and record originals ---
var font = Data.Fonts[0];
log.AppendLine($"font {font.Name.Content}: RangeStart={font.RangeStart} RangeEnd={font.RangeEnd} glyphs={font.Glyphs.Count}");
ushort testCp = 0x6B7B; // 死
var g = new UndertaleFont.Glyph();
g.Character = testCp;
g.SourceX = 2; g.SourceY = 2; g.SourceWidth = 20; g.SourceHeight = 20;
g.Shift = 20; g.Offset = 0;
font.Glyphs.Add(g);
ushort testCp2 = 0x4EA1; // 亡
var g2 = new UndertaleFont.Glyph();
g2.Character = testCp2;
g2.SourceX = 24; g2.SourceY = 2; g2.SourceWidth = 20; g2.SourceHeight = 20;
g2.Shift = 20; g2.Offset = 0;
font.Glyphs.Add(g2);
log.AppendLine($"  added glyphs U+{testCp:X4}, U+{testCp2:X4}; glyph count now {font.Glyphs.Count}");

// --- 3. save ---
using (var fs = File.Create(outFile))
{
    UndertaleIO.Write(fs, Data);
}
log.AppendLine($"saved: {outFile} ({new FileInfo(outFile).Length} bytes)");

File.WriteAllText(@"D:\Steam\steamapps\common\Dead Estate\_loc_work\dump\cjk_test_phase1.txt", log.ToString());
Console.WriteLine(log.ToString());
