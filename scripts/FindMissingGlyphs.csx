// For every font, list chars from charset.txt that have NO glyph entry.
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;

var charset = new HashSet<int>(File.ReadAllText(@"D:\Steam\steamapps\common\Dead Estate\_loc_work\charset.txt", Encoding.UTF8)
    .Select(c => (int)c).Where(c => c > 127));
var sb = new StringBuilder();
foreach (var f in Data.Fonts)
{
    var have = new HashSet<int>(f.Glyphs.Select(g => (int)g.Character));
    var missing = charset.Where(c => !have.Contains(c)).Select(c => (char)c).ToList();
    sb.AppendLine(f.Name.Content + ": missing " + missing.Count + " / " + charset.Count);
    if (missing.Count > 0)
        sb.AppendLine("  " + string.Join(" ", missing.Select(c => c + "(U+" + ((int)c).ToString("X4") + ")")));
}
File.WriteAllText(@"D:\Steam\steamapps\common\Dead Estate\_loc_work\dump\font_missing_chars.txt", sb.ToString(), Encoding.UTF8);
Console.WriteLine("done, charset=" + charset.Count);
