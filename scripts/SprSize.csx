foreach (var nm in new[] { "sprAnyaFancyFont", "sprAnyaTypewriterFont" }) {
    var s = Data.Sprites.ByName(nm);
    var tp = s.Textures[0].Texture;
    var b = s.Textures[0].BoundingWidth;
    var bh = s.Textures[0].BoundingHeight;
    Console.WriteLine($"{nm}: frames={s.Textures.Count} tex={tp.SourceWidth}x{tp.SourceHeight} bound={b}x{bh} bbox=({s.Left},{s.Top},{s.Right},{s.Bottom})");
}
