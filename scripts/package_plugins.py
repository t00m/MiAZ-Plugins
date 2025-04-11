import os
import glob

print("Packaging plugins:")
for plugin_dir in [os.path.basename(x) for x in glob.glob('src/*')]:
    ZIPFILE = f"{plugin_dir}.zip"
    cmd = f"cd src; zip -r {ZIPFILE} {plugin_dir} > /dev/null; cp -f {ZIPFILE} ../plugins; rm -f {ZIPFILE}"
    os.system(cmd)
    print(f" - Plugin {plugin_dir} packaged successfully")
print("")
cmd = "python3 ./scripts/build_plugin_index.py"
os.system(cmd)
print("")

