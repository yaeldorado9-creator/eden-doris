# Without the fixes from newer Eden

Second APK of each release (`Eden-Doris-<n>-no-newer-eden.apk`): `patches/0001` to `0041`, then the patches here,
which are Doris' later changes (`patches/0049` to `0053`) rebased without the fixes carried over from newer Eden in
build 18 (`patches/0042` to `0048`: Eden #4565 TotK dark squares, #4490 and #4531/#4528 copy-back of GPU-written
buffer bytes on NCE writes, #4473 inline upload and macro dirty tracking, #4530 duplicate NCE interrupts, #4551
conditional bindless handles, #4508 subgroup emulation on Qualcomm/Turnip).

Without #4490/#4531 there is no copy-back of GPU-written buffer bytes before the game's writes; the build-19 handling
of GPU-drawn textures on a write fault (kept unless their own bytes change) is kept, on Eden's original invalidation
path (`DorisInvalidateFromFault`).
