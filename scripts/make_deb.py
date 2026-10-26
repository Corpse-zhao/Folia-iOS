#!/usr/bin/env python3
"""Build a roothide-compatible deb from an .app bundle (manual ar builder, no dpkg needed)."""
import gzip, io, os, sys, tarfile, time

def add_tar(t, path, arcname, mode=None):
    if os.path.isdir(path):
        ti = tarfile.TarInfo(arcname + "/")
        ti.type = tarfile.DIRTYPE
        ti.mode = 0o755
        ti.mtime = int(time.time())
        ti.uid = ti.gid = 0
        ti.uname = ti.gname = "root"
        t.addfile(ti)
        for n in sorted(os.listdir(path)):
            add_tar(t, os.path.join(path, n), arcname + "/" + n, mode)
    else:
        data = open(path, "rb").read()
        ti = tarfile.TarInfo(arcname)
        ti.size = len(data)
        ti.mode = mode if mode is not None else 0o644
        ti.mtime = int(time.time())
        ti.uid = ti.gid = 0
        ti.uname = ti.gname = "root"
        t.addfile(ti, io.BytesIO(data))

def make_tar_gz(entries):
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w") as t:
        for src, arc, mode in entries:
            add_tar(t, src, arc, mode)
    return gzip.compress(buf.getvalue())

def ar_member(name, body):
    assert len(name) <= 16
    hdr = name.ljust(16).encode() + b"0".ljust(12) + b"0".ljust(6) + b"0".ljust(6) + b"100644".ljust(8) + str(len(body)).ljust(10).encode() + b"\x60\n"
    if len(body) % 2:
        body += b"\n"
    return hdr + body

CONTROL = """Package: com.corpsezhao.folia
Name: Folia
Version: 1.0.0
Architecture: iphoneos-arm64e
Description: Folia music player - iOS web shell (Capacitor)
Section: Applications
Maintainer: Corpse-zhao
Author: Corpse-zhao
Depends: firmware (>= 15.0)
"""

POSTINST = """#!/bin/sh
uicache -p /Applications/Folia.app 2>/dev/null || uicache -a 2>/dev/null || true
exit 0
"""

def main():
    app_dir, out = sys.argv[1], sys.argv[2]
    assert os.path.isdir(app_dir), app_dir
    # control tarball
    cbuf = io.BytesIO()
    with tarfile.open(fileobj=cbuf, mode="w") as t:
        data = CONTROL.encode()
        ti = tarfile.TarInfo("control"); ti.size = len(data); ti.mode = 0o644
        ti.mtime = int(time.time()); ti.uid = ti.gid = 0; ti.uname = ti.gname = "root"
        t.addfile(ti, io.BytesIO(data))
        pdata = POSTINST.encode()
        ti = tarfile.TarInfo("postinst"); ti.size = len(pdata); ti.mode = 0o755
        ti.mtime = int(time.time()); ti.uid = ti.gid = 0; ti.uname = ti.gname = "root"
        t.addfile(ti, io.BytesIO(pdata))
    control_gz = gzip.compress(cbuf.getvalue())

    # data tarball: Applications/Folia.app
    data_gz = make_tar_gz([(app_dir, "Applications/Folia.app", None)])

    with open(out, "wb") as f:
        f.write(b"!<arch>\n")
        f.write(ar_member("debian-binary", b"2.0\n"))
        f.write(ar_member("control.tar.gz", control_gz))
        f.write(ar_member("data.tar.gz", data_gz))
    print("deb written:", out, os.path.getsize(out), "bytes")

if __name__ == "__main__":
    main()
