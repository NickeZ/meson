#!/usr/bin/env python3
"""Wrapper to move built artifacts by cargo

Will move *.a files and files without extension to path given by --outdir.
"""
import sys
import os
import shutil
import subprocess
import json
# import pprint
import argparse

def main(args):
    """Main"""
    parser = argparse.ArgumentParser()
    parser.add_argument('--outdir', nargs='?', default='.')
    parser.add_argument('--target-dir', nargs='?', default='.')

    (known_args, args) = parser.parse_known_args(args)

    env_with_target = os.environ.copy()
    if known_args.target_dir:
        env_with_target['CARGO_TARGET_DIR'] = known_args.target_dir

    cargo_p = subprocess.Popen(
        ['cargo', 'build', '--message-format=json'] + args,
        stdout=subprocess.PIPE,
        env=env_with_target,
    )

    output = cargo_p.stdout.read().decode('utf-8')

    for line in output.strip().split('\n'):
        crate = []
        try:
            crate = json.loads(line)
        except json.JSONDecodeError as err:
            print("Failed to parse json {}".format(err), file=sys.stderr)
        # pprint.pprint(crate)
        if 'reason' not in crate:
            continue
        if 'filenames' not in crate:
            continue
        if crate['reason'] == 'compiler-artifact':
            for name in crate['filenames']:
                dirname = os.path.dirname(name)
                basename = os.path.basename(name)
                target_name = os.path.join(known_args.outdir, basename)
                (stem, extension) = os.path.splitext(basename)
                dfile = os.path.join(dirname, stem + '.d')
                if not extension:
                    # Built an executable
                    if basename == 'build-script-build':
                        pass
                        # TODO: Do something with build scripts?
                    else:
                        shutil.move(name, target_name)
                        update_d_file(dfile, name, target_name)
                elif extension in ['.a', '.so', '.dll']:
                    # Built a library
                    shutil.move(name, target_name)
                    update_d_file(dfile, name, target_name)
                elif extension == '.d':
                    print('yay')


def update_d_file(dfile, old, new):
    """Update d-file in-place"""
    old = old.replace(' ', '\\ ')
    new = new.replace(' ', '\\ ')
    content = ''
    with open(dfile) as dfile_r:
        content = dfile_r.read()
        content = content.replace(old, new)
    with open(dfile, 'w') as dfile_w:
        dfile_w.write(content)



if __name__ == '__main__':
    main(sys.argv[1:])
