# Dead Estate《死亡庄园》简体中文汉化补丁

Dead Estate 的完整简体中文汉化补丁。最终版本 **v3g**。

## 下载补丁

**直接下载（解压到游戏根目录即完成安装）：**

```
https://github.com/Cyclin15/dead-estate-chs/releases/latest/download/死亡庄园汉化补丁v3g.zip
```

或到 [Releases 页面](https://github.com/Cyclin15/dead-estate-chs/releases) 下载。

## 安装

1. 完全退出 Steam 和游戏
2. 把压缩包里的 `data.win` 解压到游戏根目录（Steam 库中右键游戏 → 管理 → 浏览本地文件），覆盖原文件
3. 启动游戏

## 还原

Steam 中右键游戏 → 属性 → 已安装文件 → 验证游戏文件完整性；或用 Release 附件 `original_backup_data.win` 覆盖回去。

## 版本信息（v3g）

- 汉化版 `data.win` MD5：`5BF13F8FA3BEF72A36B79ACE7F127412`（107,428,828 字节）
- **4,910 条译文**：对话、道具/武器/诅咒描述、UI、勋章、挑战、安雅模式全篇文本
- **34 个游戏字体全部重建**，中文采用[缝合像素字体 Fusion Pixel Font](https://github.com/TakWolf/fusion-pixel-font)，像素风格与游戏美术一致；拉丁字形与原始度量不变，英文排版不受影响
- 「安雅的任务」模式两个特殊字体（手写体、打字机体）新增中文版
- 老存档完全兼容（存档键名保持英文；35 个存档键字符串特意回退为英文）
- 按原版英文保留：PLAY! / COSTUME / 难度名称 / 街机倒计时词（HURRY / NICE / WIN / BADASS）等由纯英文 LED 精灵字体或按布局需要保留原文的项目
- 历次修复：breakString 中文换行 bug（描述框飞出屏幕）、♦ 文本控制码字形、街机模式倒计时方框

## 仓库内容

- `scripts/` — 全部构建与调试脚本（BuildV3.csx 主管线、SwapV2Fonts.csx 字体移植、各分析脚本）
- `dump/` — 翻译数据（`translations.json`，键=字符串表索引）、原文字表（`pristine_strings.json`）、字符集（`charset.txt` 在根目录）、换行修复源码（`scrStrings_fixed.gml`）等
- `docs/` — 补丁说明

Release 附件：

| 附件 | 说明 |
|---|---|
| `死亡庄园汉化补丁v3g.zip` | **补丁本体**，解压到游戏根目录即安装 |
| `data_v3g_win.zip` / `data_v3g.win` | 最终版 data.win |
| `data_base_1001.win` | 构建基底（10.1 版），BuildV3 的加载起点 |
| `project_all.zip` | 全部工程文件（字体源、工具、导出、截图等） |
| `original_backup_data.win` | 原版英文 data.win 备份 |

## 构建管线

```
dump/translations.json（键=字符串索引，值=中文）
  + charset.txt（译文字符集）
        │
        ▼  tools/utmt UndertaleModCli.exe load out/data.win -s scripts/BuildV3.csx
   字符串替换 + 34 字体重建 + 安雅中文字体 + 字节码补丁 + breakString 修复
        │
        ▼  SwapV2Fonts.csx（从带 v2 字体的文件移植字体表与纹理）
   data_v3g.win
```

修改翻译：编辑 `dump/translations.json`（回退某条 = 删除对应键）→ 跑 BuildV3 → SwapV2Fonts → 覆盖游戏目录 `data.win`。

工具：[UndertaleModTool](https://github.com/UnderminersTeam/UndertaleModTool)、[Fusion Pixel Font](https://github.com/TakWolf/fusion-pixel-font)（缝合像素字体，OFL 协议）。
