# Eden (Doris)

<img src="docs/icon.png" width="96" align="right" alt="Eden (Doris) icon">

A personal build of the [Eden](https://git.eden-emu.dev/eden-emu/eden) Nintendo Switch emulator for Android,
aimed at fixing the graphical problems that remain in *Tears of the Kingdom* on Snapdragon 8 Gen 2 / Adreno 740
handhelds (AYN Thor Pro): distant terrain, structures and shadows that flicker or vanish for a moment.

## Installs beside every other Eden

| | Eden (Doris) | Official Eden | Eden Nightly (coexist) |
|---|---|---|---|
| Package | `dev.eden.eden_doris` | `dev.eden.eden_emulator` | `dev.eden.eden_nightly` / `dev.eden.eden_emulator.nightly` |
| Name on the home screen | Eden (Doris) | Eden | Eden Nightly |

Because the package is its own, installing or updating Doris never replaces or updates another Eden, and the other
Edens never update Doris. Its settings, keys, firmware, drivers, saves and shader cache live in its own folder
(`Android/data/dev.eden.eden_doris`). It does not run Eden's own update checker, so it never downloads an official
Eden build.

## What it is built on

Doris starts from exactly the build Yael plays on: Eden PR #4324
(`c3bdfd14c5-xbzk/mhr-flicker-slow-evidences`, late-August 2026 Eden plus one experimental commit), not from newer
Eden. With its default settings Doris behaves like that build; fixes are added on top.

Doris's own settings are under **Settings → Graphics → Eden (Doris) experiments** (globally or per game). Each one takes
effect the next time the game starts.

* **GPU barriers** (default: Doris: real barriers). Eden turns the game's "wait until the GPU is done" points into a
  Vulkan event wait that guarantees neither ordering nor visibility of earlier writes, and puts no barrier after compute
  work. On Adreno this lets draws read culling results, indirect draw arguments and vertex data that aren't finished
  yet, so distant terrain, buildings and shadows can drop out for a frame. Doris uses real barriers. "Eden (as before)"
  switches back, for comparison; "+ tiled-cache barriers" also makes the game's tiled-cache barriers real.
* **Core layout** (default: Let Android decide). "Doris" puts Eden's GPU emulation thread, the busiest one, on the
  fastest CPU core (the prime core on Snapdragon 8 Gen 2) and the other heavy emulator threads on the middle cores,
  through Eden's own core groups. The prime core is also the hottest, so this is off by default.
* **CPU profiler** (default: on for now, while the speed-up work needs data). Samples where the GPU thread and the
  Vulkan worker spend their CPU time and writes the totals to `doris_profile.txt` in the log folder every 20 seconds.
  Each release includes `libyuzu-android-symbols-<n>.zip` to turn the offsets into function names.
* **Performance report** (default: off). While a game runs, writes a summary to the log every 10 seconds: frame
  times, how busy each emulator thread is (and on which core), CPU and GPU clocks, GPU load, battery temperature;
  per frame, the draws, dispatches, render passes and submits, new pipelines, how long the GPU thread waited for
  presentation and GPU fences and the Vulkan worker for shader builds, and the GPU time of the whole frame, of frame
  generation and of output scaling (GPU timestamps); and how often the GPU thread and the Vulkan worker ran on prime,
  middle or little cores. Share it with **Share debug logs**.
* **Wait for new textures** (default: up to 8 ms per frame). Only matters with ASTC Decoding Method on CPU Async:
  Eden draws new textures before they are decoded, so new places flash as textures fill in. Doris waits briefly for
  each new texture and uploads it straight away.
* **Texture decoding threads** (default 2; Eden uses 1). Background threads for CPU Async decoding.
* **Wait for new shaders** (default: up to 8 ms per frame). Only matters with asynchronous shaders on: Eden hides
  anything whose shader is still compiling, so new places flicker as things pop in. Doris first waits up to this long
  per frame for the shader to finish. "Don't wait (Eden)" switches back.
* **Shader loop limit**: how many times a loop inside a game shader may repeat before it is cut short.
  PR #4324 lowered Eden's 8192 to 256. Choices: 256 (PR #4324, default), 512, 1024, 2048, 4096, 8192 (Eden default),
  no limit.
* **Monster Hunter Rise record fix**: always (PR #4324, default), only in Monster Hunter Rise, or off. The log notes
  every time it rewrites a copy, and in which game.

## Speed-ups from eden-lun

Doris carries 20 of the CPU-side speed-ups that [eden-lun](https://github.com/luneflu/eden-lun) (by alvindimas05)
made to Eden's GPU emulation: cheaper address translation, fewer redundant cache and LRU updates, faster pipeline
and descriptor lookups, batched register writes. They are applied unchanged as git commits (with `cherry picked from`
lines), plus one Doris commit that adapts three of them to this older base and ports a fourth, and a port of
eden-lun's device-memory continuity fix adapted to this base (a stale run could read or write memory that no longer
backs a range).

Left out on purpose: "skip dirty cascade on unchanged register writes" (can leave stale state on screen) and the flat
descriptor-ID lookup (needs newer texture-cache code). "Decouple vertex buffer dirty from vertex input" was carried
from build 6 to 9 and is undone from build 10: it made a vertex stream that is switched on (or changes stride) without
its address being rewritten keep its old, often empty, binding, so objects (water most visibly) vanished for a moment.
With dynamic vertex input off, as on Adreno, it never saved any time.

## How it is built

* `UPSTREAM` names the PR #4324 commit on Eden's server (with a GitHub-mirror fallback, `upstream/pr4324.patch`).
* `patches/` holds every Doris change as a git patch, applied in order on top of it.
* Each push to `main` runs [the workflow](.github/workflows/build.yml), which builds the `doris` flavor and publishes
  the APK as a release named `doris-<number>`. Later builds have a higher version code and the same signature, so each
  one installs as an update of the previous Doris.

No game files, keys or firmware are in this repository or in its releases.

## License

Eden is GPL-3.0-or-later; so are these patches. See the upstream repository for the full license and credits.
