# ORBIT · 15-second product launch animation

A fictional note-taking product, adapted with Codex from the Leadde Open Lab Product Launch template. Includes a complete product brief, editable copy and colors, deterministic Canvas animation, and MP4 export.

[Watch the video and follow the tutorial](https://leaddeopenlab.github.io/awesome-opus-5-5-video-prompts/tutorials/codex-product-launch-video/)

## Preview and edit

Open `index.html`. Change the product name, headings, features and accent color. An uploaded screenshot appears in the first feature card. Click **Save config.js** and replace this folder's `config.js` before rendering; unsaved browser edits are not used by the renderer.

## Export

Install Node.js 22+ and FFmpeg (available on PATH), then run in this folder:

```sh
npm install
npx playwright install chromium
npm run check
npm run render -- orbit.mp4
```

Output: silent H.264 MP4, 15 seconds, 1920×1080, 30 fps. `motion.js` controls the scenes; `config.js` contains editable copy and colors. Fonts may differ slightly across systems.

## Prompts and attribution

`prompt.en.txt` and `prompt.zh-CN.txt` explain the fictional product, storyboard and deliverables. These reproduction prompts were rewritten from the completed film, not copied verbatim from the original conversation. They do not guarantee an identical result.

This example was rendered and checked with Codex, not tested with Claude. ORBIT is a fictional product; cards depict concept interfaces, not a working application. No external video, images or music are used. Code is licensed under MIT; see LICENSE.
