# Apex Doris (Turnip driver)

Balemuni's **Apex v2 Ultimate** Turnip driver rebuilt from source, as the base for driver-side work on
*Tears of the Kingdom* in Eden (Doris). Apex's repository has no source, so its changes were recovered from its
`vulkan.freedreno.so` (V2 release, `Balemuni_Apex_v2_ULTIMATE_SD8Gen2.zip`, sha256 810567af…):

- Mesa main `b9a2bf372b` (26.3.0-devel), NDK r28, Android API 30, 16 KiB pages, ARMv8.2 code tuned for Cortex-X3.
- driconf (dumped from the binary's tables): for emulator engines (Eden reports the engine `yuzu Emulator`) fast
  border colors for undefined formats, D3D texture-coordinate rounding, out-of-bounds indirect UBO loads allowed,
  DONT_CARE treated as LOAD; rules for rpcs3 and xenia; and TOTK/BOTW rules matched against the *application*
  name (`.*(totk).*`), which Eden reports as `yuzu Emulator`, so **they never applied in Eden**.
- ir3 global code motion on by default (`GCM=1`), 512 KiB pipeline and kgsl profiling suballocators, 4 GiB disk
  shader cache.

`patches/0001` is that rebuild (the "as is" zip). `patches/0002`-`0004` are the Doris driver for TotK on Eden; everything
in them applies to Eden only (engine name `yuzu Emulator`). The "fast" zip has 0001-0003, the main zip all four:

- **32-bit color images stay tiled.** Eden gives every 32-bit color image a view format list with all 19 formats
  of its size class, BGRA8 among them; on A740 (a7xx gen2) Turnip makes any image whose list mixes swapped and
  unswapped formats LINEAR, so all of TotK's 32-bit render targets and textures were drawn and sampled untiled.
  They are now tiled (still without UBWC). R8G8 vs R16 reinterpretation still goes linear.
- **Render mode measured per pass:** each render pass with 5+ draws is timed on the GPU in SYSMEM and GMEM and
  the faster one is used; GMEM only when at least 15% faster (the CCU switch is paid outside the timed pass), and
  the choice is locked after 10 samples per mode and 10 s, for passes from 0.15 ms. (0002; the main zip replaces
  this with 0004.)
- **Real GPU barriers (0003).** Eden turns the game's "wait until the GPU is done" points into an event wait with no
  memory barrier and puts no barrier after compute work. Every dispatch is now followed by a barrier and every event
  wait is a full memory barrier, the barriers Eden (Doris) build 6 records itself, so they also work in a stock Eden.
- **Every render pass in tile memory (0004)**, Apex's TOTK rule (#8) applied to Eden. Of its two options only
  `prefer_gmem` changes anything in Eden (Eden's depth-writing fragment shaders declare no depth direction, so LRZ is
  already off for them). In a stock Eden, Apex Doris 3's "apexfix" zip (this rule, untiled images, no barriers) had no
  black squares on the ground but strong distant flicker; Apex Doris 9 (measured modes, mostly SYSMEM) had no distant
  flicker but black squares. GMEM's binning pass reads geometry before drawing, so without barriers it picks up
  unfinished compute results; 0003 is there for that.

How it got there (builds 3 to 8 carried GPU reports; the history has them): the reports showed the main
render passes at about 9-10 ms of a 25 ms frame, the 32-bit images linear, small passes and the 1080p output
(FSR, frame generation) as the rest. In Eden (Doris) builds of that time, Apex's own TotK rule (prefer GMEM) fixed
neither the grass nor the ground texture switching.

Built by `.github/workflows/driver.yml` into a release `apex-doris-<n>`.
