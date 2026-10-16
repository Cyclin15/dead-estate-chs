// Scan data_v3e.win: find all Functions / Variables whose Name is non-ASCII
// (i.e. got translated), and list which STRG indices are referenced as names.
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;

var data = Data;
string work = @"D:\Steam\steamapps\common\Dead Estate\_loc_work";

var sb = new StringBuilder();
int bad = 0;
foreach (var f in data.Functions)
{
    var c = f.Name?.Content;
    if (!string.IsNullOrEmpty(c) && c.Any(ch => ch > 127))
    { sb.AppendLine($"FUNC idx={data.Functions.IndexOf(f)} name={c}"); bad++; }
}
foreach (var v in data.Variables)
{
    var c = v.Name?.Content;
    if (!string.IsNullOrEmpty(c) && c.Any(ch => ch > 127))
    { sb.AppendLine($"VARI idx={data.Variables.IndexOf(v)} name={c}"); bad++; }
}
sb.AppendLine($"total non-ascii names: {bad}");

// protected index sets
var funcIdx = new HashSet<int>();
foreach (var f in data.Functions) funcIdx.Add(data.Strings.IndexOf(f.Name));
var variIdx = new HashSet<int>();
foreach (var v in data.Variables) variIdx.Add(data.Strings.IndexOf(v.Name));

// check against translations.json
var tr = Newtonsoft.Json.JsonConvert.DeserializeObject<Dictionary<string, string>>(
    File.ReadAllText(Path.Combine(work, "dump", "translations.json"), Encoding.UTF8));
int collide = 0;
foreach (var kv in tr)
{
    int i = int.Parse(kv.Key);
    if (funcIdx.Contains(i)) { sb.AppendLine($"COLLIDE-FUNC {i}: {kv.Value}"); collide++; }
    if (variIdx.Contains(i)) { sb.AppendLine($"COLLIDE-VARI {i}: {kv.Value}"); collide++; }
}
sb.AppendLine($"colliding translations: {collide}");
File.WriteAllText(Path.Combine(work, "dump", "name_scan.txt"), sb.ToString());
Console.WriteLine("scan done");
