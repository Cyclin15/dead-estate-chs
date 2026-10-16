// Dump per-font glyph info from the installed data.win: coverage of key chars.
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;

var sb = new StringBuilder();
var key = new[] { ' ', '\u3000', '♦', ',', '.', 'A', '0', '，', '。', '的' };
foreach (var f in Data.Fonts)
{
    var glyphs = new HashSet<char>(f.Glyphs.Select(g => (char)g.Character));
    sb.Append($"{f.Name.Content}: n={f.Glyphs.Count} asc={f.Ascender}");
    foreach (var c in key)
        sb.Append($" {(int)c:X4}:{(glyphs.Contains(c) ? "Y" : "-")}");
    // space glyph details
    var sp = f.Glyphs.FirstOrDefault(g => g.Character == ' ');
    if (sp != null) sb.Append($" space(w={sp.SourceWidth},h={sp.SourceHeight},shift={sp.Shift})");
    var fw = f.Glyphs.FirstOrDefault(g => g.Character == '\u3000');
    if (fw != null) sb.Append($" fw(w={fw.SourceWidth},h={fw.SourceHeight},shift={fw.Shift})");
    sb.AppendLine();
}
File.WriteAllText(@"D:\Steam\steamapps\common\Dead Estate\_loc_work\dump\font_glyphsets.txt", sb.ToString());
Console.WriteLine("done");
