using System;
using System.Reflection;
using System.Text;

var log = new StringBuilder();
log.AppendLine("== Data properties ==");
foreach (var p in Data.GetType().GetProperties())
    log.AppendLine("  " + p.Name + " : " + (p.PropertyType?.Name ?? "?"));

var gi = Data.GeneralInfo;
if (gi != null)
{
    log.AppendLine("== GeneralInfo properties ==");
    foreach (var p in gi.GetType().GetProperties())
    {
        try
        {
            object v = p.GetValue(gi);
            string vs = v == null ? "null" : v.ToString();
            if (v is System.Collections.IEnumerable && !(v is string)) vs = "(collection)";
            log.AppendLine("  " + p.Name + " = " + vs);
        }
        catch { log.AppendLine("  " + p.Name + " = <err>"); }
    }
}

// GEN8 flag bytes commonly hold interpolate; dump raw fields too
try
{
    var f = gi.GetType().GetField("Byte29", BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public);
    if (f != null) log.AppendLine("Byte29 = " + f.GetValue(gi));
}
catch { }

File.WriteAllText(@"D:\Steam\steamapps\common\Dead Estate\_loc_work\dump\gen8_info.txt", log.ToString());
Console.WriteLine(log.ToString());
