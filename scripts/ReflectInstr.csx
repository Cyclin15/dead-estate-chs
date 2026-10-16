using System;
using System.Text;
using System.Linq;
using System.Reflection;
using UndertaleModLib.Models;

var code = Data.Code.First(c => c.Name.Content == "gml_Object_game_Create_0");
var inst = code.Instructions[6007];
var log = new StringBuilder();
log.AppendLine("== instr 6007: " + inst.ToString());
foreach (var f in typeof(UndertaleInstruction).GetFields(BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance))
{
    object fv = null;
    try { fv = f.GetValue(inst); } catch {}
    log.AppendLine("FIELD " + f.FieldType.Name + " " + f.Name + " = " + (fv == null ? "null" : fv.ToString()));
}
foreach (var p in typeof(UndertaleInstruction).GetProperties(BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance))
{
    object pv = null;
    try { pv = p.GetValue(inst); } catch {}
    log.AppendLine("PROP " + p.PropertyType.Name + " " + p.Name + " = " + (pv == null ? "null" : pv.ToString()));
}
var ft = Data.Fonts[0];
log.AppendLine("== font[0] " + ft.Name.Content + ": EmSize=" + ft.EmSize + " Bold=" + ft.Bold + " Italic=" + ft.Italic + " RangeStart=" + ft.RangeStart + " RangeEnd=" + ft.RangeEnd + " Charset=" + ft.Charset + " AA=" + ft.AntiAliasing + " ScaleX=" + ft.ScaleX + " ScaleY=" + ft.ScaleY + " Ascender=" + ft.Ascender + " SDFSpread=" + ft.SDFSpread + " LineHeight=" + ft.LineHeight + " AscenderOffset=" + ft.AscenderOffset);
log.AppendLine("font count: " + Data.Fonts.Count);
foreach (var fn in Data.Fonts.Take(6)) log.AppendLine("  font: " + fn.Name.Content);
Console.WriteLine(log.ToString());
