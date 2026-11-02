import hashlib
import json
from pathlib import Path
import subprocess
import sys

source = Path(sys.argv[1]).resolve()
spec = json.loads((Path(__file__).parent / 'base.json').read_text())

def git(*args):
    return subprocess.check_output(['git', '-C', str(source), *args], text=True).strip()

assert git('rev-parse', 'HEAD') == spec['commit'], 'Wrong Eden base'
assert hashlib.sha256((source / 'src/android/app/debug.keystore').read_bytes()).hexdigest() == spec['signing_keystore_sha256'], 'Signing key changed'
changed = set(git('diff', '--name-only', 'HEAD').splitlines())
changed.update(git('ls-files', '--others', '--exclude-standard').splitlines())
native = {name for name in changed if name.startswith('src/') and not name.startswith('src/android/')}
assert native == {
    'src/video_core/renderer_vulkan/vk_scheduler.cpp',
    'src/video_core/renderer_vulkan/vk_scheduler.h',
}, f'Unexpected native changes: {native}'
android_allowed = {
    'src/android/app/build.gradle.kts',
    'src/android/app/src/main/AndroidManifest.xml',
    'src/android/app/src/main/java/org/yuzu/yuzu_emu/utils/CustomSettingsHandler.kt',
}
assert all(name in native | android_allowed or name.startswith('src/android/app/src/doris/') for name in changed), changed
gradle = (source / 'src/android/app/build.gradle.kts').read_text()
assert 'applicationId = "dev.eden.eden_doris"' in gradle
assert 'System.getenv("DORIS_VERSION_CODE")' in gradle
assert '-DENABLE_UPDATE_CHECKER=OFF' in gradle
subprocess.run(['git', '-C', str(source), 'diff', '--check'], check=True)
print('Pinned base, unchanged signing key and limited native patch scope verified.')
