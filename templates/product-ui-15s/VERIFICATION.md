# Verification / 实测记录

Date: 2026-10-16 (Asia/Shanghai)

## Environment

- macOS, Apple Silicon.
- Node.js 24.19.0.
- Playwright 1.62.1 and its installed Chromium (build 1234).
- FFmpeg with libx264.
- Headless browser running this local template only. No personal browser session or account was used.

## Completed checks

- Default preview loads from `file://` without HTTP requests.
- `seek(7)` produces the same image after seeking forward and backward.
- Product name, Chinese ending copy, call to action and accent color update through the editing controls.
- A portrait PNG uploads, displays with preserved aspect ratio, saves inside the downloaded configuration, and can be removed.
- Downloaded `config.js` contains the edited text and image data.
- Preview layout fits a 390-pixel mobile viewport without horizontal overflow.
- No browser JavaScript errors during the checks.
- Opening, editor, ending and transition frames reviewed; text fades out before the application shell changes layout.
- Full 450-frame MP4 rendering completed. Final file is checked with FFprobe and decoded with FFmpeg before delivery.

## Output

- `example.mp4`: 15.000 seconds, 1920 × 1080, 30 fps, 450 frames.
- H.264 video, yuv420p, no audio stream.
- `poster.jpg`: still from the rendered example.

## Scope

This verifies a runnable template and its export workflow on the environment above. It is not an Opus reproduction test, a model benchmark, or a claim that an actual product video editor is implemented. Windows and Linux were not separately tested. Fonts can vary by operating system.

模板可运行和可导出已实测；未把演示中的虚构 UI 当作真实产品功能。截图是静态内容替换，内部按钮不会自动变成真实交互。
