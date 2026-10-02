# Codex Pets 桌面宠物素材包

![小黑框动作预览](assets/preview.gif)

这是 Codex Pets 的已生成素材包，包含精灵图和动作预览。Pets 平台安装请使用 Pets 插件导入素材；本仓库不含独立桌面运行器。

最终素材为 `assets/spritesheet.png`：1536 × 2288 像素，73 帧。

`sounds/sound_hook.py` 是 macOS 本地 Codex 音效脚本：提交请求播放 Tink，首次工具调用播放 Pop，本轮结束播放 Glass；同一轮的事件会去重。

将 `sounds/sound_hook.py` 保留在固定路径，然后在 `~/.codex/hooks.json` 的 `hooks` 对象中，为 `UserPromptSubmit`、`PreToolUse`、`Stop` 各添加以下配置；将示例绝对路径替换为脚本的实际路径：

```json
{
  "UserPromptSubmit": [{"hooks": [{"type": "command", "command": "/usr/bin/python3 \"绝对路径/sound_hook.py\"", "timeout": 3}]}],
  "PreToolUse": [{"hooks": [{"type": "command", "command": "/usr/bin/python3 \"绝对路径/sound_hook.py\"", "timeout": 3}]}],
  "Stop": [{"hooks": [{"type": "command", "command": "/usr/bin/python3 \"绝对路径/sound_hook.py\"", "timeout": 3}] }]
}
```

把这个配置用于上述三个事件，并保留 `hooks.json` 中已有的 hooks。配置后在 Codex CLI 中运行 `/hooks` 并信任该 hook。详情见 [Codex Hooks 文档](https://learn.chatgpt.com/docs/hooks)。
