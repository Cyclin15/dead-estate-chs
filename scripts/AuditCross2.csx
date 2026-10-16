using System;
using System.Linq;
using System.Reflection;
using UndertaleModLib.Models;

var code = Data.Code.First(c => c.Name.Content == "gml_Object_game_Create_0");
var list = code.Instructions.ToList();
var addr = new uint[list.Count + 1];
var mi = typeof(UndertaleInstruction).GetMethod("CalculateInstructionSize", BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance);
for (int i = 0; i < list.Count; i++)
    addr[i+1] = addr[i] + (uint)mi.Invoke(list[i], null);
var boundaries = new System.Collections.Generic.HashSet<uint>(addr);

int onB = 0, offB = 0, n = 0;
foreach (var i in Enumerable.Range(0, list.Count))
{
    var inst = list[i];
    string s = inst.ToString().Trim();
    if (!(s.StartsWith("b ") || s.StartsWith("bt ") || s.StartsWith("bf "))) continue;
    bool magic = false;
    var pm = typeof(UndertaleInstruction).GetProperty("JumpOffsetPopenvExitMagic");
    try { magic = (bool)pm.GetValue(inst); } catch {}
    if (magic) continue;
    n++;
    uint tgt = addr[i] + (uint)inst.JumpOffset;
    if (boundaries.Contains(tgt)) onB++; else { offB++; Console.WriteLine("OFFBOUNDARY i=" + i + " addr=" + addr[i] + " off=" + inst.JumpOffset + " tgt=" + tgt); }
}
Console.WriteLine("branches=" + n + " on-boundary=" + onB + " off=" + offB);
