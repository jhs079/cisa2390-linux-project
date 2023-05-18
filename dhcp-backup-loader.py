#!/usr/bin/env python3
#
# CISA2390 Linux Fallback DHCP Controller Script
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

from time import sleep
import subprocess


class DHCPFallbackController():
    def __init__(self):
        disable_dhcp_service_cmd = "systemctl stop dhcpd"
        try:
            status = subprocess.run(disable_dhcp_service_cmd.split())
        except subprocess.CalledProcessError as e:
            status = e
        return status.returncode

    disable_dhcp_service_cmd = "systemctl stop dhcpd"
    enable_dhcp_service_cmd = "systemctl start dhcpd"

    backup_dhcp_status = False
    dhcp_down_wait_count = 0

    def toggle_dhcp(self, enable=False):
        try:
            status = subprocess.run(self.disable_dhcp_service_cmd if not enable else self.enable_dhcp_service_cmd)
        except subprocess.CalledProcessError as e:
            status = e
        return status.returncode

    def check_primary_dhcp(self):
        primary_dhcp_status_cmd = "ping -c 1 172.16.18.1"
        try:
            subprocess.run(primary_dhcp_status_cmd.split())
        except subprocess.CalledProcessError:
            self.dhcp_down_wait_count += 1
            print(f"DHCP server FAILED to respond to ping. Number of tries: {self.dhcp_down_wait_count}")
            if self.dhcp_down_wait_count == 3:
                print("Reached max number of retries! Backup DHCP server starting")
                self.toggle_dhcp(enable=True)
                self.backup_dhcp_status = True
                return
        if self.backup_dhcp_status:
            self.dhcp_down_wait_count = 0
            print("DHCP server is back up! Powering down backup DHCP.")
            self.toggle_dhcp(enable=False)
            self.backup_dhcp_status = False


if __name__ == "__main__":
    controller = DHCPFallbackController()
    while True:
        sleep(60)
        controller.check_primary_dhcp()
