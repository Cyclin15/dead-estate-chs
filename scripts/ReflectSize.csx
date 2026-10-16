using System;
using System.Text;
using System.Linq;
using System.Reflection;
var log = new StringBuilder();
var t = typeof(UndertaleModLib.Models.UndertaleInstruction);
foreach (var m in t.GetMethods(BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance | BindingFlags.Static))
    if (m.Name.ToLower().Contains("size") || m.Name.ToLower().Contains("address"))
        log.AppendLine(m.ToString());
foreach (var p in t.GetProperties())
    if (p.Name.ToLower().Contains("addr") || p.Name.ToLower().Contains("offset"))
        log.AppendLine("PROP " + p.ToString());
// also check static helpers on the code class
foreach (var m in typeof(UndertaleModLib.Models.UndertaleCode).GetMethods())
    if (m.Name.ToLower().Contains("addr") || m.Name.ToLower().Contains("size"))
        log.AppendLine("CODE " + m.ToString());
Console.WriteLine(log.ToString());
