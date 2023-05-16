#!/usr/bin/env python3
#
# CISA2390 Cisco Syslog/config Backup Script
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

import json
from netmiko import ConnectHandler


def load_device(conf, ip) -> Dict:
    with open(conf) as f:
        device = json.load(f)
    device["ip"] = ip
    return device


if __name__ == "__main__":
    ip_addresses = json.load("ip_addresses.json")
    for ip in ip_addresses:
        device = load_device("cisco-backup.json", ip)
        ssh_connection = ConnectHandler(**device)
        ssh_connection.enable()
        ssh_connection.send_command(f"copy startup-config scp://172.16.37.11//home/cisco/startup-config-{ip}")
        ssh_connection.disconnect()
