// Independent read-back: dump a sample of the translated strings using ordinal
// comparison (no non-ASCII literals in this file, so no encoding ambiguity).
using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using UndertaleModLib;

string work = @"D:\Steam\steamapps\common\Dead Estate\_loc_work";
string outPath = Path.Combine(work, "dump", "sample_zh.txt");
var sb = new StringBuilder();

// indices chosen to span items, weapons, dialogue and UI
int[] probes = { 846, 847, 850, 851, 763, 14509, 14617, 14560, 14002, 13319 };
foreach (int i in probes)
{
    if (i < Data.Strings.Count)
        sb.AppendLine($"[{i}] {Data.Strings[i].Content}");
}

// count how many string entries are not pure ASCII (i.e. translated)
int nonAscii = 0, total = 0;
foreach (var s in Data.Strings)
{
    if (s.Content == null) continue;
    total++;
    foreach (char c in s.Content) { if (c > 127) { nonAscii++; break; } }
}
sb.AppendLine();
sb.AppendLine($"strings with non-ASCII content: {nonAscii} / {total}");

File.WriteAllText(outPath, sb.ToString(), new UTF8Encoding(false));
Console.WriteLine($"wrote {outPath}: nonAscii={nonAscii}/{total}");
