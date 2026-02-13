# B 站视频转文本 - 参考文档

## 环境检测逻辑

`check_env.py` 检测以下内容：

| 项目 | 检测方式 | 必需条件 |
|------|----------|----------|
| Python | sys.version_info | 3.10+ |
| ffmpeg | `which ffmpeg` + `ffmpeg -version` | 存在且可执行 |
| yt-dlp | `which yt-dlp` + `yt-dlp --version` | 存在且可执行 |
| Whisper | `import whisper` | 仅无字幕时需要 |

输出 JSON 字段说明：

- `ready_for_subtitle`：是否有字幕路径所需依赖（python + ffmpeg + yt-dlp）
- `ready_for_whisper`：是否具备无字幕转写能力
- `install_commands`：按当前 OS 给出的安装命令列表

## 故障排查

### 1. 提示 "missing yt-dlp"

- 运行 `pip install yt-dlp`
- 或 Mac：`brew install yt-dlp`
- 或从 [yt-dlp releases](https://github.com/yt-dlp/yt-dlp/releases) 下载可执行文件并加入 PATH

### 2. 提示 "missing ffmpeg"

- Mac：`brew install ffmpeg`
- Windows：`choco install ffmpeg` 或从 [gyan.dev](https://www.gyan.dev/ffmpeg/builds/) 下载

### 3. 未能获取视频文本

- 有字幕：B 站字幕通常需登录。使用 `--cookies-from-browser chrome`（或 safari）从浏览器读取 cookie。部分视频可能未上传 CC 字幕，仅会列出 danmaku（弹幕）。
- 无字幕：检查是否已安装 `openai-whisper`，首次运行会下载模型，需网络。若无字幕且未安装 Whisper，会失败。

### 4. B 站 403 / 签名错误

- 更新 yt-dlp：`pip install -U yt-dlp`
- B 站有时会更新 API，需使用最新版 yt-dlp

### 5. Whisper 转写过慢

- 默认使用 `base` 模型，可改为 `tiny` 或 `small`（在 bvt.py 中修改 `whisper.load_model("base")`）
- 有 GPU 时可安装 `pip install openai-whisper` 的 CUDA 版本

### 6. Windows 下 pip 找不到

- 确保安装 Python 时勾选 "Add to PATH"
- 或使用 `py -3 -m pip install -r requirements.txt`

## 字幕语言代码

B 站支持的语言代码示例：zh-CN、zh-Hans、zh-TW、zh-Hant、en 等。脚本会依次尝试 zh-CN、zh、zh-Hans、zh-TW。
