// Scan: find translations that collide with ANY name reference
// (functions, variables, and all asset names) — those must stay untranslated.
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;

var sb = new StringBuilder();
var protectedIdx = new HashSet<int>();
foreach (var f in Data.Functions) protectedIdx.Add(Data.Strings.IndexOf(f.Name));
foreach (var v in Data.Variables) protectedIdx.Add(Data.Strings.IndexOf(v.Name));
foreach (var s in Data.Sprites) protectedIdx.Add(Data.Strings.IndexOf(s.Name));
foreach (var s in Data.Sounds) protectedIdx.Add(Data.Strings.IndexOf(s.Name));
foreach (var b in Data.Backgrounds) protectedIdx.Add(Data.Strings.IndexOf(b.Name));
foreach (var p in Data.Paths) protectedIdx.Add(Data.Strings.IndexOf(p.Name));
foreach (var s in Data.Scripts) protectedIdx.Add(Data.Strings.IndexOf(s.Name));
foreach (var s in Data.Shaders) protectedIdx.Add(Data.Strings.IndexOf(s.Name));
foreach (var f in Data.Fonts) protectedIdx.Add(Data.Strings.IndexOf(f.Name));
foreach (var t in Data.Timelines) protectedIdx.Add(Data.Strings.IndexOf(t.Name));
foreach (var o in Data.GameObjects) protectedIdx.Add(Data.Strings.IndexOf(o.Name));
foreach (var r in Data.Rooms) protectedIdx.Add(Data.Strings.IndexOf(r.Name));
foreach (var e in Data.Extensions) protectedIdx.Add(Data.Strings.IndexOf(e.Name));
foreach (var s in Data.Sequences) protectedIdx.Add(Data.Strings.IndexOf(s.Name));
foreach (var a in Data.AnimationCurves) protectedIdx.Add(Data.Strings.IndexOf(a.Name));
protectedIdx.Remove(-1);
sb.AppendLine($"protected string indices: {protectedIdx.Count}");

var tr = Newtonsoft.Json.JsonConvert.DeserializeObject<Dictionary<string, string>>(
    File.ReadAllText(@"D:\Steam\steamapps\common\Dead Estate\_loc_work\dump\translations.json", Encoding.UTF8));
int collide = 0;
foreach (var kv in tr)
{
    if (int.TryParse(kv.Key, out int i) && protectedIdx.Contains(i))
    { sb.AppendLine($"COLLIDE {i}: pristine={Data.Strings[i].Content} translated={kv.Value}"); collide++; }
}
sb.AppendLine($"collisions: {collide}");
File.WriteAllText(@"D:\Steam\steamapps\common\Dead Estate\_loc_work\dump\name_scan2.txt", sb.ToString());
Console.WriteLine("done");
