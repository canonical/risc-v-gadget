#!/usr/bin/python3
""" Test an image """
""" Usage: python test.py <image> [debug] """

import pexpect
import shutil
import sys
from pathlib import Path

def main():
    image = sys.argv[1]
    debug = (sys.argv[2] == "debug") if len(sys.argv) >= 3 else False

    if debug:
        print("Enabling debug mode.")

    print(f"Setting up EFI variables...")
    vars_src = Path("/usr/share/qemu-efi-riscv64/RISCV_VIRT_VARS.fd")
    vars_dst = Path("RISCV_VIRT_VARS.fd")
    if vars_src.exists():
        shutil.copy(vars_src, vars_dst)
        print(f"Copied {vars_src} to {vars_dst}")
    elif not vars_dst.exists():
        print(f"Error: {vars_src} not found and {vars_dst} not present.", file=sys.stderr)
        sys.exit(1)

    print(f"Testing image '{image}'. Starting qemu...")
    p = pexpect.spawn(
        f'qemu-system-riscv64 '
        f'-cpu rva23s64 '
        f'-machine virt -nographic -m 2048 -smp 4 '
        f'-drive if=pflash,format=raw,unit=0,file=/usr/share/qemu-efi-riscv64/RISCV_VIRT_CODE.fd,readonly=on '
        f'-drive if=pflash,format=raw,unit=1,file=RISCV_VIRT_VARS.fd,readonly=off '
        f'-device virtio-net-device,netdev=eth0 -netdev user,id=eth0 '
        f'-device virtio-rng-pci '
        f'-drive file={image},format=raw,if=virtio'
    )
    
    if debug:
        p.logfile = sys.stdout.buffer
        
    print("Waiting for the virtual machine to boot in qemu...")
    expects = ["Cloud-init v.* finished", "ubuntu login:"]
    found = p.expect(expects, timeout=240)
    print(f"Found '{expects[found]}', waiting for '{expects[1 - found]}'...")
    p.expect(expects[1 - found], timeout=60)
    
    print("Machine initialization done, trying to log in...")
    p.sendline("ubuntu")
    p.expect("Password:")
    p.sendline("ubuntu")
    print("Login information sent ! Waiting for 'change password' prompt...")

    # Change password
    p.expect("Current password:")
    print("Changing password...")
    p.sendline("ubuntu")
    p.expect("New password:")
    p.sendline("again-ubuntu")
    p.expect("Retype new password:")
    p.sendline("again-ubuntu")

    # Shell access
    p.expect("ubuntu@ubuntu:~")
    print("Shell access obtained, image ok.")


if __name__ == '__main__':
    main()
