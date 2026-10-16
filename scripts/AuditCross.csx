using System;
using System.Text;
using System.Linq;
using System.Reflection;
using UndertaleModLib.Models;

var code = Data.Code.First(c => c.Name.Content == "gml_Object_game_Create_0");
var list = code.Instructions.ToList();

var addr = new uint[list.Count + 1];
var mi = typeof(UndertaleInstruction).GetMethod("CalculateInstructionSize", BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance);
for (int i = 0; i < list.Count; i++)
    addr[i+1] = addr[i] + (uint)mi.Invoke(list[i], null);
Console.WriteLine("total bytes: " + addr[list.Count] + " (code.Length=" + code.Length + ")");

uint editStart = addr[6001];
uint editEnd   = addr[6019];
Console.WriteLine("edit region bytes: " + editStart + " .. " + editEnd);

var log = new StringBuilder();
int cross = 0, nbranch = 0;
for (int i = 0; i < list.Count; i++)
{
    var inst = list[i];
    string s = inst.ToString().Trim();
    bool isBranch = s.StartsWith("b ") || s.StartsWith("bt ") || s.StartsWith("bf ") || s.Contains("popenv");
    if (!isBranch) continue;
    nbranch++;
    bool popenvMagic = false;
    try { var pm = typeof(UndertaleInstruction).GetProperty("JumpOffsetPopenvExitMagic"); if (pm != null) popenvMagic = (bool)pm.GetValue(inst); } catch {}
    if (s.Contains("popenv") && popenvMagic) { log.AppendLine("note: popenv magic at i=" + i + " addr=" + addr[i]); continue; }
    int src = (int)addr[i];
    int tgt = src + inst.JumpOffset;
    bool straddle = (src < editStart && tgt >= editStart) || (src >= editEnd && tgt < editEnd);
    if (straddle) { cross++; log.AppendLine("CROSS: i=" + i + " addr=" + src + " s='" + s + "' off=" + inst.JumpOffset + " tgt=" + tgt); }
}
Console.WriteLine("branch-ish instrs: " + nbranch + ", straddling jumps: " + cross);
Console.Write(log.ToString());
for (int i = 5998; i <= 6020; i++)
    Console.WriteLine(addr[i] + " [" + i + "] " + list[i].ToString());
