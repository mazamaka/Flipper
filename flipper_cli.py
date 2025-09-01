#!/usr/bin/env python3
import glob
import os
import signal
import subprocess
import sys
import time
from typing import Optional
import serial


class Port:
    @staticmethod
    def detect() -> str:
        x = sorted(glob.glob("/dev/serial/by-id/*Flipper*if00"))
        if x:
            return os.path.realpath(x[0])
        y = sorted(glob.glob("/dev/ttyACM*"))
        if y:
            return y[0]
        raise RuntimeError("Порт Flipper не найден")

    @staticmethod
    def free(dev: str):
        for cmd in (["lsof", "-t", dev], ["fuser", dev]):
            try:
                p = subprocess.check_output(cmd, text=True).split()
                for pid in p:
                    try:
                        os.kill(int(pid), signal.SIGTERM)
                    except ProcessLookupError:
                        pass
            except subprocess.CalledProcessError:
                pass
        os.system("pkill -f qFlipper >/dev/null 2>&1")
        time.sleep(0.2)


class Flipper:
    def __init__(self, port: Optional[str] = None, baud: int = 230400, timeout: float = 1.0):
        self.port = port or Port.detect()
        self.baud = baud
        self.timeout = timeout
        self.ser: Optional[serial.Serial] = None

    def __enter__(self):
        try:
            self.ser = serial.Serial(self.port, self.baud, timeout=self.timeout, write_timeout=self.timeout, exclusive=True)
        except serial.SerialException:
            Port.free(self.port)
            self.ser = serial.Serial(self.port, self.baud, timeout=self.timeout, write_timeout=self.timeout, exclusive=True)
        return self

    def __exit__(self, *a):
        if self.ser and self.ser.is_open:
            self.ser.close()

    def cmd(self, s: str, read_sec: float = 2.0) -> str:
        self.ser.reset_input_buffer()
        self.ser.write((s + "\r\n").encode())
        self.ser.flush()
        end = time.time() + read_sec
        buf = bytearray()
        while time.time() < end:
            n = self.ser.in_waiting
            b = self.ser.read(n or 1)
            if b:
                buf.extend(b)
            else:
                time.sleep(0.05)
        out = buf.decode(errors="ignore").strip()
        lines = [x for x in out.splitlines() if x and not x.startswith(("Welcome to Flipper", "Read the manual", "Run `help`", "Firmware version:", ">:"))]
        return lines[-1] if lines else ""

    def cmd_all(self, s: str, read_sec: float = 2.0) -> list[str]:
        """Send a command and return all filtered output lines as a list."""
        self.ser.reset_input_buffer()
        self.ser.write((s + "\r\n").encode())
        self.ser.flush()
        end = time.time() + read_sec
        buf = bytearray()
        while time.time() < end:
            n = self.ser.in_waiting
            b = self.ser.read(n or 1)
            if b:
                buf.extend(b)
            else:
                time.sleep(0.05)
        out = buf.decode(errors="ignore").strip()
        lines = [x for x in out.splitlines() if x and not x.startswith(("Welcome to Flipper", "Read the manual", "Run `help`", "Firmware version:", ">:"))]
        return lines

    def sub_from_file(self, path: str, repeat: int = 1, device: int = 0) -> str:
        return self.cmd(f"subghz tx_from_file {path} {repeat} {device}", read_sec=3.0)


if __name__ == "__main__":
    # TARGET = "/ext/subghz/Win_down.sub"
    # TARGET = "/ext/subghz/Win_down_2.sub"
    TARGET = "/ext/subghz/Win_stop.sub"
    # TARGET = "/ext/subghz/Win_stop_2.sub"
    # TARGET = "/ext/subghz/Win_up.sub"
    # TARGET = "/ext/subghz/Win_up_2.sub"
    # TARGET = "/ext/subghz/B_open.sub"
    # TARGET = "/ext/subghz/B_close.sub"

    REPEAT = 1
    DEVICE = 0

    with Flipper() as f:
        res = f.sub_from_file(TARGET, REPEAT, DEVICE)
        print(res or "OK")
