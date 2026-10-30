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

`patches/0001` is that rebuild (the "as is" zip). Further patches are Doris changes:

- **0002**: for Eden, each render pass with 5+ draws is timed on the GPU in both SYSMEM and GMEM modes and the
  faster mode is used (Turnip's profiled autotuner) instead of the bandwidth estimate. The driver writes
  `log/apex_doris.txt` in Eden's folder every 10 s: GPU time of the timed render passes, SYSMEM vs GMEM, and the
  passes that cost the most with both modes' averages.

- **0003** (separate zip, `-apexfix`): Apex's own TotK rule (#8: prefer GMEM, ignore the fragment shader's depth
  direction) switched on for Eden by matching Eden's engine name. Not combined with 0002 (both set the render mode
  choice). Eden's shaders declare no depth direction, so in practice this is "GMEM for every render pass with 5+
  draws".

Built by `.github/workflows/driver.yml` into a release `apex-doris-<n>`.
