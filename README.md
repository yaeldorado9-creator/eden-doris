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

Doris's own settings are under **Settings → Graphics → Eden (Doris) experiments** (globally or per game). Most take
effect the next time the game starts; the ones marked "right away" apply as soon as they are changed.

* **GPU barriers** (default: Doris: real barriers where needed). Eden turns the game's "wait until the GPU is done"
  points into a Vulkan event wait that guarantees neither ordering nor visibility of earlier writes, and puts no
  barrier after compute work. On Adreno this lets draws read culling results, indirect draw arguments and vertex data
  that aren't finished yet, so distant terrain, buildings and shadows can drop out for a frame. Doris puts a barrier
  after every compute dispatch, and a full barrier at a wait point when a draw since the previous one wrote storage
  buffers or images (or used transform feedback). In the build 18 log, 113 of TotK's 130 wait points per frame had no
  such draw before them; from build 19 those stop neither the GPU nor the render pass (compute, uploads, copies and
  render pass ends carry barriers of their own). "Real barriers at every wait (build 18)" keeps a full barrier at every
  wait point; "Eden (as before)" switches back, for comparison; "+ tiled-cache barriers" also makes the game's
  tiled-cache barriers real. A full barrier that would follow another one with nothing recorded in between is left
  out (it would change nothing).
* **Texture cleanup** (default: Doris; right away). See [Texture cleanup](#texture-cleanup). "Eden (as before)"
  switches back to build 15's behaviour.
* **Core layout** (default: Let Android decide). "Doris" puts Eden's GPU emulation thread, the busiest one, on the
  fastest CPU core (the prime core on Snapdragon 8 Gen 2) and the other heavy emulator threads on the middle cores,
  through Eden's own core groups. The prime core is also the hottest, so this is off by default.
* **CPU profiler** (default: off). Samples where the GPU thread and the
  Vulkan worker spend their CPU time (with call stacks, and system-library function names) and writes the totals to
  `doris_profile.txt` in the log folder every 20 seconds.
  Each release includes `libyuzu-android-symbols-<n>.zip` to turn the offsets into function names.
* **Performance report** (default: off). While a game runs, writes a summary to the log every 10 seconds (with the
  device's clock time, to match it with videos of the screen): frame times, how busy each emulator thread is (and on which core), CPU and GPU clocks, GPU load, battery temperature (and the GPU's and the hottest CPU and GPU sensors', where readable);
  per frame, the draws, dispatches, render passes and submits, new pipelines, how long the GPU thread waited for
  presentation and GPU fences and the Vulkan worker for shader builds, and the GPU time of the whole frame, of frame
  generation and of output scaling (GPU timestamps); how often the GPU thread and the Vulkan worker ran on prime,
  middle or little cores; worker wake-ups, render passes cut by a submit, memory-protection changes, wait-for-idles
  (and how many redundant barriers were left out) and tiled-cache barriers per frame; texture uploads (and how many
  replaced GPU-drawn contents) and what the texture garbage collector removed, copied back or called off, with GPU
  memory against its thresholds; upload volume, new staging buffers and new GPU memory per frame, and the time the GPU
  thread spent getting or freeing GPU memory, waiting for the game's commands and waiting for the texture and buffer
  cache locks (and how long fence handling held them); how often the game wrote to pages holding GPU-written bytes
  (copied back first) and how long it waited for that; how many wait-for-idles came inside a render pass and how many
  had no storage writes by draws before them; how often the game wrote next to GPU-drawn textures and whether their
  contents were kept; and the textures (size and format) that were uploaded again over GPU-drawn contents, had their
  bytes changed by the game, or were removed by the cleanup with GPU-drawn contents lost; partial uploads; which path
  marked a GPU-drawn texture as changed as a whole; textures sharing memory (pairs Eden keeps apart and why, textures
  created from drawings, same-layout updates); separate heap mappings (Android); every separate heap rebuild (all
  memory protection changes wait for it) is logged with how long it took. It also lists the longest hitches
  (frames over 50 ms) of every 10 seconds, each with how long the GPU emulation thread was actually busy in it, how
  long it waited for the game's commands, for the GPU, for presentation, for GPU memory and for the cache locks, how
  busy the game's own threads were, and the shaders, uploads, new memory, texture removals, draws and submits in that
  frame. While the
  report is on, a hitch sampler records the GPU emulation thread's call stacks during every frame that runs past
  40 ms (every 2 ms, nothing in between) and writes those of frames over 50 ms to `doris_hitches.txt` in the log
  folder. Share it with **Share debug logs**.
* **Wait for new textures** (default: up to 8 ms per frame). Only matters with ASTC Decoding Method on CPU Async:
  Eden draws new textures before they are decoded, so new places flash as textures fill in. Doris waits briefly for
  each new texture and uploads it straight away.
* **Texture decoding threads** (default 2; Eden uses 1). Background threads for CPU Async decoding.
* **Wait for new shaders** (default: up to 8 ms per frame). Only matters with asynchronous shaders on: Eden hides
  anything whose shader is still compiling, so new places flicker as things pop in. Doris first waits up to this long
  per frame for the shader to finish. "Don't wait (Eden)" switches back.
* **Shader loop limit**: how many times a loop inside a game shader may repeat before it is cut short.
  PR #4324 lowered Eden's 8192 to 256 for Monster Hunter Rise. The count runs per pixel (or vertex, or compute
  thread) for the whole shader and is not reset when a loop starts again, so a loop inside another loop reaches 256
  quickly and the rest of its work is skipped. From build 17 the default is Eden's 8192 (the first game start after
  the change takes longer, while the affected shaders are compiled again). Choices: 256 (PR #4324), 512, 1024, 2048,
  4096, 8192 (default), no limit.
* **Monster Hunter Rise record fix**: always (PR #4324, default), only in Monster Hunter Rise, or off. The log notes
  every time it rewrites a copy, and in which game.

## GPU drawings and the game's own writes (build 19)

The game's code and the GPU often keep data on the same 4 KiB page of memory. Eden only learns that the game wrote to
a page, not where:

* **Textures.** Eden treated every texture on a written page as changed by the game and, at its next use, uploaded it
  again from guest memory. For a texture the GPU drew into, guest memory still holds what was there before, so the
  drawing was replaced with old contents until the game drew it again (the build 18 log: up to 400 such uploads every
  10 seconds; the likeliest cause of the ground switching material for half a second). From build 19, when the game
  writes to a page shared with a GPU-drawn texture, Doris keeps a copy of the texture's own bytes on that page as
  they were before the write and lets the write through. At the texture's next use (or the end of the frame) it
  compares: if the game changed those bytes, the texture is uploaded again as in Eden; if it only wrote the data next
  to it, what the GPU drew stays.
* **Buffers.** Since build 18 (Eden #4490/#4531), bytes the GPU wrote on such a page are copied back before the
  game's write. Each copy waits for the GPU to finish everything queued, about 20 ms while a frame is in flight, and
  in the build 18 log the game then wrote the next pages of the same buffer, in bursts of 10 to 13 waits. Build 19
  copies back the GPU-written bytes of the surrounding 512 KiB at once, so those writes find none.

### Only what changed is uploaded (build 20)

The build 19 report named the textures that still lost what the GPU drew: one family, R8G8 textures of 260x260 with
9 mip levels (256 plus a 2-pixel border on each side, the shape of a terrain tile) and the render targets of their
levels, uploaded again from guest memory up to 141 times in 10 seconds. When the game's code changes any part of a
texture, Eden uploads all of it again, so everything else the GPU drew in it (the other mip levels, the borders, the
rest of the level) was replaced with old contents. From build 20:

* A game write to a GPU-drawn texture keeps a copy of the texture's bytes on up to 64 pages per texture; at the
  texture's next use (or the end of the frame) Doris finds the 512-byte blocks of the texture's memory layout whose
  bytes changed and uploads only those. Everything else keeps what the GPU drew. Plain 2D textures, texture arrays
  and mip levels are handled; other layouts, or writes over more than 64 pages (the game rewriting the whole
  texture), are uploaded whole as in Eden.
* DMA copies and inline uploads that Eden carries out on the CPU upload just the blocks they wrote into GPU-drawn
  textures.
* The block layout maths was checked on a PC against Eden's own unswizzling for 11 texture layouts.

### Textures that share memory (build 21)

Builds 19 and 20 protected what the GPU drew only in textures marked as GPU-drawn. The build 20 log showed the
protection working (no GPU-drawn texture was uploaded again over its drawing) while the ground kept switching, so the
drawings were being lost somewhere that mark doesn't reach. Eden keeps several textures over the same memory: the
terrain tile that the game samples (260x260, 9 mip levels) and the render targets it draws each level through (288x260,
160x130, 96x65, 32x16 and smaller, their widths rounded up to the memory layout). Three gaps between them:

* **A texture made from a drawing wasn't marked as one.** When Eden creates a texture over memory that a render target
  already drew into, it copies the drawing in, but marked the new texture as if it had been read from guest memory.
  The game's next write anywhere on its 82 pages then uploaded all of it again from guest memory, which never got the
  drawing (a dark tile), and the render targets never gave it back (they weren't newer), until the game drew that
  tile again. GPU copies (blits, DMA) also read it from guest memory. Such textures are now marked as GPU-drawn, as
  Eden already does when it updates a texture from a render target later on.
* **Textures Eden can't join never exchanged contents.** Eden joins two textures over the same memory only when one
  fits inside the other by its rules; the rest ("bad overlap") are kept apart, and a drawing in one never reaches the
  other. Where both lay the shared memory out the same way (same bytes per texel, same row pitch, same block height,
  starting whole block rows apart), the newer drawing is now copied into the other when it is used, which is what the
  memory itself would show. Checked on a PC against Eden's own unswizzling, for the terrain tile against each of its
  render targets (both ways, also with the render targets' block height as the game might set it), and for other
  layouts that must and must not match.
* **The cleanup could copy back an old drawing.** Before copying a texture back to guest memory and removing it, the
  cleanup now first brings it up to date from the textures that share its memory. Render targets with one level that
  share memory with more than one texture are removed without a copy back of their own (as in Eden); their drawings
  now survive in the textures that were updated from them.

The report adds a line on textures sharing memory (pairs kept apart as each new texture is created, textures created
from drawings, same-layout updates, uploads next to drawings) and names the pairs Eden keeps apart, with the reason
each one can't be part of the other; the first time a pair shows up, both layouts are written to the log in full.
Formats are named instead of numbered. It also shows the GPU's temperature and the hottest CPU and GPU sensors,
where the system lets apps read them.

## Fixes from newer Eden (build 18)

Doris is based on late-August Eden. These later Eden fixes are carried over (as git commits with
`cherry picked from` lines, or ported where this base differs):

* **TotK dark squares** (Eden #4565). Adreno (Qualcomm's driver and Turnip) rounds texture-gather coordinates
  differently from the Switch's GPU, so a gather near a texel edge can read the neighbouring texels. In *Tears of the
  Kingdom* that gives large dark squares on the ground; whole stretches of terrain can show the wrong material. Eden
  already corrected the coordinates for other GPUs; now also for Qualcomm and Turnip.
* **GPU-written data kept when the game writes next to it** (Eden #4490, #4531, #4530). With the NCE CPU backend,
  the game writing anywhere on a page that also holds bytes the GPU wrote (culling results, indirect draw
  arguments, vertex data) made Eden throw those bytes away and later re-read stale ones from guest memory. They are
  now copied back first. Includes Eden's fix for the duplicate-interrupt deadlock this exposed.
* **Dirty tracking for GPU inline uploads and macros** (Eden #4473): compute inline uploads and Maxwell macro
  arguments that arrive in several pieces are tracked as one, and neighbouring macro arguments are no longer cleared.
* **Bindless textures chosen by a condition** (Eden #4551): when a shader picks its texture with a condition, the
  shader compiler now follows the condition instead of using an old handle (the wrong texture).
* **Missing subgroup operations on Qualcomm and Turnip** (Eden #4508): warp shuffles and geometry shader subgroup
  data are emulated where the driver lacks them, instead of being skipped.
* **Buffer uploads without "optimized vertex buffers"** use Eden's older logic (Eden #4528), as Eden does on
  Android.

The shader changes mean the first game start after installing build 18 rebuilds the game's shaders (a longer
loading screen, once).

## Submitting work to the GPU

* Eden woke its Vulkan worker thread with a condition-variable notify every time it handed over work (every 4 draws),
  and the worker made another one per chunk; on Android every notify is a futex system call. Doris only notifies a
  thread that is actually asleep (build 11 profile: these calls were about 12% of the GPU emulation thread and 9% of
  the worker).
* Submits (every 512 draws) happen exactly when Eden does them. Build 12 held submits back while a render pass was
  open; that started the GPU later in each frame and caused hitches, so it was undone.
* From build 16, recorded work is handed to the worker every 16 draws instead of every 4. Build 15 still woke the
  worker 500 to 780 times per frame (it falls asleep between hand-offs), each one a futex system call on the GPU
  emulation thread; the build 14 profile put system calls from draws at 5.4% of that thread.

## Uploads (build 17)

The build 16 log: the longest hitches (360 to 560 ms, with the GPU emulation thread busy all along) each came with
GPU memory jumping by 256 to 576 MiB, always in whole 64 MiB blocks, and falling back within seconds. The likeliest
source is staging memory (build 17's report measures it directly): an upload that doesn't fit in the part of the stream buffer the GPU has finished with gets a staging buffer of
its own, made on the spot (fresh memory the kernel has to provide and clear, page by page, on the GPU thread) and freed
again about two seconds later; so does every upload over 16 MiB.

* The stream buffer is 512 MiB on Android (Eden: 256 MiB), and all of it is touched once while the game loads.
* Uploads up to half its size go through it (Eden: up to 16 MiB).
* Before deciding that part of it, or a spare staging buffer, is still in use, the GPU's real progress is read
  (the value kept on the CPU side is only updated when something waits for the GPU).

The texture cleanup's pressure threshold moves from 2.2 to 2.45 GiB to make room for the bigger stream buffer.

## Shader builds (build 17)

With asynchronous shaders off, a draw that needs a new pipeline stops everything until the pipeline is built. Eden
builds pipelines on background threads (lower priority, power-efficiency hint, usually the little cores); in the
build 16 log the Vulkan worker waited 55 to 224 ms each time. With asynchronous shaders off, Doris runs the builders
at normal priority on the performance cores. (With asynchronous shaders on, nothing waits for them, and they stay in
the background as in Eden.)

## Texture cleanup

Eden's texture garbage collector, as the build 15 log shows it in *Tears of the Kingdom*:

* Its threshold is 1.6 GiB of GPU memory, and the game sits just above it (1725 MiB for most of the session). Above
  the threshold every texture unused for 25 frames is removed, so it removed 550 to 3600 textures every 10 seconds
  and the game uploaded about as many again.
* Below the threshold it never removes a texture the GPU drew into (one that has to be copied back), so those pile
  up until memory is over it. Build 14 went further and kept them until memory was critical: GPU memory climbed to
  3.5 GiB, then thousands of textures were purged at once. It was reverted in build 15.
* A texture the GPU drew into is copied back to guest memory before removal, and Eden waits for the GPU to finish
  everything queued for each copy (build 15 waited once per pass, still a hitch each time: 63 to 1983 copies in 10
  seconds).

Doris's texture cleanup (build 16, the default):

* Copies back never wait. The copy is recorded and the texture stays; at a later frame, once the GPU has done the
  copy, the data is written to guest memory and the texture removed. If the texture was used, drawn into or written
  by the game's CPU code in the meantime, the removal is called off and the texture kept. At most 64 copies
  (128 MiB) are under way at a time.
* Below the pressure threshold a texture has to be unused for 300 frames (10 seconds) before it goes, GPU drawings
  included, so nothing piles up and nothing the game is still using is thrown out.
* The pressure threshold is 2.45 GiB instead of 1.6 GiB (2.2 GiB in build 16; aggressive cleanup still starts at
  3.2 GiB). Above it, the rules are Eden's (unused for 25 frames).
* Build 17 also called a removal off whenever another texture over the same guest memory was created, removed or
  drawn into before the copy was written back. In the build 17 log that started about 1850 copies back every
  10 seconds (build 16: about 160), most of them called off again, and the GPU was busier. Build 18 is back to
  build 16's rules.

"Eden (as before)" switches back to build 15 (Eden's rules, one GPU wait per pass) without restarting the game.

## Frame generation after a hitch

Eden's frame generation pacer stops generating frames for 1 second after any frame that takes longer than 100 ms
(a shader compile, a loading hitch). With a fixed multiplier, that turned every hitch into a second of half-rate
output. Doris resumes after about 100 ms in fixed-multiplier mode (generation still waits for two steady frames in a
row); the target-rate mode is unchanged.

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
