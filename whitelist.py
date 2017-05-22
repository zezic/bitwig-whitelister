import argparse
import subprocess
import os
from utils import (
    compress_linenumbers,
    get_key_listing,
    get_rec_listing,
    remove_last_linenumbertable
)

UNPACKED_DIR = './unpacked'
DISASSEMBLED_DIR = './disassembled'
MATH_UUID_PART = '6146bcd7'

parser = argparse.ArgumentParser(description='Add custom devices and modulators.')
parser.add_argument('--device', action='append')
parser.add_argument('--modulator', action='append')
parser.add_argument('--jar', action='store')
parser.add_argument('--output', action='store')
args = parser.parse_args()

devices_in = args.device or []
modulators_in = args.modulator or []
jar = args.jar
output = args.output

print(' Recieved devices: '.center(80, '-'))
print('\n'.join(devices_in))
print(' Recieved modulators: '.center(80, '-'))
print('\n'.join(modulators_in))
print(' Working... '.center(80, '-'))

unpack_jar_cmd = ['unzip', '-o', jar, '-d', UNPACKED_DIR]
subprocess.check_output(unpack_jar_cmd)

hardcode_class_file = subprocess.check_output([
    'grep', '-rl', MATH_UUID_PART, UNPACKED_DIR
]).decode('utf-8').strip()

disassembly_class_cmd = [
    'python2', 'libs/krakatau/disassemble.py',
    '-out', DISASSEMBLED_DIR,
    hardcode_class_file
]

disassembly_output = subprocess.check_output(disassembly_class_cmd)
disassembly_output = disassembly_output.decode('utf-8')

hardcode_j_file = ''
for line in disassembly_output.split('\n'):
    if 'written' in line:
        hardcode_j_file = line.split('Class written to ')[1].strip()
        break

with open(hardcode_j_file, 'r') as f:
    hardcode = f.readlines()

for idx, line in enumerate(hardcode):
    if '.field public static' in line:
        VARS_OFFSET = idx
        break

extra_vars = ['illegal{}'.format(idx)
              for idx in
              range(len(devices_in) + len(modulators_in))]

vars_lines = ['.field public static {} Ljava/util/UUID; \n'.format(var)
              for var in extra_vars]

extra_vars.reverse()

hardcode = hardcode[:VARS_OFFSET] + vars_lines + hardcode[VARS_OFFSET:]

searching_for_recs = False
RECS_START = None
for idx, line in enumerate(hardcode):
    if not searching_for_recs:
        if '.field public static final' in line and 'Ljava/util/Map;' in line:
            HASHMAP_NAME = line.split('final ')[1].split(' ')[0]
        if '.stack stack_1 Integer' in line:
            KEYS_START = idx + 2
        if 'new java/util/HashMap' in line:
            KEYS_END = idx
            CLASS_NAME = hardcode[idx - 1].split('/core/')[1].split(' ')[0]
            searching_for_recs = True
    else:
        if not RECS_START and 'getstatic Field com/bitwig/flt/packaging/core' in line:
            RECS_START = idx
        if RECS_START and '.linenumbertable' in line:
            RECS_END = idx - 2
            # break

keys, keys_last_number = compress_linenumbers(hardcode[KEYS_START:KEYS_END])
recs, recs_last_number = compress_linenumbers(hardcode[RECS_START:RECS_END])

all_plugins_in = []
for device in devices_in:
    all_plugins_in.append({
        "type": "device",
        "data": device
    })
for mod in modulators_in:
    all_plugins_in.append({
        "type": "modulator",
        "data": mod
    })

for plugin in all_plugins_in:
    uuid = plugin.get('data').split(':')[0]
    filename = '{0}s/{1}.bw{0}'.format(plugin.get('type'), plugin.get('data').split(':')[1])
    key_listing = get_key_listing(
        uuid=uuid,
        var=extra_vars.pop(),
        last_number=keys_last_number,
        class_name=CLASS_NAME
    )
    rec_listing = get_rec_listing(
        uuid=uuid,
        filename=filename,
        last_number=recs_last_number,
        class_name=CLASS_NAME,
        hashmap_name=HASHMAP_NAME
    )
    keys_last_number = keys_last_number + len(key_listing)
    recs_last_number = recs_last_number + len(rec_listing)
    keys = keys + key_listing
    recs = recs + rec_listing

hardcode = hardcode[:KEYS_START] + keys + hardcode[KEYS_END:RECS_START] + recs + hardcode[RECS_END:]
hardcode = remove_last_linenumbertable(hardcode)

with open(hardcode_j_file, 'w') as f:
    f.writelines(hardcode)

assembly_class_cmd = [
    'python2', 'libs/krakatau/assemble.py',
    '-out', UNPACKED_DIR,
    hardcode_j_file
]

assembly_output = subprocess.check_output(assembly_class_cmd)
os.chdir(UNPACKED_DIR)
pack_jar_cmd = 'jar -cf ../' + output + ' *'
os.system(pack_jar_cmd)
os.chdir('..')
print(' Done. '.center(80, '-'))
