// Diff glyph sets: ORIGINAL backup data.win fonts vs current file's (rebuilt) fonts.
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using UndertaleModLib;

var orig = UndertaleData.CreateNew();
string origPath = @"D:\Steam\steamapps\common\Dead Estate\_loc_work\汉化补丁\backup_original\data.win";
using (var fs = new FileStream(origPath, FileMode.Open, FileAccess.Read))
    orig = UndertaleIO.Read(fs, (m, e) => { });

var sb = new StringBuilder();
foreach (var nf in Data.Fonts)
{
    var of = orig.Fonts.ByName(nf.Name.Content);
    if (of == null) { sb.AppendLine(nf.Name.Content + ": NOT IN ORIGINAL"); continue; }
    var oc = new SortedSet<char>(of.Glyphs.Select(g => (char)g.Character));
    var nc = new SortedSet<char>(nf.Glyphs.Select(g => (char)g.Character));
    var lost = oc.Where(c => !nc.Contains(c)).ToList();
    var gained = nc.Where(c => !oc.Contains(c)).ToList();
    sb.AppendLine(nf.Name.Content + ": orig=" + oc.Count + " new=" + nc.Count + " lost=" + lost.Count + " gainedCJK=" + gained.Count(c => c > 0x2FFF));
    if (lost.Count > 0)
        sb.AppendLine("  LOST: " + string.Join(" ", lost.Select(c => c + "(U+" + ((int)c).ToString("X4") + ")")));
}
File.WriteAllText(@"D:\Steam\steamapps\common\Dead Estate\_loc_work\dump\font_glyph_diff.txt", sb.ToString(), Encoding.UTF8);
Console.WriteLine("done");
