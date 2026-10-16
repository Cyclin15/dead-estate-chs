// Dump detailed font range info to understand how the game maps character codes to glyphs.
using System;
using System.IO;
using System.Text;
using UndertaleModLib;
using UndertaleModLib.Models;

string outPath = @"D:\Steam\steamapps\common\Dead Estate\_loc_work\dump\fontranges.txt";
var sb = new StringBuilder();

foreach (var f in Data.Fonts)
{
    if (f == null) continue;
    string disp = f.DisplayName != null ? f.DisplayName.Content : "";
    sb.AppendLine($"--- {f.Name.Content} (display={disp}) em={f.EmSize} bold={f.Bold} italic={f.Italic}");
    sb.AppendLine($"    RangeStart={f.RangeStart}  RangeEnd={f.RangeEnd}  GlyphCount={f.Glyphs.Count}  Charset={f.Charset}");
    // show a few glyph entries verbatim
    int n = 0;
    foreach (var g in f.Glyphs)
    {
        if (n++ >= 6) break;
        sb.AppendLine($"      char={g.Character} (0x{g.Character:X4}) sx={g.SourceX} sy={g.SourceY} sw={g.SourceWidth} sh={g.SourceHeight} shift={g.Shift} off={g.Offset}");
    }
    // last few
    var list = f.Glyphs;
    int start = Math.Max(0, list.Count - 4);
    for (int i = start; i < list.Count; i++)
    {
        var g = list[i];
        sb.AppendLine($"      ...char={g.Character} (0x{g.Character:X4}) sx={g.SourceX} sy={g.SourceY} sw={g.SourceWidth} sh={g.SourceHeight} shift={g.Shift} off={g.Offset}");
    }
    // check whether any glyph Character exceeds 255
    int over = 0;
    foreach (var g in f.Glyphs) if (g.Character > 255) over++;
    sb.AppendLine($"    glyphs with Character > 255: {over}");
}

// Also: what does the bytecode version / general info say about string encoding
sb.AppendLine();
sb.AppendLine("GeneralInfo:");
sb.AppendLine("  BytecodeVersion=" + Data.GeneralInfo.BytecodeVersion);
try { sb.AppendLine("  Major=" + Data.GeneralInfo.Major + " Minor=" + Data.GeneralInfo.Minor + " Build=" + Data.GeneralInfo.Build); } catch {}
try { sb.AppendLine("  Name=" + Data.GeneralInfo.Name.Content); } catch {}
try { sb.AppendLine("  DisplayName=" + Data.GeneralInfo.DisplayName.Content); } catch {}

File.WriteAllText(outPath, sb.ToString());
Console.WriteLine("wrote " + outPath);
