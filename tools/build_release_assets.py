from __future__ import annotations

import argparse
import hashlib
import shutil
import subprocess
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def split_file(path: Path, part_size: int) -> list[Path]:
    parts: list[Path] = []
    for old_part in path.parent.glob(path.name + ".part*"):
        old_part.unlink()

    with path.open("rb") as src:
        index = 1
        while True:
            chunk = src.read(part_size)
            if not chunk:
                break
            part = path.with_name(f"{path.name}.part{index:02d}")
            part.write_bytes(chunk)
            parts.append(part)
            index += 1
    return parts


def combine_parts(parts: list[Path], output: Path) -> None:
    with output.open("wb") as dst:
        for part in parts:
            with part.open("rb") as src:
                shutil.copyfileobj(src, dst, 1024 * 1024)


def run_7z_test(seven_zip: Path, archive: Path) -> None:
    result = subprocess.run(
        [str(seven_zip), "t", str(archive)],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    print(result.stdout)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--zip", required=True, type=Path)
    parser.add_argument("--part-size-mb", default=1900, type=int)
    parser.add_argument("--seven-zip", type=Path)
    args = parser.parse_args()

    archive = args.zip.resolve()
    if not archive.exists():
        raise SystemExit(f"Missing archive: {archive}")

    print(f"Archive: {archive}")
    print(f"Archive size: {archive.stat().st_size}")
    archive_sha = sha256(archive)
    print(f"Archive sha256: {archive_sha}")

    parts = split_file(archive, args.part_size_mb * 1024 * 1024)
    for part in parts:
        print(f"Part: {part.name} size={part.stat().st_size} sha256={sha256(part)}")

    sha_file = archive.with_name(archive.stem + ".sha256.txt")
    sha_file.write_text(
        f"sha256:{archive.name}={archive_sha}\n"
        + "".join(f"sha256:{part.name}={sha256(part)}\n" for part in parts),
        encoding="utf-8",
    )
    print(f"SHA file: {sha_file.name} size={sha_file.stat().st_size}")

    recombined = archive.with_name(archive.name + ".recombined-test")
    if recombined.exists():
        recombined.unlink()
    combine_parts(parts, recombined)
    recombined_sha = sha256(recombined)
    print(f"Recombined sha256: {recombined_sha}")
    if recombined_sha != archive_sha:
        raise SystemExit("Recombined ZIP SHA256 does not match original ZIP")

    if args.seven_zip:
        run_7z_test(args.seven_zip.resolve(), recombined)

    recombined.unlink()
    print("Release assets are valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
