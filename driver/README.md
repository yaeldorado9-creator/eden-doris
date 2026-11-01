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

`patches/0001` is that rebuild (the "as is" zip). `patches/0002`-`0003` are the Doris driver for TotK on Eden (the main
zip); everything in them applies to Eden only (engine name `yuzu Emulator`):

- **32-bit color images stay tiled.** Eden gives every 32-bit color image a view format list with all 19 formats
  of its size class, BGRA8 among them; on A740 (a7xx gen2) Turnip makes any image whose list mixes swapped and
  unswapped formats LINEAR, so all of TotK's 32-bit render targets and textures were drawn and sampled untiled.
  They are now tiled (still without UBWC). R8G8 vs R16 reinterpretation still goes linear. (0002)
- **Render mode measured per pass:** each render pass with 5+ draws is timed on the GPU in SYSMEM and GMEM and
  the faster one is used; GMEM only when at least 15% faster (the CCU switch is paid outside the timed pass), and
  the choice is locked after 10 samples per mode and 10 s, for passes from 0.15 ms. (0002)
- **No LRZ** (the coarse block depth cull), as `TU_DEBUG=nolrz`. (0003)

Driver 10 tried the other way round, and its patches are in the history: real GPU barriers for Eden plus every
render pass in GMEM (Apex's TOTK rule; of its two options only `prefer_gmem` changes anything in Eden, because
Eden's depth-writing fragment shaders declare no depth direction). In a stock Eden: driver 9 (measured, mostly
SYSMEM) had no distant flicker but square blocks of black, flickering ground; Apex Doris 3 "apexfix" and driver 10
(every pass in GMEM) had no black squares but low fps and strong distant flicker, with or without the barriers.
So the measured render modes stay and LRZ, which culls in blocks, goes.

How it got there (builds 3 to 8 carried GPU reports; the history has them): the reports showed the main
render passes at about 9-10 ms of a 25 ms frame, the 32-bit images linear, small passes and the 1080p output
(FSR, frame generation) as the rest. In Eden (Doris) builds of that time, Apex's own TotK rule (prefer GMEM) fixed
neither the grass nor the ground texture switching.

Built by `.github/workflows/driver.yml` into a release `apex-doris-<n>`.
