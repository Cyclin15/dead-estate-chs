using System;
using System.Text;
using System.Linq;
using System.Reflection;
using UndertaleModLib.Models;

var log = new StringBuilder();
var gt = typeof(UndertaleFont.Glyph);
log.AppendLine("Glyph fields:");
foreach (var f in gt.GetFields(BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance))
    log.AppendLine("  " + f.FieldType.Name + " " + f.Name);

var ft = typeof(UndertaleFont);
log.AppendLine("Font fields:");
foreach (var f in ft.GetFields(BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance))
    log.AppendLine("  " + f.FieldType.Name + " " + f.Name);

// compare original font vs new font glyph field values
foreach (int idx in new[] { 0, 13, 34, 35 })
{
    var f = Data.Fonts[idx];
    var g = f.Glyphs.First();
    var sb = new StringBuilder();
    foreach (var fl in gt.GetFields(BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance))
    {
        try { sb.Append(fl.Name + "=" + (fl.GetValue(g) ?? "null") + "; "); } catch {}
    }
    log.AppendLine($"font[{idx}] {f.Name.Content}: {sb}");
}
Console.WriteLine(log.ToString());
