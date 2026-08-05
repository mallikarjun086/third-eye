"""Reproducibly build the paired gallery/ + queries/ evaluation set.

The Kaggle CUFS/CUFSF copy ('arbazkhan971/cuhk-face-sketch-database-cufs')
ships raw photo and sketch folders whose filename indexes do NOT line up.
This script pairs photos and sketches by their person ID so every teammate
builds the exact same test set (deterministic output -> identical metrics).

Usage:
    python prepare_dataset.py [dataset_dir]

dataset_dir defaults to 'dataset'. Requires the raw folders present:
    <dir>/photos, <dir>/sketches
Produces:
    <dir>/gallery/   - suspect photos, one per person  (110xx.jpg...)
    <dir>/queries/   - matching sketches, one per person
"""
import os
import shutil
import sys


def person_id(filename, side):
    base = os.path.splitext(filename)[0]
    if side == "photo":
        return base[:-3] if base.endswith("-01") else base
    return base[:-7] if base.endswith("-01-sz1") else base


def main():
    base = sys.argv[1] if len(sys.argv) > 1 else "dataset"
    photo_dir = os.path.join(base, "photos")
    sketch_dir = os.path.join(base, "sketches")
    gallery_dir = os.path.join(base, "gallery")
    queries_dir = os.path.join(base, "queries")

    for d in (photo_dir, sketch_dir):
        if not os.path.isdir(d):
            sys.exit(f"missing folder {d!r} - download the dataset first (see README)")

    photos = {}
    for f in sorted(os.listdir(photo_dir)):
        if f.lower().endswith(".jpg"):
            photos[person_id(f, "photo")] = f

    sketches = {}
    for f in sorted(os.listdir(sketch_dir)):
        if f.lower().endswith(".jpg"):
            sketches[person_id(f, "sketch")] = f

    pairs = sorted(set(photos) & set(sketches))
    if not pairs:
        sys.exit("no overlapping person IDs found between photos and sketches")

    os.makedirs(gallery_dir, exist_ok=True)
    os.makedirs(queries_dir, exist_ok=True)
    for pid in pairs:
        shutil.copy(os.path.join(photo_dir, photos[pid]), os.path.join(gallery_dir, pid + ".jpg"))
        shutil.copy(os.path.join(sketch_dir, sketches[pid]), os.path.join(queries_dir, pid + ".jpg"))

    print(f"Built {len(pairs)} photo/sketch pairs")
    print(f"  gallery/ -> {gallery_dir}")
    print(f"  queries/ -> {queries_dir}")


if __name__ == "__main__":
    main()