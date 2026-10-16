// Phase 2: reload the file written by CjkRoundTripA and verify CJK survived the round-trip.
using System;
using System.IO;
using System.Text;
using UndertaleModLib;
using UndertaleModLib.Models;

string inFile = @"D:\Steam\steamapps\common\Dead Estate\_loc_work\dump\cjk_roundtrip.win";
var log = new StringBuilder();

string cjk = "死亡庄园：汉化测试——简体中文";
bool foundString = false;
for (int i = 0; i < Data.Strings.Count; i++)
{
    if (Data.Strings[i].Content == cjk) { foundString = true; log.AppendLine($"OK  CJK string survived at slot {i}"); break; }
}
if (!foundString) log.AppendLine("FAIL CJK string not found after reload");

var font = Data.Fonts[0];
bool g1 = false, g2 = false;
foreach (var gl in font.Glyphs)
{
    if (gl.Character == 0x6B7B) { g1 = true; log.AppendLine($"OK  glyph U+6B7B survived (shift={gl.Shift}, w={gl.SourceWidth})"); }
    if (gl.Character == 0x4EA1) { g2 = true; log.AppendLine($"OK  glyph U+4EA1 survived (shift={gl.Shift}, w={gl.SourceWidth})"); }
}
if (!g1) log.AppendLine("FAIL glyph U+6B7B lost");
if (!g2) log.AppendLine("FAIL glyph U+4EA1 lost");
log.AppendLine($"font glyph count after reload: {font.Glyphs.Count}");

// also confirm the string table is UTF-8 encoded on disk
byte[] all = File.ReadAllBytes(inFile);
byte[] needle = Encoding.UTF8.GetBytes(cjk);
int pos = -1;
for (int i = 0; i + needle.Length <= all.Length; i++)
{
    bool ok = true;
    for (int j = 0; j < needle.Length; j++) { if (all[i + j] != needle[j]) { ok = false; break; } }
    if (ok) { pos = i; break; }
}
log.AppendLine(pos >= 0 ? $"OK  raw UTF-8 bytes of the CJK string found at file offset {pos}" : "note: UTF-8 bytes not found as a contiguous run (may be null-terminated / offset-mapped)");

File.WriteAllText(@"D:\Steam\steamapps\common\Dead Estate\_loc_work\dump\cjk_test_phase2.txt", log.ToString());
Console.WriteLine(log.ToString());
