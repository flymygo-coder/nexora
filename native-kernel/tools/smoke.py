#!/usr/bin/env python3
"""Boot ISO in QEMU, verify serial markers, capture a framebuffer screenshot."""
from pathlib import Path
import socket, subprocess, time
from PIL import Image
root=Path(__file__).resolve().parent.parent
build=root/'build'
iso=build/'Nexora_Kernel_0.1.iso'
log=build/'serial.log'
monitor=build/'monitor.sock'
ppm=build/'screen.ppm'
png=build/'Nexora_Kernel_QEMU.png'
for path in (log,monitor,ppm,png): path.unlink(missing_ok=True)
cmd=['qemu-system-i386','-m','256M','-vga','std','-cdrom',str(iso),'-boot','d','-serial',f'file:{log}','-display','none','-monitor',f'unix:{monitor},server,nowait','-no-reboot','-no-shutdown']
print('Launching QEMU',flush=True)
p=subprocess.Popen(cmd,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
try:
    deadline=time.monotonic()+45
    while time.monotonic()<deadline:
        data=log.read_bytes() if log.exists() else b''
        if b'NEXORA_KERNEL_BOOT_OK' in data: break
        if p.poll() is not None: raise RuntimeError(f'QEMU exited with {p.returncode}; serial={data[-400:]}')
        time.sleep(.5)
    else: raise RuntimeError('Kernel boot marker not found: '+repr(data[-400:]))
    if b'NEXORA_SELFTEST_OK' not in data: raise RuntimeError('Memory self-test failed')
    print('Kernel boot and memory self-test OK',flush=True)
    with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as s:
        s.settimeout(6)
        s.connect(str(monitor))
        s.sendall(f'screendump {ppm}\n'.encode())
        time.sleep(2)
    if not ppm.exists() or ppm.stat().st_size<10000: raise RuntimeError('Screenshot unavailable')
    image=Image.open(ppm).convert('RGB')
    if image.width<800 or image.height<600:raise RuntimeError('Framebuffer resolution too small')
    if len(set(image.resize((48,32)).getdata()))<15:raise RuntimeError('Framebuffer appears blank')
    image.save(png)
    print('Framebuffer screenshot:',png,image.size,flush=True)
finally:
    p.terminate()
    try:p.wait(timeout=5)
    except subprocess.TimeoutExpired:p.kill();p.wait()
