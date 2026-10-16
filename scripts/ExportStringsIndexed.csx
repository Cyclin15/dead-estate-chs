using System;
using System.IO;
using System.Text;
using UndertaleModLib;

string outPath = @"D:\Steam\steamapps\common\Dead Estate\_loc_work\dump\strings_indexed.json";

var sb = new StringBuilder();
sb.Append("{\n\"Strings\": [\n");
for (int i = 0; i < Data.Strings.Count; i++)
{
    string s = Data.Strings[i].Content ?? "";
    sb.Append("  \"");
    foreach (char c in s)
    {
        switch (c)
        {
            case '"': sb.Append("\\\""); break;
            case '\\': sb.Append("\\\\"); break;
            case '\n': sb.Append("\\n"); break;
            case '\r': sb.Append("\\r"); break;
            case '\t': sb.Append("\\t"); break;
            default:
                if (c < 32) sb.Append("\\u").Append(((int)c).ToString("x4"));
                else sb.Append(c);
                break;
        }
    }
    sb.Append(i == Data.Strings.Count - 1 ? "\"\n" : "\",\n");
}
sb.Append("]\n}\n");

File.WriteAllText(outPath, sb.ToString());
Console.WriteLine("Wrote " + Data.Strings.Count + " strings to " + outPath);
