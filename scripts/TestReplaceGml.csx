using System;
using System.Text;
var log = new StringBuilder();
var code = Data.Code.ByName("gml_Object_game_Create_0");
log.AppendLine("code found: " + (code != null));
string gml = code.GetGMLCode();  // if ReplaceGml exists, GetGMLCode likely too
log.AppendLine("gml len: " + gml.Length);
// try replace the fancy line
string oldLine = "global.fntAnyaFancy = font_add_sprite_ext(sprAnyaFancyFont, \"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ?' \", true, 1);";
if (gml.Contains(oldLine))
{
    log.AppendLine("target line found");
    string newGml = gml.Replace(oldLine, "global.fntAnyaFancy = font_add_sprite_ext(sprAnyaFancyFont, \"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ?' \", true, 1);");
    // no-op replace; just testing API existence below
    try
    {
        code.ReplaceGml(newGml);
        log.AppendLine("ReplaceGml OK (no-op)");
    }
    catch (Exception e) { log.AppendLine("ReplaceGml FAILED: " + e.Message); }
}
else log.AppendLine("target line NOT found");
Console.WriteLine(log.ToString());
