function newProcessString(arg0, arg1 = 9999, arg2 = draw_get_font(), arg3 = true)
{
    var ogFont = draw_get_font();
    draw_set_font(arg2);
    arg0 = breakString(arg0, arg1);
    draw_set_font(ogFont);
    var pa = new TextPieceArray();
    var effectsArray = [];
    var index = 0;
    pa.rawString = arg0;
    while (string_length(arg0) > 0)
    {
        var i = 1;
        while (string_char_at(arg0, i + 1) != "♦" && i < string_length(arg0))
        {
            i++;
        }
        var copyText = string_copy(arg0, 1, i);
        var piece = new TextPiece(copyText, []);
        pa.addTextPiece(piece);
        arg0 = string_delete(arg0, 1, i);
        index++;
    }
    for (var i = 0; i < pa.length; i++)
    {
        var pc = pa.array[i];
        if (string_char_at(pc.text, 1) == "♦")
        {
            var ch = string_copy(pc.text, 1, 2);
            switch (ch)
            {
                case "♦r":
                    effectsArray = [new TEReset()];
                    break;
                case "♦/":
                    break;
                case "♦w":
                    array_push(effectsArray, new TEWave());
                    break;
                case "♦s":
                    array_push(effectsArray, new TEShake());
                    break;
                case "♦b":
                    array_push(effectsArray, new TEBold());
                    break;
                case "♦i":
                    array_push(effectsArray, new TEItalics());
                    break;
                case "♦k":
                    array_push(effectsArray, new TEButton());
                    break;
                case "♦`":
                    array_push(effectsArray, new TCRainbow());
                    break;
                case "♦0":
                    array_push(effectsArray, new TCRed());
                    break;
                case "♦1":
                    array_push(effectsArray, new TCOrange());
                    break;
                case "♦2":
                    array_push(effectsArray, new TCYellow());
                    break;
                case "♦3":
                    array_push(effectsArray, new TCGreen());
                    break;
                case "♦4":
                    array_push(effectsArray, new TCAqua());
                    break;
                case "♦5":
                    array_push(effectsArray, new TCBlue());
                    break;
                case "♦6":
                    array_push(effectsArray, new TCViolet());
                    break;
                case "♦7":
                    array_push(effectsArray, new TCWhite());
                    break;
                case "♦8":
                    array_push(effectsArray, new TCGray());
                    break;
                case "♦9":
                    array_push(effectsArray, new TCBlack());
                    break;
            }
            if (array_length(effectsArray) > 0)
            {
                with (effectsArray[array_length(effectsArray) - 1])
                {
                    parentPiece = pc;
                    parentArray = pa;
                }
            }
            array_copy(pc.effectsArray, 0, effectsArray, 0, array_length(effectsArray));
            if (ch == "♦/")
            {
                pc.hasLineBreak = true;
                array_push(pc.effectsArray, new TELineBreak());
            }
            var j = array_length(effectsArray) - 1;
            while (j >= 0)
            {
                if (is_instanceof(effectsArray[j], TELineBreak))
                {
                    array_delete(effectsArray, j, 1);
                }
                if (is_instanceof(effectsArray[j], TEBold))
                {
                    pc.isBold = true;
                }
                if (is_instanceof(effectsArray[j], TEItalics))
                {
                    pc.isItalics = true;
                }
                j--;
            }
            pc.text = string_delete(pc.text, 1, 2);
        }
    }
    pa.persistent = arg3;
    return pa;
}

function TextPieceArray() constructor
{
    array = [];
    length = 0;
    remove = false;
    copy = 9999;
    listIndex = -1;
    rawString = "";
    animated = false;
    updatedEffects = false;
    persistent = false;
    if (!instance_exists(oTextPieceManager))
    {
        instance_create_depth(0, 0, 0, oTextPieceManager);
    }
    with (oTextPieceManager)
    {
        if (ds_list_find_index(list, other) < 0)
        {
            ds_list_add(list, other);
        }
        other.listIndex = ds_list_find_index(list, other);
    }
    
    addTextPiece = function(arg0)
    {
        array_push(array, arg0);
        arg0.owner = self;
        setLength();
        setPieceBeginnings();
        checkAnimated();
    };
    
    insertTextPiece = function(arg0, arg1)
    {
        array_insert(array, arg1, arg0);
        setLength();
        setPieceBeginnings();
    };
    
    deleteTextPiece = function(arg0)
    {
        array[arg0] = undefined;
        array_delete(array, arg0, 1);
        setLength();
        checkAnimated();
    };
    
    setLength = function()
    {
        length = array_length(array);
    };
    
    setPieceBeginnings = function()
    {
        var n = 1;
        for (var i = 0; i < array_length(array); i++)
        {
            array[i].beginIndex = n;
            n += string_length(array[i].text);
        }
    };
    
    checkAnimated = function()
    {
        animated = false;
        for (var i = 0; i < length; i++)
        {
            with (array[i])
            {
                if (hasEffect(TEWave) || hasEffect(TEShake) || hasEffect(TCRainbow))
                {
                    other.animated = true;
                    break;
                }
            }
        }
        return animated;
    };
    
    destroy = function()
    {
        remove = true;
        for (var i = 0; i < length; i++)
        {
            deleteTextPiece(i);
        }
    };
}

function TextPiece(arg0, arg1) constructor
{
    self.text = arg0;
    self.effectsArray = arg1;
    x = 0;
    y = 0;
    width = 0;
    height = 0;
    breakLine = false;
    hasLineBreak = false;
    isBold = false;
    isItalics = false;
    beginIndex = 1;
    copy = 9999;
    xScale = 1;
    yScale = 1;
    angle = 0;
    owner = -4;
    visible = true;
    offY = 0;
    
    drawText = function()
    {
        if (visible)
        {
            draw_text_transformed(x, y, string_copy(text, 1, copy), xScale, yScale, angle);
        }
        width += (string_width(text) * xScale);
        height += (string_height(text) * yScale);
    };
    
    hasEffect = function(arg0)
    {
        for (var i = 0; i < array_length(effectsArray); i++)
        {
            if (is_instanceof(effectsArray[i], arg0))
            {
                return true;
            }
        }
        return false;
    };
    
    addEffect = function(arg0)
    {
        array_push(effectsArray, new arg0());
        if (!isBold && arg0 == TEBold)
        {
            isBold = true;
        }
        if (!isItalics && arg0 == TEItalics)
        {
            isItalics = true;
        }
        with (owner)
        {
            updatedEffects = true;
        }
    };
    
    removeEffect = function(arg0)
    {
        var i = array_length(effectsArray) - 1;
        while (i >= 0)
        {
            if (is_instanceof(effectsArray[i], arg0))
            {
                array_delete(effectsArray, i, 1);
                effectsArray[i] = undefined;
            }
            i--;
        }
        if (isBold && arg0 == TEBold)
        {
            isBold = false;
        }
        if (isItalics && arg0 == TEItalics)
        {
            isItalics = false;
        }
        with (owner)
        {
            updatedEffects = true;
        }
    };
    
    draw = function()
    {
        width = 0;
        height = 0;
        offY = 0;
        for (var i = 0; i < array_length(effectsArray); i++)
        {
            if (is_struct(effectsArray[i]))
            {
                effectsArray[i].modify(self);
            }
        }
        drawText();
    };
}

function TextEffect() constructor
{
    parentPiece = -4;
    parentArray = -4;
    
    modify = function(arg0)
    {
    };
    
    createFunction = function()
    {
    };
    
    destroyFunction = function()
    {
    };
}

function TEReset() : TextEffect() constructor
{
}

function TELineBreak() : TextEffect() constructor
{
    modify = function(arg0)
    {
        with (arg0)
        {
            breakLine = true;
        }
    };
}

function TEWave() : TextEffect() constructor
{
    modify = function(arg0)
    {
        with (arg0)
        {
            drawText = function()
            {
                var tx = x;
                var ty = y;
                for (var i = 1; i <= min(copy, string_length(text)); i++)
                {
                    var ch = string_char_at(text, i);
                    if (visible)
                    {
                        draw_text_transformed(tx, ty + floor(wave(-2, 1, 1, beginIndex + (i * 0.15))), ch, xScale, yScale, angle);
                    }
                    var chw = string_width(ch) * xScale;
                    tx += chw;
                    width += chw;
                }
                height = max(height, string_height(text) * yScale);
            };
        }
    };
}

function TEShake() : TextEffect() constructor
{
    modify = function(arg0)
    {
        with (arg0)
        {
            drawText = function()
            {
                var tx = x;
                var ty = y;
                for (var i = 1; i <= min(copy, string_length(text)); i++)
                {
                    var ch = string_char_at(text, i);
                    if (visible)
                    {
                        draw_text_transformed(tx + irandom_range(-1, 1), ty + irandom_range(-1, 1), ch, xScale, yScale, angle);
                    }
                    var chw = string_width(ch) * xScale;
                    tx += chw;
                    width += chw;
                }
                height += (string_height(text) * yScale);
            };
        }
    };
}

function TEBold() : TextEffect() constructor
{
}

function TEItalics() : TextEffect() constructor
{
}

function TEButton() : TextEffect() constructor
{
    modify = function(arg0)
    {
        with (arg0)
        {
            drawText = function()
            {
                var spr = global.controlMode ? sprButtonInput : sprKeyInput;
                var cstr = string_copy(text, 1, copy);
                var p = string_width(" ");
                var xo = 4;
                if (visible)
                {
                    if (variable_global_exists(cstr))
                    {
                        var v = variable_global_get(cstr);
                        var vin = v;
                        if (is_array(v))
                        {
                            vin = v[0];
                        }
                        var a = drawInputPrompt(x + p, y, vin);
                        xo = a[0];
                        height = max(height, a[1]);
                        width += xo;
                        offY = a[2];
                    }
                    else
                    {
                        var a = drawInputPrompt(x + p, y, cstr);
                        xo = a[0];
                        height = max(height, a[1]);
                        width += xo;
                        offY = a[2];
                    }
                }
                else if (variable_global_exists(cstr))
                {
                    var v = variable_global_get(cstr);
                    var vin = v;
                    if (is_array(v))
                    {
                        vin = v[0];
                    }
                    var a = drawInputPrompt(-9999, -9999, vin);
                    xo = a[0];
                    height = max(height, a[1]);
                    width += xo;
                    offY = a[2];
                }
                else
                {
                    var a = drawInputPrompt(-9999, -9999, cstr);
                    xo = a[0];
                    height = max(height, a[1]);
                    width += xo;
                    offY = a[2];
                }
            };
        }
    };
}

function TEColor() : TextEffect() constructor
{
    color = 16777215;
    
    modify = function(arg0)
    {
        draw_set_color(color);
    };
}

function TCRainbow() : TEColor() constructor
{
    ogModify = method(self, modify);
    
    modify = function(arg0)
    {
        color = make_color_hsv(getFrame() % 255, 255, 255);
        ogModify(arg0);
    };
}

function TCRed() : TEColor() constructor
{
    color = 4082157;
}

function TCOrange() : TEColor() constructor
{
    color = 4235519;
}

function TCYellow() : TEColor() constructor
{
    color = 65535;
}

function TCGreen() : TEColor() constructor
{
    color = 32768;
}

function TCAqua() : TEColor() constructor
{
    color = 16776960;
}

function TCBlue() : TEColor() constructor
{
    color = 16711680;
}

function TCViolet() : TEColor() constructor
{
    color = 15096319;
}

function TCWhite() : TEColor() constructor
{
    color = 16777215;
}

function TCGray() : TEColor() constructor
{
    color = 12632256;
}

function TCBlack() : TEColor() constructor
{
    color = 2951949;
}

function processStringExt(arg0, arg1, arg2)
{
    var _ogFont = draw_get_font();
    var _piece = 0;
    var _pieceIndex = 0;
    for (var q = 0; q < 2; q++)
    {
        _piece[q][UnknownEnum.Value_0] = "";
        _piece[q][UnknownEnum.Value_1] = array_create(20, 0);
        _piece[q][UnknownEnum.Value_2] = 0;
        _piece[q][UnknownEnum.Value_3] = 0;
    }
    draw_set_font(arg2);
    arg0 = breakString(arg0, arg1);
    draw_set_font(_ogFont);
    var _strLength = string_length(arg0);
    for (var i = 1; i <= _strLength; i++)
    {
        var _currentChar = string_char_at(arg0, i);
        var _pieceEffects = _piece[_pieceIndex][UnknownEnum.Value_1];
        if (_currentChar == "♦" || i == _strLength || _pieceEffects[UnknownEnum.Value_7] || _pieceEffects[UnknownEnum.Value_2] || _pieceEffects[UnknownEnum.Value_3])
        {
            if (_currentChar != "♦" && string_char_at(arg0, i - 1) != "♦")
            {
                _piece[_pieceIndex][UnknownEnum.Value_0] = _piece[_pieceIndex][UnknownEnum.Value_0] + _currentChar;
            }
            _piece[_pieceIndex][UnknownEnum.Value_2] = string_length(_piece[_pieceIndex][UnknownEnum.Value_0]);
            var _newEffect = _currentChar + string_char_at(arg0, i + 1);
            var _nextPiece = _pieceIndex + 1;
            _piece[_nextPiece][UnknownEnum.Value_0] = "";
            _piece[_nextPiece][UnknownEnum.Value_1] = array_create(20, 0);
            _piece[_nextPiece][UnknownEnum.Value_2] = 0;
            _piece[_nextPiece][UnknownEnum.Value_3] = _piece[_pieceIndex][UnknownEnum.Value_3] + _piece[_pieceIndex][UnknownEnum.Value_2];
            if (_newEffect != "♦r")
            {
                var _copyEffect = _piece[_pieceIndex][UnknownEnum.Value_1];
                _copyEffect[UnknownEnum.Value_1] = 0;
                _piece[_nextPiece][UnknownEnum.Value_1] = _copyEffect;
                var _effectIndexToSet = 0;
                switch (_newEffect)
                {
                    case "♦/":
                        _effectIndexToSet = UnknownEnum.Value_1;
                        break;
                    case "♦w":
                        _effectIndexToSet = UnknownEnum.Value_2;
                        break;
                    case "♦s":
                        _effectIndexToSet = UnknownEnum.Value_3;
                        break;
                    case "♦b":
                        _effectIndexToSet = UnknownEnum.Value_4;
                        break;
                    case "♦i":
                        _effectIndexToSet = UnknownEnum.Value_5;
                        break;
                    case "♦k":
                        _effectIndexToSet = UnknownEnum.Value_6;
                        break;
                    case "♦`":
                        _effectIndexToSet = UnknownEnum.Value_7;
                        break;
                    case "♦0":
                        _effectIndexToSet = UnknownEnum.Value_8;
                        break;
                    case "♦1":
                        _effectIndexToSet = UnknownEnum.Value_9;
                        break;
                    case "♦2":
                        _effectIndexToSet = UnknownEnum.Value_10;
                        break;
                    case "♦3":
                        _effectIndexToSet = UnknownEnum.Value_11;
                        break;
                    case "♦4":
                        _effectIndexToSet = UnknownEnum.Value_12;
                        break;
                    case "♦5":
                        _effectIndexToSet = UnknownEnum.Value_13;
                        break;
                    case "♦6":
                        _effectIndexToSet = UnknownEnum.Value_14;
                        break;
                    case "♦7":
                        _effectIndexToSet = UnknownEnum.Value_15;
                        break;
                    case "♦8":
                        _effectIndexToSet = UnknownEnum.Value_16;
                        break;
                    case "♦9":
                        _effectIndexToSet = UnknownEnum.Value_17;
                        break;
                }
                if (string_char_at(_newEffect, 1) == "♦")
                {
                    _piece[_nextPiece][UnknownEnum.Value_1][_effectIndexToSet] = 1;
                }
            }
            _pieceIndex++;
        }
        else if (string_char_at(arg0, i - 1) != "♦")
        {
            if (!is_string(_piece[_pieceIndex][UnknownEnum.Value_0]))
            {
                _piece[_pieceIndex][UnknownEnum.Value_0] = _currentChar;
            }
            else
            {
                _piece[_pieceIndex][UnknownEnum.Value_0] = _piece[_pieceIndex][UnknownEnum.Value_0] + _currentChar;
            }
        }
    }
    return _piece;
}

function processString(arg0, arg1)
{
    return newProcessString(arg0, arg1, draw_get_font());
}

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

function removeTagsFromString(arg0)
{
    for (var i = 0; i < string_length(arg0); i++)
    {
        if (string_char_at(arg0, i + 1) == "♦")
        {
            arg0 = string_delete(arg0, i + 1, 2);
        }
    }
    return arg0;
}

function getStringHeight(arg0, arg1)
{
    arg0 = breakString(arg0, arg1);
    arg0 = string_replace_all(arg0, "♦/", "\n");
    arg0 = removeTagsFromString(arg0);
    return string_height(arg0);
}

function getStringWidth(arg0, arg1)
{
    arg0 = breakString(arg0, arg1);
    arg0 = string_replace_all(arg0, "♦/", "\n");
    arg0 = removeTagsFromString(arg0);
    return string_width(arg0);
}

function getPiecesHeightExt(arg0, arg1)
{
    var _stringHeight = string_height("\n");
    var _characters = 0;
    var ogFont = draw_get_font();
    if (is_struct(arg0))
    {
        with (arg0)
        {
            var totalStringHeight = 0;
            for (var i = 0; i < array_length(array); i++)
            {
                if (array[i].isBold)
                {
                    var boldFont = asset_get_index(font_get_name(draw_get_font()) + "Bold");
                    if (font_exists(boldFont))
                    {
                        draw_set_font(boldFont);
                    }
                }
                if (array[i].isItalics)
                {
                    var italicsFont = asset_get_index(font_get_name(draw_get_font()) + "Italics");
                    if (font_exists(italicsFont))
                    {
                        draw_set_font(italicsFont);
                    }
                }
                if (array[i].hasEffect(TEButton))
                {
                    var ov = array[i].visible;
                    array[i].visible = false;
                    array[i].draw();
                    totalStringHeight = max(totalStringHeight, array[i].height);
                    _stringHeight = max(_stringHeight, totalStringHeight);
                    array[i].visible = ov;
                }
                if (variable_struct_exists(array[i], "hasLineBreak") && array[i].hasLineBreak)
                {
                    totalStringHeight = max(totalStringHeight, string_height("\n"));
                    _stringHeight += totalStringHeight;
                }
                _characters += string_length(array[i].text);
                if (_characters > arg1)
                {
                    return _stringHeight;
                }
                draw_set_font(ogFont);
            }
        }
    }
    else
    {
        for (var i = 0; i < array_length(arg0); i++)
        {
            if (arg0[i][UnknownEnum.Value_1][UnknownEnum.Value_1])
            {
                _stringHeight += string_height("\n");
            }
            _characters += string_length(arg0[i][UnknownEnum.Value_0]);
            if (_characters > arg1)
            {
                return _stringHeight;
            }
        }
    }
    return _stringHeight;
}

function getPiecesLength(arg0)
{
    var _fullLength = 0;
    if (is_struct(arg0))
    {
        with (arg0)
        {
            for (var i = 0; i < array_length(array); i++)
            {
                _fullLength += string_length(array[i].text);
            }
        }
    }
    else
    {
        for (var i = 0; i < array_length(arg0); i++)
        {
            _fullLength += arg0[i][UnknownEnum.Value_2];
        }
    }
    return _fullLength;
}

function getPiecesHeight(arg0)
{
    return getPiecesHeightExt(arg0, 9999);
}

function getPiecesWidth(arg0)
{
    var _lineWidth = 0;
    var _greatestWidth = 0;
    var ogFont = draw_get_font();
    if (is_struct(arg0))
    {
        with (arg0)
        {
            for (var i = 0; i < array_length(array); i++)
            {
                if (array[i].hasLineBreak)
                {
                    _lineWidth = 0;
                }
                if (array[i].isBold)
                {
                    var boldFont = asset_get_index(font_get_name(draw_get_font()) + "Bold");
                    if (font_exists(boldFont))
                    {
                        draw_set_font(boldFont);
                    }
                }
                if (array[i].isItalics)
                {
                    var italicsFont = asset_get_index(font_get_name(draw_get_font()) + "Italics");
                    if (font_exists(italicsFont))
                    {
                        draw_set_font(italicsFont);
                    }
                }
                with (array[i])
                {
                    var ov = visible;
                    visible = false;
                    draw();
                    visible = ov;
                    _lineWidth += width;
                }
                if (_lineWidth > _greatestWidth)
                {
                    _greatestWidth = _lineWidth;
                }
                draw_set_font(ogFont);
            }
        }
    }
    else
    {
        for (var i = 0; i < array_length(arg0); i++)
        {
            if (arg0[i][UnknownEnum.Value_1][UnknownEnum.Value_1])
            {
                _lineWidth = 0;
            }
            _lineWidth += string_width(arg0[i][UnknownEnum.Value_0]);
            if (_lineWidth > _greatestWidth)
            {
                _greatestWidth = _lineWidth;
            }
        }
    }
    return _greatestWidth;
}

function getStringFromInput(arg0, arg1 = 0)
{
    if (is_array(arg0))
    {
        if (arg1 < array_length(arg0))
        {
            arg0 = arg0[arg1];
        }
        else
        {
            return "";
        }
    }
    else if (arg1 > 0)
    {
        return "";
    }
    switch (arg0)
    {
        case 27:
            return "ESC";
            break;
        case 112:
            return "F1";
            break;
        case 113:
            return "F2";
            break;
        case 114:
            return "F3";
            break;
        case 115:
            return "F4";
            break;
        case 116:
            return "F5";
            break;
        case 117:
            return "F6";
            break;
        case 118:
            return "F7";
            break;
        case 119:
            return "F8";
            break;
        case 120:
            return "F9";
            break;
        case 121:
            return "F10";
            break;
        case 122:
            return "F11";
            break;
        case 123:
            return "F12";
            break;
        case 44:
            return "PRT SC";
            break;
        case 19:
            return "PAUSE";
            break;
        case 8:
            return "BACKSPACE";
            break;
        case 45:
            return "INS";
            break;
        case 36:
            return "HOME";
            break;
        case 33:
            return "PGUP";
            break;
        case 111:
            return "/";
            break;
        case 106:
            return "*";
            break;
        case 109:
            return "-";
            break;
        case 107:
            return "+";
            break;
        case 9:
            return "TAB";
            break;
        case 46:
            return "DEL";
            break;
        case 35:
            return "END";
            break;
        case 34:
            return "PGDN";
            break;
        case 96:
            return "NUM0";
            break;
        case 97:
            return "NUM1";
            break;
        case 98:
            return "NUM2";
            break;
        case 99:
            return "NUM3";
            break;
        case 100:
            return "NUM4";
            break;
        case 101:
            return "NUM5";
            break;
        case 102:
            return "NUM6";
            break;
        case 103:
            return "NUM7";
            break;
        case 104:
            return "NUM8";
            break;
        case 105:
            return "NUM9";
            break;
        case 110:
            return ".";
            break;
        case 13:
            return "ENTER";
            break;
        case 160:
            return "LSHIFT";
            break;
        case 161:
            return "RSHIFT";
            break;
        case 16:
            return "SHIFT";
            break;
        case 32:
            return "SPACE";
            break;
        case 162:
            return "LCTRL";
            break;
        case 164:
            return "LALT";
            break;
        case 165:
            return "RALT";
            break;
        case 163:
            return "RCTRL";
            break;
        case 37:
            return "LEFT";
            break;
        case 39:
            return "RIGHT";
            break;
        case 38:
            return "UP";
            break;
        case 40:
            return "DOWN";
            break;
        case 1:
            return "LEFT CLICK";
            break;
        case 3:
            return "MIDDLE CLICK";
            break;
        case 2:
            return "RIGHT CLICK";
            break;
        case 4:
            return "MOUSE 4";
            break;
        case 5:
            return "MOUSE 5";
            break;
        case -40:
            return "MOUSE";
            break;
        case -39:
            return "SCROLL DOWN";
            break;
        case -38:
            return "SCROLL UP";
            break;
        case 32785:
        case 32786:
        case -130:
        case -129:
        case -128:
        case -131:
            return "L STICK";
            break;
        case 32787:
        case 32788:
        case -134:
        case -133:
        case -132:
        case -135:
            return "R STICK";
            break;
        case 32769:
            return "A";
            break;
        case 32770:
            return "B";
            break;
        case 32771:
            return "X";
            break;
        case 32772:
            return "Y";
            break;
        case 32782:
            return "DOWN";
            break;
        case 32783:
            return "LEFT";
            break;
        case 32784:
            return "RIGHT";
            break;
        case 32781:
            return "UP";
            break;
        case 32777:
            return "SELECT";
            break;
        case 32778:
            return "START";
            break;
        case 32773:
            return "L SHOULDER";
            break;
        case 32775:
            return "L TRIGGER";
            break;
        case 32774:
            return "R SHOULDER";
            break;
        case 32776:
            return "R TRIGGER";
            break;
        case 32779:
            return "L STICK";
            break;
        case 32780:
            return "R STICK";
            break;
        default:
            return chr(arg0);
            break;
    }
    return chr(arg0);
}

function concat()
{
    var str = "";
    for (var i = 0; i < argument_count; i++)
    {
        str += string(argument[i]);
    }
    return str;
}

function showMessage()
{
    var str = "";
    for (var i = 0; i < argument_count; i++)
    {
        str += string(argument[i]);
    }
    if (is_struct(self))
    {
        str = concat(instanceof(self), ": ", str);
    }
    else
    {
        str = concat(object_get_name(object_index), " (", id, "): ", str);
    }
    show_debug_message(str);
    return str;
}

function getRomanNumeral(arg0)
{
    var roman_numerals = ["M", "CM", "D", "CD", "C", "XC", "L", "XL", "X", "IX", "V", "IV", "I"];
    var integer_values = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1];
    var result = "";
    for (var i = 0; i < array_length(roman_numerals); i++)
    {
        while (arg0 >= integer_values[i])
        {
            result += roman_numerals[i];
            arg0 -= integer_values[i];
        }
    }
    return result;
}

function string_wordwrap_width(arg0, arg1, arg2 = "\n", arg3 = false)
{
    var pos_space = -1;
    var pos_current = 1;
    var text_current = arg0;
    if (is_real(arg2))
    {
        arg2 = "#";
    }
    var text_output = "";
    while (string_length(text_current) >= pos_current)
    {
        if (string_width(string_copy(text_current, 1, pos_current)) > arg1)
        {
            if (pos_space != -1)
            {
                text_output += (string_copy(text_current, 1, pos_space) + string(arg2));
                text_current = string_copy(text_current, pos_space + 1, string_length(text_current) - pos_space);
                pos_current = 1;
                pos_space = -1;
            }
            else if (arg3)
            {
                text_output += (string_copy(text_current, 1, pos_current - 1) + string(arg2));
                text_current = string_copy(text_current, pos_current, string_length(text_current) - (pos_current - 1));
                pos_current = 1;
                pos_space = -1;
            }
        }
        pos_current += 1;
        if (string_char_at(text_current, pos_current) == " ")
        {
            pos_space = pos_current;
        }
    }
    if (string_length(text_current) > 0)
    {
        text_output += text_current;
    }
    return text_output;
}

enum UnknownEnum
{
    Value_0,
    Value_1,
    Value_2,
    Value_3,
    Value_4,
    Value_5,
    Value_6,
    Value_7,
    Value_8,
    Value_9,
    Value_10,
    Value_11,
    Value_12,
    Value_13,
    Value_14,
    Value_15,
    Value_16,
    Value_17
}
