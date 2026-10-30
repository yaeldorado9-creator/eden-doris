#!/bin/bash
# Builds the Doris Turnip driver for Android (arm64) from Mesa at driver/MESA_COMMIT plus
# driver/patches/*.patch, and packs it for Eden's driver manager (meta.json + vulkan.freedreno.so).
# usage: build.sh <mesa source dir> <android ndk dir> <output dir> <build number> <zip name> <variant label>
set -euo pipefail
MESA=$(realpath "$1"); NDK=$(realpath "$2"); OUT=$(realpath -m "$3"); NUM="$4"; ZIP="$5"; LABEL="$6"
HERE=$(dirname "$(realpath "$0")")
TC=$NDK/toolchains/llvm/prebuilt/linux-x86_64
API=30
CROSS=$OUT/android-aarch64.ini
mkdir -p "$OUT"
LAUNCH=""; command -v ccache >/dev/null && LAUNCH="'ccache', "
# Cortex-X3 tuning on ARMv8.2 code (LSE atomics), as Apex's "universally safe" X3 tuning; no SVE.
CPUFLAGS="'-march=armv8.2-a', '-mtune=cortex-x3', '-mbranch-protection=standard'"
cat > "$CROSS" <<CFG
[binaries]
ar = '$TC/bin/llvm-ar'
c = [${LAUNCH}'$TC/bin/aarch64-linux-android$API-clang']
cpp = [${LAUNCH}'$TC/bin/aarch64-linux-android$API-clang++']
c_ld = 'lld'
cpp_ld = 'lld'
strip = '$TC/bin/llvm-strip'
pkg-config = ['env', 'PKG_CONFIG_LIBDIR=$NDK/pkgconfig', '/usr/bin/pkg-config']

[built-in options]
c_args = [$CPUFLAGS]
cpp_args = [$CPUFLAGS, '-fno-exceptions', '-fno-unwind-tables', '-fno-asynchronous-unwind-tables']
c_link_args = ['-Wl,-z,max-page-size=16384']
cpp_link_args = ['-Wl,-z,max-page-size=16384', '-static-libstdc++']

[host_machine]
system = 'android'
cpu_family = 'aarch64'
cpu = 'armv8'
endian = 'little'
CFG
cd "$MESA"
if [ ! -f "$OUT/build/build.ninja" ]; then
  meson setup "$OUT/build" --cross-file "$CROSS" \
    -Dbuildtype=release -Doptimization=3 -Db_ndebug=true -Dstrip=true \
    -Dplatforms=android -Dplatform-sdk-version=$API -Dandroid-stub=true \
    -Dandroid-libbacktrace=disabled -Dgallium-drivers= -Dvulkan-drivers=freedreno \
    -Dfreedreno-kmds=kgsl -Dvulkan-beta=true -Degl=disabled -Dgles1=disabled -Dgles2=disabled \
    -Dopengl=false -Dglx=disabled -Dllvm=disabled -Dzstd=disabled -Dexpat=disabled \
    -Dvalgrind=disabled -Dlibunwind=disabled -Dlmsensors=disabled -Dgbm=disabled \
    -Dshader-cache=enabled -Db_lto=false
fi
ninja -C "$OUT/build" src/freedreno/vulkan/libvulkan_freedreno.so
PKG=$OUT/pkg; rm -rf "$PKG"; mkdir -p "$PKG"
"$TC/bin/llvm-strip" --strip-all "$OUT/build/src/freedreno/vulkan/libvulkan_freedreno.so" -o "$PKG/vulkan.freedreno.so"
SHA=$(git -C "$MESA" rev-parse --short=10 HEAD)
sed -e "s/@NUM@/$NUM/g" -e "s/@SHA@/$SHA/g" -e "s/@LABEL@/$LABEL/g" "$HERE/meta.json.in" > "$PKG/meta.json"
( cd "$PKG" && rm -f "../$ZIP" && zip -q -9 "../$ZIP" meta.json vulkan.freedreno.so )
echo "built $OUT/$ZIP"
