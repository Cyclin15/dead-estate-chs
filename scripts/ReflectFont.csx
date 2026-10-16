
using System;
using System.Text;
using System.Reflection;
var log = new StringBuilder();
var t = typeof(UndertaleModLib.Models.UndertaleFont);
foreach (var p in t.GetProperties())
    log.AppendLine(p.PropertyType.Name + " " + p.Name);
var s = typeof(UndertaleModLib.Models.UndertaleSprite);
foreach (var p in s.GetProperties())
    log.AppendLine("SPR " + p.PropertyType.Name + " " + p.Name);
Console.WriteLine(log.ToString());
