using System.Text;
using System.Globalization;
// full STRG audit: v3d must equal pristine everywhere except the translated map
Dictionary<int,string> ParseIdxJson(string json)
{
    var dict = new Dictionary<int,string>();
    int pos = 0;
    while (true)
    {
        int q1 = json.IndexOf('"', pos); if (q1 < 0) break;
        int q2 = json.IndexOf('"', q1 + 1); if (q2 < 0) break;
        string key = json.Substring(q1+1, q2-q1-1);
        int colon = json.IndexOf(':', q2);
        int v1 = json.IndexOf('"', colon+1); int v2 = v1+1;
        var sbv = new StringBuilder();
        while (v2 < json.Length)
        {
            char c = json[v2];
            char BS = (char)92;
            if (c == BS)
            {
                char e = json[v2+1];
                if (e == 'n') sbv.Append((char)10);
                else if (e == 'r') sbv.Append((char)13);
                else if (e == 't') sbv.Append((char)9);
                else if (e == '"') sbv.Append('"');
                else if (e == BS) sbv.Append(BS);
                else if (e == 'u') { sbv.Append((char)int.Parse(json.Substring(v2+2,4), NumberStyles.HexNumber)); v2 += 4; }
                else sbv.Append(e);
                v2 += 2; continue;
            }
            if (c == '"') break;
            sbv.Append(c); v2++;
        }
        if (int.TryParse(key, out int idx)) dict[idx] = sbv.ToString();
        pos = v2 + 1;
    }
    return dict;
}
string work = "D:/Steam/steamapps/common/Dead Estate/_loc_work";
var pristine = ParseIdxJson(File.ReadAllText(Path.Combine(work, "dump", "pristine_strings.json")));
var trans = ParseIdxJson(File.ReadAllText(Path.Combine(work, "dump", "translations.json")));
int n = Data.Strings.Count;
int diffs = 0, transOk = 0, unexpected = 0, missing = 0;
for (int i = 0; i < n && i < 30154; i++)
{
    string cur = Data.Strings[i].Content;
    if (trans.TryGetValue(i, out var tv))
    {
        if (cur == tv) transOk++; else { unexpected++; if (unexpected < 6) Console.WriteLine("TRANS-MISMATCH " + i + ": " + cur.Substring(0,Math.Min(30,cur.Length)) + " != " + tv.Substring(0,Math.Min(30,tv.Length))); }
    }
    else
    {
        if (pristine.TryGetValue(i, out var pv))
        {
            if (cur != pv) { diffs++; if (diffs < 6) Console.WriteLine("UNEXPECTED-DIFF " + i + ": " + cur.Substring(0,Math.Min(40,cur.Length)) + " != " + pv.Substring(0,Math.Min(40,pv.Length))); }
        }
        else missing++;
    }
}
Console.WriteLine("STRG audit: n=" + n + " transOk=" + transOk + " unexpectedTrans=" + unexpected + " unexpectedDiff=" + diffs + " missingPristine=" + missing);
