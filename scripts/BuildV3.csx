// V3 assembly (freeze fix):
//   1. install Chinese strings from dump/translations.json
//   2. install fontfinal2 fonts (34, logical size, Scale=1)          [as v2]
//   3. NEW regular fonts fntAnyaFancyCN / fntAnyaTypewriterCN built from the
//      original sprite frames (byte-exact Latin) + CJK fusion ink (out/v3fonts)
//   4. patch gml_Object_game_Create_0: replace the two font_add_sprite_ext calls
//      for sprAnyaFancyFont / sprAnyaTypewriterFont with pushref of the new font
//      assets (0x6000000|fontIndex). Extended charmaps in font_add_sprite_ext
//      caused the Anya title freeze; regular font assets with 2100+ glyphs are
//      proven fast (the 34 rebuilt fonts). DigitalDisplay stays a sprite font
//      (digits only), AnyaReview is unused in code.
// Runs against the ORIGINAL backup data.win.
using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Text;
using UndertaleModLib;
using UndertaleModLib.Models;

string work = @"D:\Steam\steamapps\common\Dead Estate\_loc_work";
var log = new StringBuilder();

UndertaleString GetOrAddString(string s)
{
    foreach (var st in Data.Strings)
        if (st.Content == s) return st;
    var ns = new UndertaleString(s);
    Data.Strings.Add(ns);
    return ns;
}

// ------------------------------------------------------------------ 1. strings
// out/data.win's STRG was contaminated by an early in-place build save, so first
// reset EVERY string to the pristine session-1 dump, then overlay the translations.
Dictionary<int, string> ParseIdxJson(string json)
{
    var dict = new Dictionary<int, string>();
    int pos = 0;
    while (true)
    {
        int q1 = json.IndexOf('"', pos);
        if (q1 < 0) break;
        int q2 = json.IndexOf('"', q1 + 1);
        if (q2 < 0) break;
        string key = json.Substring(q1 + 1, q2 - q1 - 1);
        int colon = json.IndexOf(':', q2);
        int v1 = json.IndexOf('"', colon + 1);
        int v2 = v1 + 1;
        var sbv = new StringBuilder();
        while (v2 < json.Length)
        {
            char c = json[v2];
            if (c == '\\')
            {
                char e = json[v2 + 1];
                switch (e)
                {
                    case 'n': sbv.Append('\n'); break;
                    case 'r': sbv.Append('\r'); break;
                    case 't': sbv.Append('\t'); break;
                    case '"': sbv.Append('"'); break;
                    case '\\': sbv.Append('\\'); break;
                    case 'u':
                        int code = int.Parse(json.Substring(v2 + 2, 4), NumberStyles.HexNumber, CultureInfo.InvariantCulture);
                        sbv.Append((char)code);
                        v2 += 4;
                        break;
                    default: sbv.Append(e); break;
                }
                v2 += 2;
                continue;
            }
            if (c == '"') break;
            sbv.Append(c);
            v2++;
        }
        if (int.TryParse(key, out int idx)) dict[idx] = sbv.ToString();
        pos = v2 + 1;
    }
    return dict;
}

var pristine = ParseIdxJson(File.ReadAllText(Path.Combine(work, "dump", "pristine_strings.json")));
int reset = 0;
foreach (var kv in pristine)
    if (kv.Key >= 0 && kv.Key < Data.Strings.Count) { Data.Strings[kv.Key].Content = kv.Value; reset++; }
log.AppendLine($"strings reset to pristine: {reset}/{pristine.Count}");

var trans = ParseIdxJson(File.ReadAllText(Path.Combine(work, "dump", "translations.json")));

// STRG entries double as function/variable names (FUNK/VARI reference them by index);
// translating those breaks name resolution at load ("Unable to find function ...").
var protectedIdx = new HashSet<int>();
foreach (var f in Data.Functions) protectedIdx.Add(Data.Strings.IndexOf(f.Name));
foreach (var v in Data.Variables) protectedIdx.Add(Data.Strings.IndexOf(v.Name));
protectedIdx.Remove(-1);
var collided = trans.Keys.Where(k => protectedIdx.Contains(k)).ToList();
if (collided.Count > 0)
{
    foreach (int k in collided)
        log.AppendLine($"REFUSING name-collision translation {k}: {Data.Strings[k].Content}");
    throw new Exception($"{collided.Count} translations collide with function/variable names — remove them from translations.json");
}

int replaced = 0;
foreach (var kv in trans)
    if (kv.Key >= 0 && kv.Key < Data.Strings.Count) { Data.Strings[kv.Key].Content = kv.Value; replaced++; }
log.AppendLine($"strings replaced: {replaced}/{trans.Count}");

// ------------------------------------------------------------------ 2. fontfinal2 fonts
string byName = Path.Combine(work, "fontfinal2");
int fontsDone = 0, glyphsAdded = 0;
foreach (string fontDir in Directory.GetDirectories(byName))
{
    string fontName = Path.GetFileName(fontDir);
    string csvPath = Path.Combine(fontDir, $"glyphs_{fontName}.csv");
    if (!File.Exists(csvPath)) continue;
    var font = Data.Fonts.ByName(fontName);
    if (font == null) { log.AppendLine($"SKIP {fontName}: not in data.win"); continue; }

    var pages = new Dictionary<int, UndertaleTexturePageItem>();
    foreach (string png in Directory.GetFiles(fontDir, "*.png"))
    {
        string bn = Path.GetFileNameWithoutExtension(png);
        int sheet = 0;
        int us = bn.LastIndexOf('_');
        if (us > 0) int.TryParse(bn[(us + 1)..], NumberStyles.Integer, CultureInfo.InvariantCulture, out sheet);

        var tex = new UndertaleEmbeddedTexture();
        tex.Name = new UndertaleString($"DEf2_{fontName}_{sheet}");
        tex.TextureData.Image = UndertaleModLib.Util.GMImage.FromPng(File.ReadAllBytes(png));
        Data.EmbeddedTextures.Add(tex);

        var tpi = new UndertaleTexturePageItem();
        tpi.Name = new UndertaleString($"DEf2page_{fontName}_{sheet}");
        tpi.SourceX = 0; tpi.SourceY = 0;
        tpi.SourceWidth = (ushort)tex.TextureData.Image.Width;
        tpi.SourceHeight = (ushort)tex.TextureData.Image.Height;
        tpi.TargetX = 0; tpi.TargetY = 0;
        tpi.TargetWidth = (ushort)tex.TextureData.Image.Width;
        tpi.TargetHeight = (ushort)tex.TextureData.Image.Height;
        tpi.BoundingWidth = (ushort)tex.TextureData.Image.Width;
        tpi.BoundingHeight = (ushort)tex.TextureData.Image.Height;
        tpi.TexturePage = tex;
        Data.TexturePageItems.Add(tpi);
        pages[sheet] = tpi;
    }

    var glyphs = new List<UndertaleFont.Glyph>();
    int head = 0, cjk = 0;
    double headerScale = 1;
    foreach (string raw in File.ReadLines(csvPath))
    {
        if (string.IsNullOrWhiteSpace(raw)) continue;
        string[] s = raw.Split(';');
        if (head == 0)
        {
            if (s.Length >= 8)
                double.TryParse(s[6], NumberStyles.Float, CultureInfo.InvariantCulture, out headerScale);
            head++;
            continue;
        }
        if (s.Length < 7) continue;
        var g = new UndertaleFont.Glyph();
        g.Character = ushort.Parse(s[0], CultureInfo.InvariantCulture);
        g.SourceX = ushort.Parse(s[1], CultureInfo.InvariantCulture);
        g.SourceY = ushort.Parse(s[2], CultureInfo.InvariantCulture);
        g.SourceWidth = ushort.Parse(s[3], CultureInfo.InvariantCulture);
        g.SourceHeight = ushort.Parse(s[4], CultureInfo.InvariantCulture);
        g.Shift = short.Parse(s[5], CultureInfo.InvariantCulture);
        g.Offset = short.Parse(s[6], CultureInfo.InvariantCulture);
        glyphs.Add(g);
        if (g.Character > 127) cjk++;
    }

    font.Glyphs.Clear();
    foreach (var g in glyphs) font.Glyphs.Add(g);
    if (pages.ContainsKey(0)) font.Texture = pages[0];
    font.ScaleX = (float)headerScale;
    font.ScaleY = (float)headerScale;

    fontsDone++;
    glyphsAdded += cjk;
}
log.AppendLine($"fonts: {fontsDone} rebuilt, {glyphsAdded} CJK glyphs");

// ------------------------------------------------------------------ 3. new fonts
// out/v3fonts/<name>/{sheet0.png, glyphs.csv}  (CSV: header;char;srcX;srcY;srcW;srcH;Shift;Offset)
var newFontIds = new Dictionary<string, int>();
foreach (string name in new[] { "fntAnyaFancyCN", "fntAnyaTypewriterCN" })
{
    string dir = Path.Combine(work, "out", "v3fonts", name);
    var tex = new UndertaleEmbeddedTexture();
    tex.Name = GetOrAddString($"DEv3_{name}");
    tex.TextureData.Image = UndertaleModLib.Util.GMImage.FromPng(File.ReadAllBytes(Path.Combine(dir, "sheet0.png")));
    Data.EmbeddedTextures.Add(tex);
    var tpi = new UndertaleTexturePageItem();
    tpi.Name = GetOrAddString($"DEv3page_{name}");
    tpi.SourceX = 0; tpi.SourceY = 0;
    tpi.SourceWidth = (ushort)tex.TextureData.Image.Width;
    tpi.SourceHeight = (ushort)tex.TextureData.Image.Height;
    tpi.TargetX = 0; tpi.TargetY = 0;
    tpi.TargetWidth = (ushort)tex.TextureData.Image.Width;
    tpi.TargetHeight = (ushort)tex.TextureData.Image.Height;
    tpi.BoundingWidth = (ushort)tex.TextureData.Image.Width;
    tpi.BoundingHeight = (ushort)tex.TextureData.Image.Height;
    tpi.TexturePage = tex;
    Data.TexturePageItems.Add(tpi);

    var font = new UndertaleFont();
    font.Name = GetOrAddString(name);
    font.DisplayName = GetOrAddString(name);
    int emSize = 16; short cjkShift = 16;
    if (name == "fntAnyaTypewriterCN") { emSize = 9; cjkShift = 11; }
    font.EmSize = emSize;
    font.Bold = false; font.Italic = false;
    font.RangeStart = 32; font.RangeEnd = 9647;
    font.Charset = 0; font.AntiAliasing = 1;
    font.ScaleX = 1f; font.ScaleY = 1f;
    font.Ascender = 0; font.LineHeight = 0; font.AscenderOffset = 0;
    font.SDFSpread = 0;
    font.Texture = tpi;
    font.Glyphs = new UndertalePointerList<UndertaleFont.Glyph>();

    int ng = 0, latin = 0;
    foreach (string raw in File.ReadLines(Path.Combine(dir, "glyphs.csv")))
    {
        if (string.IsNullOrWhiteSpace(raw)) continue;
        string[] s = raw.Split(';');
        if (s[0] == name) continue; // header line
        if (s.Length < 7) continue;
        var g = new UndertaleFont.Glyph();
        g.Character = ushort.Parse(s[0], CultureInfo.InvariantCulture);
        g.SourceX = ushort.Parse(s[1], CultureInfo.InvariantCulture);
        g.SourceY = ushort.Parse(s[2], CultureInfo.InvariantCulture);
        g.SourceWidth = ushort.Parse(s[3], CultureInfo.InvariantCulture);
        g.SourceHeight = ushort.Parse(s[4], CultureInfo.InvariantCulture);
        g.Shift = short.Parse(s[5], CultureInfo.InvariantCulture);
        g.Offset = short.Parse(s[6], CultureInfo.InvariantCulture);
        font.Glyphs.Add(g);
        ng++; if (g.Character < 128) latin++;
    }
    int fontIndex = Data.Fonts.Count;
    Data.Fonts.Add(font);
    newFontIds[name] = fontIndex;
    log.AppendLine($"new font {name}: index {fontIndex}, {ng} glyphs ({latin} latin), texture {tex.TextureData.Image.Width}x{tex.TextureData.Image.Height}");
}

// ------------------------------------------------------------------ 4. bytecode patch
// Replace the two font_add_sprite_ext calls (fancy/typewriter; the runtime
// sprite-font path freezes with extended charmaps) with static font pushrefs
// to the new regular font assets (0x6000000|fontIndex).
// CRITICAL: gml_Object_game_Create_0 has 9 child code entries (anonymous
// script methods) that share its bytecode via an absolute byte Offset field.
// The splice shifts instructions, so every child Offset must be re-derived
// from the identity of its entry instruction. UMT does NOT do this itself.
bool doPatch = (Environment.GetEnvironmentVariable("DO_PATCH") ?? "1") != "0";
bool patchToExisting = (Environment.GetEnvironmentVariable("PATCH_TO_EXISTING") ?? "0") == "1";
string outName = Environment.GetEnvironmentVariable("OUTNAME") ?? "data_v3.win";
var code = Data.Code.First(c => c.Name.Content == "gml_Object_game_Create_0");
var list = code.Instructions.ToList();
var cloneMethod = typeof(UndertaleInstruction).GetMethod("MemberwiseClone", BindingFlags.NonPublic | BindingFlags.Instance);

// serialized instruction size, in 4-byte words (VM address units)
var sizeM = typeof(UndertaleInstruction).GetMethod("CalculateInstructionSize",
    BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance);
if (sizeM is null) { Console.WriteLine("CalculateInstructionSize not found"); Console.WriteLine(log.ToString()); return; }
Func<UndertaleInstruction, int> WSz = ins => (int)(uint)sizeM.Invoke(ins, null);
var oldCum = new long[list.Count + 1];
for (int i = 0; i < list.Count; i++) oldCum[i + 1] = oldCum[i] + WSz(list[i]);
if (oldCum[list.Count] * 4 != (long)code.Length)
{ Console.WriteLine($"SIZE MISMATCH: {oldCum[list.Count]} words vs Length {code.Length}"); Console.WriteLine(log.ToString()); return; }

// locate the two target call sites: call font_add_sprite_ext preceded by pushref of the sprite
var callIdx = new List<int>();
for (int i = 0; i < list.Count; i++)
{
    var inst = list[i];
    if (inst.Kind == UndertaleInstruction.Opcode.Call && inst.ValueFunction != null && inst.ValueFunction.Name.Content == "font_add_sprite_ext")
    {
        int refVal = list[i - 1].ValueInt;
        callIdx.Add(i);
        log.AppendLine($"call site [{i}] word {oldCum[i]} sprite pushref {refVal}");
    }
}
if (callIdx.Count != 3) { Console.WriteLine("UNEXPECTED call count: " + callIdx.Count); Console.WriteLine(log.ToString()); return; }

int fancyId = patchToExisting ? 13 : newFontIds["fntAnyaFancyCN"];
int twId    = patchToExisting ? 13 : newFontIds["fntAnyaTypewriterCN"];
var pr1 = (UndertaleInstruction)cloneMethod.Invoke(list[callIdx[0] - 1], null);
pr1.ValueInt = 0x6000000 | fancyId;
var pr2 = (UndertaleInstruction)cloneMethod.Invoke(list[callIdx[1] - 1], null);
pr2.ValueInt = 0x6000000 | twId;

int s1 = callIdx[0] - 7, c1 = callIdx[0];   // replace [s1..c1] with pr1
int s2 = callIdx[1] - 7, c2 = callIdx[1];   // replace [s2..c2] with pr2
// sanity: the site we patch must be fancy(681)/typewriter(1012) in that order
if (list[callIdx[0] - 1].ValueInt != 0x1000000 + 681 || list[callIdx[1] - 1].ValueInt != 0x1000000 + 1012)
{ Console.WriteLine("SANITY FAIL: sprite refs not in expected order"); Console.WriteLine(log.ToString()); return; }

// branch audit: branch targets are srcWord + JumpOffset (words). No branch span
// may intersect an edit span, otherwise unadjusted JumpOffsets would break.
long[] editLo = { oldCum[s1], oldCum[s2] };
long[] editHi = { oldCum[c1 + 1], oldCum[c2 + 1] };
int crossings = 0;
for (int i = 0; i < list.Count; i++)
{
    var k = list[i].Kind;
    if (k != UndertaleInstruction.Opcode.B && k != UndertaleInstruction.Opcode.Bt &&
        k != UndertaleInstruction.Opcode.Bf && k != UndertaleInstruction.Opcode.PushEnv &&
        k != UndertaleInstruction.Opcode.PopEnv) continue;
    if (list[i].JumpOffsetPopenvExitMagic) continue;
    long src = oldCum[i];
    long dst = src + list[i].JumpOffset;
    long lo = Math.Min(src, dst), hi = Math.Max(src, dst);
    for (int e = 0; e < 2; e++)
        if (lo < editHi[e] && hi >= editLo[e])
        {
            crossings++;
            log.AppendLine($"  BRANCH CROSSES edit {e}: [{i}] word {src} -> {dst} (edit [{editLo[e]},{editHi[e]})");
        }
}
if (crossings != 0) { Console.WriteLine($"BRANCH AUDIT FAILED: {crossings} crossings"); Console.WriteLine(log.ToString()); return; }
log.AppendLine($"branch audit: 0 crossings over edits [{editLo[0]},{editHi[0]}) [{editLo[1]},{editHi[1]})");

if (doPatch)
{
    // splice, keeping an old-index -> new-index map for the child offset fixup
    var newList = new List<UndertaleInstruction>(list.Count - 14);
    var idxMap = new Dictionary<int, int>();
    for (int k = 0; k < list.Count; k++)
    {
        if (k == s1 || k == s2)
        {
            idxMap[k] = newList.Count;
            newList.Add(k == s1 ? pr1 : pr2);
        }
        else if ((k > s1 && k <= c1) || (k > s2 && k <= c2))
        {
            // removed argument/call instructions
        }
        else
        {
            idxMap[k] = newList.Count;
            newList.Add(list[k]);
        }
    }
    code.Replace(newList);

    // re-derive child entry Offsets: child.Offset (bytes) pointed at a word
    // boundary in the OLD layout; remap via instruction identity.
    var newInstrs = code.Instructions;
    var newCum = new long[newInstrs.Count + 1];
    for (int i = 0; i < newInstrs.Count; i++) newCum[i + 1] = newCum[i] + WSz(newInstrs[i]);
    log.AppendLine($"new bytecode: {newInstrs.Count} instrs, {newCum[newInstrs.Count]} words ({newCum[newInstrs.Count] * 4} bytes; old {code.Length})");
    var posToIdx = new Dictionary<long, int>();
    for (int i = 0; i < list.Count; i++) posToIdx[oldCum[i]] = i;
    foreach (var child in code.ChildEntries)
    {
        if (child.Offset % 4 != 0 || !posToIdx.TryGetValue(child.Offset / 4, out int k))
        { Console.WriteLine($"CHILD OFFSET not on an old instruction boundary: {child.Name?.Content} {child.Offset}"); Console.WriteLine(log.ToString()); return; }
        if (!idxMap.TryGetValue(k, out int nk))
        { Console.WriteLine($"CHILD entry instruction was removed by the splice: {child.Name?.Content}"); Console.WriteLine(log.ToString()); return; }
        uint newOff = (uint)(newCum[nk] * 4);
        if (newOff != child.Offset)
            log.AppendLine($"child {child.Name?.Content}: Offset {child.Offset} -> {newOff}");
        child.Offset = newOff;
    }
    log.AppendLine($"patched gml_Object_game_Create_0: {list.Count} -> {newInstrs.Count} instrs ({newCum[newInstrs.Count] * 4} bytes), pushref fonts {pr1.ValueInt}/{pr2.ValueInt}, children fixed: {code.ChildEntries.Count}");
}
else
{
    log.AppendLine("patch SKIPPED (DO_PATCH=0)");
}
// dump patched region for the log
if (doPatch)
{
    var li = code.Instructions.ToList();
    int p = li.IndexOf(pr1);
    for (int i = p - 1; i <= p + 7; i++)
        log.AppendLine("  " + li[i].ToString());
}

// ------------------------------------------------------------------ 4b. breakString fix
// breakString (in gml_GlobalScript_scrStrings) searches backward for a space when
// a line overflows the wrap width; if the string's only spaces lie AFTER the
// overflow point (e.g. "1 HP" embedded in a CJK description), the search falls
// through to position 1 and a line break is inserted after the first character,
// again and again — text height explodes and item description boxes render off
// screen. Fix: only search for a space in the text BEFORE the overflow point
// (string_pos(" ", string_copy(arg0, 1, q))); otherwise break at the overflow
// character (correct CJK behavior). Verified: recompiled bytecode round-trips to
// the identical decompiled GML, and the " " literal reuses string index 1644.
bool doBreakFix = (Environment.GetEnvironmentVariable("DO_BREAKFIX") ?? "1") != "0";
if (doBreakFix)
{
    var rootScr = Data.Code.First(c => c.Name.Content == "gml_GlobalScript_scrStrings");
    var gctx2 = new UndertaleModLib.Decompiler.GlobalDecompileContext(Data);
    var group2 = new UndertaleModLib.Compiler.CompileGroup(Data, gctx2) { MainThreadAction = MainThreadAction };
    group2.PersistLinkingLookups = true;
    string fixedGml = File.ReadAllText(Path.Combine(work, "dump", "scrStrings_fixed.gml"), Encoding.UTF8);
    group2.QueueCodeReplace(rootScr, fixedGml);
    var res = group2.Compile();
    if (!res.Successful)
    {
        Console.WriteLine("breakString fix FAILED to compile:");
        foreach (var e in res.Errors ?? Array.Empty<UndertaleModLib.Compiler.CompileError>())
            Console.WriteLine("  " + e);
        Console.WriteLine(log.ToString());
        return;
    }
    log.AppendLine($"breakString fix: recompiled gml_GlobalScript_scrStrings ({rootScr.Length} bytes, {rootScr.ChildEntries.Count} children)");
}
else
{
    log.AppendLine("breakString fix SKIPPED (DO_BREAKFIX=0)");
}

// ------------------------------------------------------------------ 5. write
string outDir = Path.Combine(work, "out");
Directory.CreateDirectory(outDir);
string outFile = Path.Combine(outDir, outName);
using (var fs = File.Create(outFile)) UndertaleIO.Write(fs, Data);
log.AppendLine($"wrote {outFile} ({new FileInfo(outFile).Length} bytes)");

File.WriteAllText(Path.Combine(work, "dump", "build_v3.txt"), log.ToString());
Console.WriteLine(log.ToString());
