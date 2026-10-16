using System;
using System.Text;
using System.Linq;
using System.Reflection;
var log = new StringBuilder();
var code = Data.Code.ByName("gml_Object_game_Create_0");
var ins = code.Instructions[6007];
log.AppendLine("instr 6007: " + ins.ToString());
foreach (var p in ins.GetType().GetProperties())
{
    try { log.AppendLine($"  {p.Name} = {p.GetValue(ins)}"); }
    catch (Exception e) { log.AppendLine($"  {p.Name} = <{e.GetType().Name}>"); }
}
// how does UMT resolve asset refs: look at the instruction type for pushref
log.AppendLine("type: " + ins.GetType().Name);
var f = ins.GetType().GetFields(BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance);
foreach (var fl in f)
{
    try { log.AppendLine($"F {fl.Name} = {fl.GetValue(ins)}"); }
    catch (Exception e) { log.AppendLine($"F {fl.Name} = <err>"); }
}
Console.WriteLine(log.ToString());
