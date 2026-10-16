// Discover the public fields of a font glyph so the probe can point CJK glyphs at a
// separate texture page while Latin glyphs keep their vanilla page.
using System;
using System.IO;
using System.Text;
using UndertaleModLib;
using UndertaleModLib.Models;

var sb = new StringBuilder();
var f = Data.Fonts.ByName("fntGameFontNormal");
sb.AppendLine("UndertaleFont.Glyph fields:");
foreach (var fi in typeof(UndertaleFont.Glyph).GetFields())
    sb.AppendLine($"  field {fi.FieldType.Name} {fi.Name}");
foreach (var pi in typeof(UndertaleFont.Glyph).GetProperties())
    sb.AppendLine($"  prop  {pi.PropertyType.Name} {pi.Name}");

sb.AppendLine();
sb.AppendLine("UndertaleFont fields/props:");
foreach (var pi in typeof(UndertaleFont).GetProperties())
    sb.AppendLine($"  prop  {pi.PropertyType.Name} {pi.Name}");

File.WriteAllText(@"D:\Steam\steamapps\common\Dead Estate\_loc_work\dump\glyph_fields.txt", sb.ToString());
Console.WriteLine(sb.ToString());
