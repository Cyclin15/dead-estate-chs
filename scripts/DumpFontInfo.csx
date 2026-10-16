using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using UndertaleModLib;
using UndertaleModLib.Models;

string outPath = @"D:\Steam\steamapps\common\Dead Estate\_loc_work\dump\fontinfo.json";

var sb = new StringBuilder();
sb.AppendLine("[");

var fonts = Data.Fonts;
for (int i = 0; i < fonts.Count; i++)
{
    var f = fonts[i];
    int glyphCount = f.Glyphs != null ? f.Glyphs.Count : 0;

    // collect mapped codepoints
    var cps = new List<int>();
    if (f.Glyphs != null)
    {
        foreach (var g in f.Glyphs)
        {
            if (g.Character != 0 || g.SourceX != 0 || g.SourceY != 0)
                cps.Add((int)g.Character);
        }
    }
    cps.Sort();
    int minCp = cps.Count > 0 ? cps[0] : 0;
    int maxCp = cps.Count > 0 ? cps[cps.Count - 1] : 0;

    bool hasCJK = false;
    foreach (int c in cps) { if (c >= 0x4E00 && c <= 0x9FFF) { hasCJK = true; break; } }

    string display = f.DisplayName != null ? f.DisplayName.Content : null;
    if (display == null && f.Name != null) display = f.Name.Content;

    string glyphsSample = "";
    int take = 0;
    foreach (int c in cps)
    {
        if (take++ >= 40) break;
        glyphsSample += c.ToString("X4") + " ";
    }

    var line = new StringBuilder();
    line.Append("  {");
    line.Append("\"index\": ").Append(i).Append(", ");
    line.Append("\"name\": \"").Append((f.Name != null ? f.Name.Content : "").Replace("\\", "\\\\").Replace("\"", "\\\"")).Append("\", ");
    line.Append("\"displayName\": \"").Append((display ?? "").Replace("\\", "\\\\").Replace("\"", "\\\"")).Append("\", ");
    line.Append("\"emSize\": ").Append(f.EmSize).Append(", ");
    line.Append("\"bold\": ").Append(f.Bold ? "true" : "false").Append(", ");
    line.Append("\"italic\": ").Append(f.Italic ? "true" : "false").Append(", ");
    line.Append("\"glyphCount\": ").Append(glyphCount).Append(", ");
    line.Append("\"mappedCount\": ").Append(cps.Count).Append(", ");
    line.Append("\"minCp\": ").Append(minCp).Append(", ");
    line.Append("\"maxCp\": ").Append(maxCp).Append(", ");
    line.Append("\"hasCJK\": ").Append(hasCJK ? "true" : "false").Append(", ");
    line.Append("\"glyphsSample\": \"").Append(glyphsSample.Trim()).Append("\"");
    line.Append("},");
    sb.AppendLine(line.ToString());
}
sb.AppendLine("]");

File.WriteAllText(outPath, sb.ToString());
Console.WriteLine("Wrote " + outPath + "  fonts=" + fonts.Count);
