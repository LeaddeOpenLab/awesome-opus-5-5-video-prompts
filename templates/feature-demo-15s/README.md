# 15-second Feature Demo starter

An original, editable animation for showing a feature through a before/action/after sequence.

[Watch the example](example.mp4) · [中文说明](README.zh-CN.md) · [Edit configuration](config.js)

15 seconds · 1920×1080 · 30 fps · silent H.264 MP4 · MIT.

## Preview and customize

Download this whole directory and open `index.html` in a browser. No build step or API key is needed for preview. Change the copy, color and template-specific fields in the sidebar, then scrub through the timeline.

Optional PNG, JPEG or WebP uploads appear in the result panel in the final scene, fitted without cropping. A screenshot remains a static image; the template does not animate its internal controls. Default artwork and code are original; Focus is a fictional product, not a working app.

Click **Save config.js**, replace the original file with the download, then refresh. Browser edits are not saved automatically. Uploaded images are embedded in the downloaded config. Reset restores the loaded config. Chinese text is supported; fixed UI labels can be edited in `motion.js`.

## Render an MP4

Install Node.js 22+ and FFmpeg, then run inside this directory:

```sh
npm install
npx playwright install chromium
npm run render -- my-demo.mp4
```

The first dependency/browser install needs a network connection. Rendering default assets works offline afterwards. `npm run render` without a filename overwrites `example.mp4`. Set `FFMPEG_PATH` if FFmpeg is not on PATH.

## Timeline

0–4s: the busy task list. 4–7.4s: click Sort by priority and move rows into order. 7.4–10.8s: hold the result. 10.8–15s: focus view and call to action.

Rows 2 and 4 are high priority; the sorting order is fixed. Edit dest and levels in motion.js to change the business logic.

## Files and checks

- `config.js`: copy, colors, screenshot and scene-specific fields.
- `motion.js`: layouts, animation and deterministic `seek(seconds)`.
- `render.mjs`: headless Chromium + FFmpeg rendering.
- `check.mjs`: run `npm run check` to check preview, edits, screenshot upload, saved config and mobile overflow.
- `VERIFICATION.md`: local verification results.

The aspect ratio and duration are fixed in code. Original template code and artwork are MIT licensed; assets you add retain their own rights. No third-party footage or music is included.
