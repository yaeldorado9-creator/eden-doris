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

## How it is built

* `UPSTREAM` pins the official Eden commit (from the [GitHub mirror](https://github.com/eden-emulator/mirror)).
* `patches/` holds every Doris change as a git patch, applied in order on top of that commit.
* Each push to `main` runs [the workflow](.github/workflows/build.yml), which builds the `doris` flavor and publishes
  the APK as a release named `doris-<number>`. Later builds have a higher version code and the same signature, so each
  one installs as an update of the previous Doris.

No game files, keys or firmware are in this repository or in its releases.

## License

Eden is GPL-3.0-or-later; so are these patches. See the upstream repository for the full license and credits.
