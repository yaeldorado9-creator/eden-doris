# Doris update based on the working nightly

This build replaces the installed Doris app. It uses Eden commit
`7a6d055094846b7787f9b8c0f238c0c68709f632`, the user's working nightly, and
keeps `dev.eden.eden_doris`, its launcher icon, and its existing signing key.

Only the patches in this directory are applied. The historical `patches/`,
`variants/`, `UPSTREAM`, `RELEASE`, and Apex driver experiments are not used.

The only native change avoids notifying the Vulkan worker or queue-drain
waiters when no such thread is waiting. Queue access and waiter state remain
protected by the same mutex. Command order, queue hand-off frequency, Vulkan
barriers, GPU submissions, shaders, textures, vertex tracking, frame generation,
and CPU affinity retain this nightly's implementation.

The build checks the package, increasing version code, and signing certificate
against Doris 40 before producing an update. Installing it over Doris preserves
Android app data; do not uninstall Doris first. Its existing settings remain,
so match the working nightly's per-game settings, UltraCam configuration and
Turnip Gen8 V38 selection before comparing performance. No driver is bundled.

This is a performance candidate, not a verified FPS improvement. Source checks,
a worker synchronization stress test, and APK validation cannot establish
graphics correctness on the Thor. Compare warmed runs of the same save and
route on Medium Underclock, including water, shadows, distant terrain and
scene transitions. Reject any new visual problem, crash or increased stutter.
