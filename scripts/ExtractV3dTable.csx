// Extract the v3d translation table from out/data_v3d.win:
// for each STRG index where content differs from pristine, dump {idx: content}.
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;

var pristine = new Dictionary<int, string>();
foreach (var line in File.ReadAllLines(@"D:\Steam\steamapps\common\Dead Estate\_loc_work\dump\pristine_strings.json", Encoding.UTF8))
{
    // format: {"idx": "text", ...} pretty-printed with indent 1 -> parse via JSON instead
}
// simpler: use Newtonsoft
var pr = Newtonsoft.Json.JsonConvert.DeserializeObject<Dictionary<string, string>>(
    File.ReadAllText(@"D:\Steam\steamapps\common\Dead Estate\_loc_work\dump\pristine_strings.json", Encoding.UTF8));

var sb = new StringBuilder();
sb.AppendLine("{");
bool first = true;
int n = 0;
for (int i = 0; i < Data.Strings.Count; i++)
{
    if (!pr.TryGetValue(i.ToString(), out var orig)) continue;
    var cur = Data.Strings[i].Content ?? "";
    if (cur != orig)
    {
        if (!first) sb.AppendLine(",");
        first = false;
        var k = Newtonsoft.Json.JsonConvert.SerializeObject(i.ToString());
        var v = Newtonsoft.Json.JsonConvert.SerializeObject(cur);
        sb.Append($"  {k}: {v}");
        n++;
    }
}
sb.AppendLine();
sb.AppendLine("}");
File.WriteAllText(@"D:\Steam\steamapps\common\Dead Estate\_loc_work\dump\translations_v3d.json", sb.ToString());
Console.WriteLine($"v3d table entries: {n}");
