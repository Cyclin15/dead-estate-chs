using System;
using System.Text;

var log = new StringBuilder();
log.AppendLine("== Options props ==");
foreach (var p in Data.Options.GetType().GetProperties())
{
    try { log.AppendLine("  " + p.Name + " = " + p.GetValue(Data.Options)); }
    catch { log.AppendLine("  " + p.Name + " = <err>"); }
}
foreach (var f in Data.Options.GetType().GetFields())
{
    try { log.AppendLine("  field " + f.Name + " = " + f.GetValue(Data.Options)); }
    catch { log.AppendLine("  field " + f.Name + " = <err>"); }
}

File.WriteAllText(@"D:\Steam\steamapps\common\Dead Estate\_loc_work\dump\options_dump.txt", log.ToString());
Console.WriteLine(log.ToString());
