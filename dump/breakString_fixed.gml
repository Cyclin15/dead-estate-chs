function breakString(arg0, arg1)
{
    var _stringWidth = 0;
    for (var q = 0; q <= string_length(arg0); q++)
    {
        var _currentChar = string_char_at(arg0, q);
        var _prevChar = string_char_at(arg0, q - 1);
        if (string_copy(arg0, q, 2) != "♦/")
        {
            _stringWidth += string_width(_currentChar);
            if (_stringWidth >= arg1)
            {
                var _searchIndex = q;
                _stringWidth = 0;
                if (string_pos(" ", string_copy(arg0, 1, q)))
                {
                    while (_currentChar != " " && _searchIndex > 1)
                    {
                        _searchIndex--;
                        _currentChar = string_char_at(arg0, _searchIndex);
                        if (_currentChar != "♦" && _prevChar != "♦")
                        {
                            _stringWidth += string_width(_currentChar);
                        }
                        if ((_prevChar + _currentChar) == "♦/")
                        {
                            _stringWidth = 0;
                        }
                    }
                }
                if (_currentChar == " ")
                {
                    arg0 = string_delete(arg0, _searchIndex, 1);
                }
                arg0 = string_insert("♦/", arg0, _searchIndex);
            }
        }
        else if (string_copy(arg0, q, 2) == "♦/")
        {
            _stringWidth = 0;
        }
    }
    return arg0;
}
