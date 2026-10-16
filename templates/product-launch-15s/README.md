# 15-second Product Launch starter

An original, editable animation for introducing a new product and three benefits.

[Watch the example](example.mp4) · [中文说明](README.zh-CN.md) · [Edit configuration](config.js)

15 seconds · 1920×1080 · 30 fps · silent H.264 MP4 · MIT.

## Preview and customize

Download this whole directory and open `index.html` in a browser. No build step or API key is needed for preview. Change the copy, color and template-specific fields in the sidebar, then scrub through the timeline.

Optional PNG, JPEG or WebP uploads appear in the product card in the opening scene, fitted without cropping. A screenshot remains a static image; the template does not animate its internal controls. Default artwork and code are original; Gather is a fictional product, not a working app.

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

0–4s: product introduction and tilted product card. 4–10.5s: three sequential feature cards with animated graphics. 10.5–15s: a centered launch headline, call to action and URL.

Edit featureOne/Two/Three and detailOne/Two/Three for the benefit cards. The default collect/connect/share graphics are defined in motion.js.

## Files and checks

- `config.js`: copy, colors, screenshot and scene-specific fields.
- `motion.js`: layouts, animation and deterministic `seek(seconds)`.
- `render.mjs`: headless Chromium + FFmpeg rendering.
- `check.mjs`: run `npm run check` to check preview, edits, screenshot upload, saved config and mobile overflow.
- `VERIFICATION.md`: local verification results.

The aspect ratio and duration are fixed in code. Original template code and artwork are MIT licensed; assets you add retain their own rights. No third-party footage or music is included.
