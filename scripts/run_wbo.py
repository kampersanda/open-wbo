#!/usr/bin/env python3

import os
import subprocess
import sys
import concurrent.futures
from argparse import ArgumentParser
import platform
import pathlib


def run_command(cmd, infn):
    print(cmd)
    output = subprocess.run(cmd, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, encoding='utf-8', shell=True)
    return cmd, output.stdout, infn


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('-e', '--exe_cmd', required=True, type=str)
    parser.add_argument('-d', '--data_list', required=True, type=str)
    parser.add_argument('-w', '--max_workers', default=1, type=int)
    args = parser.parse_args()

    executor = concurrent.futures.ThreadPoolExecutor(
        max_workers=args.max_workers)
    futures = []

    time_opt = ''
    if platform.system() == 'Darwin':
        time_opt = '-l'
    elif platform.system() == 'Linux':
        time_opt = '--verbose'
    else:
        print("invalid platform")
        exit()

    exe_cmd = args.exe_cmd
    exe_path = pathlib.Path(exe_cmd)

    if not exe_path.is_absolute():
        exe_cmd = './' + exe_cmd

    for infn in open(args.data_list):
        infn = infn.rstrip()
        cmd = '/usr/bin/time {opt} {exe} -algorithm=4 {infn}'.format(
            opt=time_opt, exe=exe_cmd, infn=infn)
        futures.append(executor.submit(run_command, cmd, infn))

    rets = []
    for future in concurrent.futures.as_completed(futures):
        cmd, stdout, infn = future.result()
        open('{}.stdout'.format(infn), 'w').write(cmd + '\n' + stdout)

    executor.shutdown()
