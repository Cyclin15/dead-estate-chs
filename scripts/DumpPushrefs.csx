using System;
using System.Text;
using System.Linq;
using UndertaleModLib.Models;

var log = new StringBuilder();
var counts = new System.Collections.Generic.SortedDictionary<long, int>();
foreach (var code in Data.Code)
{
    var list = code.Instructions;
    for (int i = 0; i < list.Count; i++)
    {
        string s = list[i].ToString().Trim();
        if (s.StartsWith("pushref.i "))
        {
            long v = list[i].ValueInt;
            long hi = v >> 24;
            counts[hi] = counts.GetValueOrDefault(hi) + 1;
        }
    }
}
foreach (var kv in counts) log.AppendLine($"high byte 0x{kv.Key:X} ({kv.Key}): {kv.Value} pushrefs");

// find draw_set_font call sites and what feeds them
int n = 0;
foreach (var code in Data.Code)
{
    var list = code.Instructions;
    for (int i = 0; i < list.Count; i++)
    {
        var inst = list[i];
        if (inst.Kind == UndertaleInstruction.Opcode.Call && inst.ValueFunction != null &&
            (inst.ValueFunction.Name.Content == "draw_set_font"))
        {
            // print the 4 instructions before the call
            var ctx = string.Join(" | ", Enumerable.Range(Math.Max(0, i - 3), Math.Min(3, i) + 1).Select(j => list[j].ToString().Trim()));
            if (n < 25) log.AppendLine(code.Name.Content + ": " + ctx);
            n++;
        }
    }
}
log.AppendLine("draw_set_font sites: " + n);
Console.WriteLine(log.ToString());
