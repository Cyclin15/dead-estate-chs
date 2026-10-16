// Verify how a font glyph character code is physically encoded in data.win.
// fnt_gm_15 is serialized early, so we can locate its glyph table and inspect bytes.
using System;
using System.IO;
using System.Text;
using UndertaleModLib;
using UndertaleModLib.Models;

string outPath = @"D:\Steam\steamapps\common\Dead Estate\_loc_work\dump\glyph_encoding.txt";
var sb = new StringBuilder();

var font = Data.Fonts[0];
sb.AppendLine($"font {font.Name.Content}: RangeStart={font.RangeStart} RangeEnd={font.RangeEnd} glyphs={font.Glyphs.Count}");

// Compute the exact byte size of the glyph array as the library would write it,
// then compare against observations in the raw file.
int count = font.Glyphs.Count;
var chars = new ushort[count];
int k = 0;
foreach (var g in font.Glyphs) chars[k++] = g.Character;
sb.AppendLine("first 8 Character values: " + string.Join(",", chars[0..8]));
sb.AppendLine("last 5 Character values : " + string.Join(",", chars[(count-5)..count]));

// Look for the distinctive run of the first several character codes in the raw file
string file = @"D:\Steam\steamapps\common\Dead Estate\data.win";
byte[] all = File.ReadAllBytes(file);

// Probe: is it 1 byte per char (old format) or 2 bytes (GMS2)?
// Build both candidate byte patterns for characters 32,33,34,35,36,37,38,39
var b1 = new byte[] { 32, 33, 34, 35, 36, 37, 38, 39 };
var b2 = new byte[] { 32,0, 33,0, 34,0, 35,0, 36,0, 37,0, 38,0, 39,0 };
sb.AppendLine();
sb.AppendLine("=== searching raw file for the leading glyph character sequence ===");
sb.AppendLine("1-byte pattern found at: " + string.Join(",", FindAll(all, b1, 6)));
sb.AppendLine("2-byte pattern found at: " + string.Join(",", FindAll(all, b2, 6)));

// Also search for the single 2-byte value 0x25AF (9647) near the glyph area
var v = new byte[] { 0xAF, 0x25 };
sb.AppendLine("bytes AF 25 occurrences: " + string.Join(",", FindAll(all, v, 10)));

File.WriteAllText(outPath, sb.ToString());
Console.WriteLine(sb.ToString());

static System.Collections.Generic.List<long> FindAll(byte[] hay, byte[] needle, int max)
{
    var res = new System.Collections.Generic.List<long>();
    for (long i = 0; i + needle.Length <= hay.LongLength && res.Count < max; i++)
    {
        bool ok = true;
        for (int j = 0; j < needle.Length; j++) { if (hay[i + j] != needle[j]) { ok = false; break; } }
        if (ok) res.Add(i);
    }
    return res;
}
