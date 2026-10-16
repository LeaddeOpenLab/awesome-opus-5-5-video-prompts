# 15-second Product UI Starter

A small, editable product animation from Leadde Open Lab. Open a file, change the copy and colors, add a screenshot, and render a 15-second video.

[简体中文使用说明](README.zh-CN.md) · [Example MP4](example.mp4) · [Configuration](config.js)

![Example frame](poster.jpg)

**15 seconds · 1920 × 1080 · 30 fps · silent · MIT**

The example uses **Forma**, a fictional product. Its illustrated “choose → customize → export” workflow is an animation, not a functioning video editor. The template and visuals are original code; it is not a reproduction of a community prompt or a claim about any particular model.

## 1. Preview without installing anything

Download this folder and double-click `index.html` in a modern browser. Everything required for the default preview is local. No account, API key, server or paid renderer is needed.

- Play, pause, replay, or scrub the timeline.
- Edit the product name, opening, middle and ending text, accent color, website and call to action.
- Upload an optional PNG, JPEG or WebP screenshot. It appears inside the editor preview, with its aspect ratio preserved.
- Open **More copy** to edit subtitles, project name and background color.

The preview makes no network requests. The GitHub link only navigates when clicked.

## 2. Keep your changes

Click **Save config.js**, then replace the original `config.js` in this folder with the downloaded file. Refresh to confirm your changes are saved. The screenshot is embedded in that file; keep it reasonably sized (around 1600 pixels wide is usually sufficient).

Edits are temporary until saved. The browser does not overwrite the original file automatically. **Reset** restores the configuration loaded from disk, not necessarily the factory defaults.

You can also edit `config.js` directly. Example:

```js
productName: "Your product",
accent: "#087F73",
headline: "Start with a clear idea.",
editorTitle: "Make it yours.",
endHeadline: "Ready for your next launch.",
cta: "Try the demo",
website: "your-product.com",
```

English and Chinese copy are supported. Short headlines read best. The smaller fictional UI labels remain English and can be edited in `motion.js`.

## 3. Export an MP4

Prerequisites: **Node.js 22 or newer**, npm and **FFmpeg** on your PATH. Browser preview does not require these tools; MP4 export does.

Open a terminal in this folder:

```sh
npm install
npx playwright install chromium
npm run render
```

This generates `example.mp4`, replacing an existing file with that name. To keep the supplied example:

```sh
npm run render -- my-product.mp4
```

The renderer captures 450 deterministic frames and encodes them using FFmpeg. Output is H.264, yuv420p, 1920 × 1080, 30 fps, 15 seconds, with no audio track. Internet access is needed for initial dependency installation, not for rendering the default template afterward.

If FFmpeg is not on PATH, set `FFMPEG_PATH` to its executable path. If Playwright reports a missing browser, run the Chromium installation command above. Linux hosts may need browser system dependencies (`npx playwright install --with-deps chromium`).

## What can I change?

| File | Purpose |
|---|---|
| `config.js` | Brand name, text, color and optional screenshot |
| `index.html` | Preview player and editing controls |
| `motion.js` | Canvas artwork and the deterministic `seek(seconds)` timeline |
| `render.mjs` | Frame capture and MP4 encoding |
| `example.mp4` | Rendered example |
| `check.mjs` | Practical preview and configuration checks |

Scene timings are fixed: **0–3 seconds** choose a template; **3–11.2 seconds** customize and preview; **11.2–15 seconds** export confirmation and call to action. Swapping a screenshot changes the picture inside the frame, not the surrounding layout or the screenshot’s internal interactions. Layout and timing changes require editing `motion.js`.

## Verification

Run `npm run check` to check offline loading, deterministic scrubbing, Chinese text and color changes, screenshot upload/removal, configuration download and a 390-pixel mobile layout. Review screenshots are written to `qa/`.

The supplied example was rendered and checked on macOS Apple Silicon. See [verification notes](VERIFICATION.md) for the actual environment and output. Other operating systems can render different system fonts.

## License

Original template code and generated default artwork: [MIT](LICENSE). Screenshots, branding and other material you add retain their own rights. No third-party footage, music or font files are bundled.

[Explore more prompts and examples](https://github.com/LeaddeOpenLab/awesome-opus-5-5-video-prompts). If this starter helps, a GitHub star makes it easy to find again.
