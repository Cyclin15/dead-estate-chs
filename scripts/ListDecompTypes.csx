using System;
using System.Linq;
var t = typeof(UndertaleModLib.Decompiler.GlobalDecompileContext);
foreach (var p in t.GetProperties()) Console.WriteLine("P " + p.PropertyType.Name + " " + p.Name + " (set:" + p.CanWrite + ")");
foreach (var c in t.GetConstructors()) Console.WriteLine("C " + c);
