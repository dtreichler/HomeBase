import os.path
import glob
import os
import subprocess

def get_module_fonts():
    dirname = os.path.dirname(__file__)
    fontfiles = glob.glob(os.path.join(dirname, '*.[ot]tf'))
    fonts = {}
    for f in fontfiles:
        filename = os.path.basename(f)
        (root,ext) = os.path.splitext(filename)
        fonts[root] = f
    return fonts

def get_system_fonts():
    sp = subprocess.Popen('fc-list', stdout=subprocess.PIPE)
    out = sp.stdout.read().decode('utf-8')
    fontfiles = [x.split(':')[0] for x in out.strip().split('\n')]
    fonts = {}
    for f in fontfiles:
        print(f)
        filename = os.path.basename(f)
        (root,ext) = os.path.splitext(filename)
        fonts[root] = f
    return fonts

mod_fonts = get_module_fonts()
sys_fonts = get_system_fonts()

fonts = sys_fonts.copy()
fonts.update(mod_fonts)


