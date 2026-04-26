#!/usr/bin/env python3

import os
import glob
import subprocess

print("Purge unnecessary bits")
subprocess.run("scripts/delete_pycaches.sh", shell=True, check=True)
print("")

print("Recreate plugin definitions")
subprocess.run(["python3", "scripts/create_plugin_definitions.py", "src"], check=True)
print("")

print("Packaging plugins:")
for plugin_dir in [os.path.basename(x) for x in glob.glob('src/*')]:
    ZIPFILE = f"{plugin_dir}.zip"
    cmd = f"cd src; zip -r {ZIPFILE} {plugin_dir} > /dev/null; cp -f {ZIPFILE} ../plugins; rm -f {ZIPFILE}"
    subprocess.run(cmd, shell=True, check=True)
    print(f" - Plugin {plugin_dir} packaged successfully")
print("")
subprocess.run(["python3", "./scripts/build_plugin_index.py"], check=True)
print("")
