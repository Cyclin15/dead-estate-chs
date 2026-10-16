// Extract every translatable unit into a single reviewable TSV.
// Two sources: (1) the string table, (2) string literals used as display text in GML.
// We only REPORT here; the actual replacement works on the string table by index.
using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using System.Text.RegularExpressions;
using UndertaleModLib;
using UndertaleModLib.Models;

string outPath = @"D:\Steam\steamapps\common\Dead Estate\_loc_work\dump\units.tsv";
string jsonPath = @"D:\Steam\steamapps\common\Dead Estate\_loc_work\dump\units.json";

var shaderRe = new Regex(@"#version|gl_FragColor|uniform\s+sampler2D|void\s+main\s*\(", RegexOptions.IgnoreCase);
var identRe = new Regex(@"^[A-Za-z_][A-Za-z0-9_]*$");
var pathRe = new Regex(@"^[A-Za-z0-9_\\/\.\-]+$");
var wordRe = new Regex(@"[A-Za-z]{2,}");
var punctRe = new Regex(@"[.,!?'""\-:;]");

int prose = 0;
var sb = new StringBuilder();
var json = new StringBuilder();
sb.AppendLine("idx\tlen\tkind\ttext");
json.Append("[");

for (int i = 0; i < Data.Strings.Count; i++)
{
    string s = Data.Strings[i].Content ?? "";
    string t = s.Trim();
    if (t.Length == 0) continue;
    if (shaderRe.IsMatch(t)) continue;
    if (identRe.IsMatch(t) || pathRe.IsMatch(t)) continue;
    if (!wordRe.IsMatch(t)) continue;
    if (!(t.Contains(" ") || punctRe.IsMatch(t))) continue;

    prose++;
    string kind = t.Length > 1500 ? "credits" : "text";
    string flat = s.Replace("\\", "\\\\").Replace("\t", "\\t").Replace("\r", "").Replace("\n", "\\n");
    sb.Append(i).Append('\t').Append(s.Length).Append('\t').Append(kind).Append('\t').Append(flat).Append('\n');

    if (prose > 1) json.Append(",\n");
    json.Append("  {\"idx\":").Append(i).Append(",\"t\":\"");
    foreach (char c in s)
    {
        switch (c)
        {
            case '"': json.Append("\\\""); break;
            case '\\': json.Append("\\\\"); break;
            case '\n': json.Append("\\n"); break;
            case '\r': continue;
            case '\t': json.Append("\\t"); break;
            default:
                if (c < 32) json.Append("\\u").Append(((int)c).ToString("x4"));
                else json.Append(c);
                break;
        }
    }
    json.Append("\"}");
}
json.Append("\n]\n");

File.WriteAllText(outPath, sb.ToString());
File.WriteAllText(jsonPath, json.ToString());
Console.WriteLine("translatable units = " + prose);
Console.WriteLine("tsv: " + outPath);
Console.WriteLine("json: " + jsonPath);
