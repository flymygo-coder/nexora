#!/usr/bin/env python3
"""Boot Nexora ISO in QEMU and preserve screenshots on failure."""
import pathlib, socket, subprocess, sys, tempfile, time
from PIL import Image

if len(sys.argv) != 2:
    raise SystemExit("Usage: boot-live.py ISO_PATH")
iso=pathlib.Path(sys.argv[1]).resolve()
assert iso.is_file() and iso.stat().st_size>100_000_000
out=pathlib.Path("artifacts/live-boot").resolve()
out.mkdir(parents=True, exist_ok=True)
serial=out/"serial.log"
serial.unlink(missing_ok=True)
with tempfile.TemporaryDirectory() as tmp:
    monitor=pathlib.Path(tmp)/"monitor.sock"
    err=(out/"qemu-stderr.log").open("wb")
    cmd=["qemu-system-x86_64","-machine","q35,accel=tcg","-m","2048","-smp","2",
         "-boot","d","-cdrom",str(iso),"-vga","std","-display","none",
         "-serial",f"file:{serial}","-monitor",f"unix:{monitor},server,nowait",
         "-no-reboot","-nic","none"]
    p=subprocess.Popen(cmd,stdout=subprocess.DEVNULL,stderr=err)
    def send(command):
        try:
            with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as s:
                s.settimeout(2);s.connect(str(monitor))
                s.sendall((command+"\n").encode())
            return True
        except (OSError,socket.timeout) as e:
            print("QEMU monitor:",e,flush=True);return False
    def shot(stem):
        ppm=out/(stem+".ppm")
        if send(f"screendump {ppm}"):
            time.sleep(2)
            if ppm.is_file():
                im=Image.open(ppm).convert("RGB")
                im.save(out/(stem+".png"))
                print("Captured",stem,im.size,flush=True)
                ppm.unlink(missing_ok=True)
    try:
        passed=False
        begin=time.monotonic()
        checkpoints={30:"early",90:"middle",165:"late"}
        while time.monotonic()-begin<200:
            data=serial.read_bytes() if serial.exists() else b""
            if b"NEXORA_LIVE_BOOT_OK" in data:
                passed=True;shot("boot-success");break
            if p.poll() is not None:break
            t=time.monotonic()-begin
            for threshold,name in list(checkpoints.items()):
                if t>threshold:
                    shot(name)
                    if name=="early":send("sendkey ret")
                    del checkpoints[threshold]
            time.sleep(2)
        if not passed:
            shot("boot-failed")
            raise RuntimeError("Live boot marker not observed; serial tail: "+repr(data[-1000:]))
        print("PASS: Nexora Live reached multi-user state",flush=True)
    finally:
        p.terminate()
        try:p.wait(timeout=8)
        except subprocess.TimeoutExpired:p.kill();p.wait()
        err.close()
