string f = @"D:\Steam\steamapps\common\Dead Estate\data.win";
var bytes = File.ReadAllBytes(f);
Console.WriteLine($"game data.win bytes={bytes.Length}");
// check by loading: the CLI already loaded out file; just report a few indices of the CURRENT loaded data
int[] idxs = {9245, 1500, 8084, 10078, 755};
foreach (int i in idxs) Console.WriteLine($"{i}: {Data.Strings[i].Content.Replace("\n","\n")}");
