# Eden (Doris)

An Android build for the AYN Thor Pro that updates the existing Doris app.

The current build starts from Eden nightly **7a6d055094**, retaining Doris's
package (`dev.eden.eden_doris`), icon and signing key. Its only native performance
change reduces unnecessary Vulkan worker wake-ups. Earlier Doris graphics
experiments and the broad Lun patch groups are excluded.

Use the existing **Turnip Gen8 V38** driver and the same per-game and UltraCam
settings as the working nightly. The APK does not install a driver or copy
settings from another Eden installation.

Install the new APK over Doris without uninstalling it. The build validates the
package, signing certificate and increasing version code against Doris 40.
Official Eden and the separate nightly app are unaffected.

This is a candidate for testing: no FPS gain or absence of graphics regressions
has been established on the Thor. See [build details and validation](nightly/README.md).

The workflow in `.github/workflows/build.yml` applies only `nightly/patches/` to
the exact revision in `nightly/base.json`. Historical `patches/`, `variants/`,
`UPSTREAM`, `RELEASE` and `driver/` remain for reference and are not part of this APK.

Eden and these patches are GPL-3.0-or-later. No games, console keys or firmware are included.
