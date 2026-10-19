#!/usr/bin/env python3
"""Boot Nexora Live ISO under QEMU and require systemd service signal on COM1."""
import pathlib
import subprocess
import sys
import tempfile
import time

if len(sys.argv) != 2:
    raise SystemExit("Usage: python3 tests/boot-live.py path/to/Nexora.iso")
iso = pathlib.Path(sys.argv[1]).resolve()
if not iso.is_file() or iso.stat().st_size < 100_000_000:
    raise SystemExit("ISO file missing or unexpectedly small")
with tempfile.TemporaryDirectory(prefix="nexora-boot-") as d:
    log = pathlib.Path(d) / "serial.log"
    cmd = [
        "qemu-system-x86_64", "-machine", "q35,accel=tcg", "-cpu", "max",
        "-m", "2048", "-smp", "2", "-boot", "d", "-cdrom", str(iso),
        "-display", "none", "-vga", "std", "-serial", f"file:{log}",
        "-monitor", "none", "-no-reboot", "-no-shutdown", "-nic", "none",
    ]
    print("Launching BIOS ISO smoke test in QEMU", flush=True)
    p = subprocess.Popen(cmd, stderr=subprocess.PIPE)
    try:
        end = time.monotonic() + 240
        while time.monotonic() < end:
            data = log.read_bytes() if log.exists() else b""
            if b"NEXORA_LIVE_BOOT_OK" in data:
                print("PASS: systemd started in Live ISO, verified via COM1", flush=True)
                break
            if p.poll() is not None:
                raise RuntimeError(f"QEMU exited unexpectedly: {p.returncode}")
            time.sleep(2)
        else:
            raise RuntimeError(
                "Live boot marker not observed in QEMU before timeout. "
                + f"Serial tail: {data[-1500:]!r}"
            )
    finally:
        p.terminate()
        try:
            p.wait(timeout=10)
        except subprocess.TimeoutExpired:
            p.kill()
            p.wait()
