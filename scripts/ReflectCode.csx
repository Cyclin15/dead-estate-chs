using System;
using System.Text;
using System.Reflection;
var log = new StringBuilder();
foreach (var p in typeof(UndertaleModLib.Models.UndertaleCode).GetProperties())
    log.AppendLine("PROP " + p.PropertyType.Name + " " + p.Name);
foreach (var m in typeof(UndertaleModLib.Models.UndertaleCode).GetMethods())
    if (!m.IsSpecialName) log.AppendLine("M " + m.Name);
Console.WriteLine(log.ToString());
