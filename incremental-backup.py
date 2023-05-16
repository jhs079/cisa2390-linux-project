#!/usr/bin/env python3
#
# CISA2390 Linux Incremental Backup RootFS Automation Script
#
# Permission to use, copy, modify, and/or distribute this software for
# any purpose with or without fee is hereby granted.
#
# THE SOFTWARE IS PROVIDED “AS IS” AND THE AUTHOR DISCLAIMS ALL
# WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE
# FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY
# DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN
# AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT
# OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
#


#
# This script aims to have an incremental backup system using rsync.
# With rsync, we are preserving the *entire* rootfs in a specified backup path.
#
# This backup path contains a base, full backup, as well as 6 "incremental" backups,
# which are all hardlinked to the previous incremental backup. So the "base" backup
# is a full copy, the first incremental backup is a full copy that hard links identical
# files to the base, the second is a full copy with hardlinked identical files to
# the first incremental backup, and so on.
#
# Once 7 total backups are reached, the base and the first incremental backups
# will be merged, and the system will proceed to create the next backup.
#
# For now, paths are hardcoded to rootfs as source and /mnt/backup as the backup
# directory. This may be changed to an argv-based system in the future to allow for
# wider usage without having to directly edit this file.
#

import os
import subprocess
import sys


# A subprocess wrapper command.
# Run the command, check output, and if the command failed, immediately exit
# before causing any more damage
def run_command_check_output(command):
    try:
        subprocess.run(command.split(), stderr=subprocess.STDOUT, stdout=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        print("Command failed! Please check backup folder.")
        sys.exit(1)


backup_path = "/mnt/backup"
backup_source = "/"

# first backup is a full base backup
CREATE_BASE = 1
# after first run, there will be 6 incremental backups
CREATE_INCREMENT = 2
# after 6 incremental backups, merge the first and last backup, this will be run most often
MERGE_INCREMENT = 3

print("CISA2390 Linux Incremental Backup RootFS Automation Script")
print("Subject to the 0BSD license\n\n")


action = 0
increment_num = 1

if not os.path.exists(backup_path):
    os.mkdir(backup_path)

for i in [1, 2, 3, 4, 5, 6, 7]:
    if not os.path.isdir(f"{backup_path}/{i}"):
        if i == 1:
            action = CREATE_BASE
        else:
            action = CREATE_INCREMENT
        increment_num = i
        break
    if i == 7:
        increment_num = 7
        action = MERGE_INCREMENT
        break


# copy everything from root
subproc_command = "rsync -arltgdovXASx --exclude /mnt --exclude /tmp"
if action == CREATE_BASE:
    subproc_command = f"{subproc_command} {backup_source} {backup_path}/1"
elif action == CREATE_INCREMENT or action == MERGE_INCREMENT:
    subproc_command = f"{subproc_command} --link-dest {backup_path}/{increment_num - 1} {backup_source} {backup_path}/{increment_num}"


process = None

# merge increment before making another one
if action == MERGE_INCREMENT:
    print("Reached 7 backups, merging base and increment 1...")
    run_command_check_output(f"rm -rf {backup_path}/1")
    for i in [2, 3, 4, 5, 6, 7]:
        run_command_check_output(f"mv -f {backup_path}/{i} {backup_path}/{i-1}")


if action == CREATE_BASE:
    print("Creating initial backup...")
else:
    print(f"Creating incremental backup {increment_num}...")


# run the backup
run_command_check_output(subproc_command)

print("Completed!")
sys.exit(0)
