string baseDir = @"D:\Steam\steamapps\common\Dead Estate\_loc_work";
var idxs = new int[]{755,760,763,1055,1058,1063,4563,4565,9388,9407,9408,9409,9410,9411,9412,9413,9414,9415,9416,9417,9418,9419,9423,9446,9479,9689,9732,9806,9926,10078,10079,10457,10613,10899,8084};
var expect = new Dictionary<int,string>{
 {755,"Save amount"},{760,"Anya time"},{763,"Anya heals"},{1055,"Anya Additional Maximum HP Key"},{1058,"Anya Additional Speed Key"},{1063,"Anya Inventory Space Key"},{4563,"run start floor"},{4565,"challenge on"},{9388,"Anya HP Key"},{9407,"Cleared Intro"},{9408,"Got Jump Boots"},{9409,"Got Queens Key"},{9410,"Got Kings Key"},{9411,"Got Spring Emblem"},{9412,"Got Summer Emblem"},{9413,"Got Autumn Emblem"},{9414,"Got Winter Emblem"},{9415,"Got 8 Ball"},{9416,"Got All Emblems"},{9417,"Got 3 Emblems"},{9418,"Got 2 Emblems"},{9419,"Got 1 Emblem"},{9423,"Anya Area Name Key"},{9446,"let player use mirrors"},{9479,"Balloon Popped"},{9689,"Courtyard blocked"},{9732,"Encountered Cult Circle"},{9806,"Encountered Doppelganger"},{9926,"Cleared Anya campaign"},{10078,"Begun anya run"},{10079,"Escaped first chase"},{10457,"Rooms Swapped"},{10613,"Encountered Portrait Ghost"},{10899,"Encountered Trick Hall"},{8084,"gamepad discovered"}};
int ok = 0, bad = 0;
foreach (int i in idxs)
{
    var s = Data.Strings[i].Content;
    if (s == expect[i]) ok++; else { bad++; Console.WriteLine($"MISMATCH {i}: {s} != {expect[i]}"); }
}
Console.WriteLine($"reverted strings ok={ok} bad={bad}");
