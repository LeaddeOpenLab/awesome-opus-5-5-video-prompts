# Local verification

Verified on macOS on 2026-10-16 with Playwright 1.62.1, Chromium and FFmpeg.

- Offline file preview, no external requests.
- Deterministic forward/backward seeking.
- Chinese copy and accent editing.
- Portrait image upload visibly changes the appropriate scene; screenshot fits without cropping.
- Downloaded config preserves copy and embedded image; remove-image works.
- 390px editor viewport has no horizontal overflow.
- No browser JavaScript errors during checks or render.
- MP4: H.264, yuv420p, 1920×1080, 30fps, 450 frames, 15.000s, no audio.
- FFmpeg full-file decode completed without errors.
- Opening, middle and ending frames inspected visually.

Windows and Linux have not been tested locally. Preview requires no installation; export requires Node.js, Chromium and FFmpeg.
