import json
import re
from pathlib import Path
import subprocess
import sys

tools, previous, current = map(Path, sys.argv[1:])
spec = json.loads((Path(__file__).parent / 'base.json').read_text())

def inspect(apk):
    badging = subprocess.check_output([str(tools / 'aapt'), 'dump', 'badging', str(apk)], text=True)
    package = re.search(r"package: name='([^']+)' versionCode='(\d+)'", badging)
    assert package, f'No package information in {apk}'
    signature = subprocess.check_output([str(tools / 'apksigner'), 'verify', '--verbose', '--print-certs', str(apk)], text=True)
    certificates = re.findall(r'Signer #\d+ certificate SHA-256 digest: ([0-9a-f]+)', signature)
    assert certificates, f'No signing certificate in {apk}'
    return package[1], int(package[2]), certificates

old, new = inspect(previous), inspect(current)
assert old[0] == new[0] == spec['package'], f'Package mismatch: {old[0]}, {new[0]}'
assert new[1] > old[1], f'Update version must increase: {old[1]} -> {new[1]}'
assert new[2] == old[2], 'Signing certificate differs; Android would reject the update'
print(f'Update verified: {new[0]}, versionCode {old[1]} -> {new[1]}, identical signer.')
