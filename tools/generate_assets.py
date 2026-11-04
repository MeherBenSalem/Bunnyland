#!/usr/bin/env python3
"""Generates every Bunnyland asset except sounds: creature models, textures (+ glow masks) and
animations, item and block textures/models, the journal GUI, particles, recipes, loot tables,
tags, biome modifiers, advancements, the GameTest arena and the English lang file.

    python tools/generate_assets.py

Sounds are synthesised separately by tools/generate_sounds.py. Generated folders are wiped and
fully rewritten on every run (see CLEAN below).
"""
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from assetgen import anims, creatures, variants  # noqa: E402
from assetgen.core import ASSETS, DATA, ROOT, str_seed, write_json  # noqa: E402
from assetgen.paint import MISSING, paint_model  # noqa: E402
from assetgen.species import SPECIES  # noqa: E402

CLEAN = [
    ASSETS / "geo", ASSETS / "animations", ASSETS / "textures", ASSETS / "models", ASSETS / "blockstates",
    ASSETS / "particles", ASSETS / "lang", DATA, ROOT / "data" / "minecraft" / "tags",
]


def generate_creatures():
    report = []
    for sid, rig, params in SPECIES:
        names = variants.variant_list(sid)
        layout = None
        geo = None
        bones = None
        for vname, rare in names:
            pal = variants.palette(sid, vname)
            model = creatures.BUILDERS[sid](pal)
            model.pack()
            sig = [(tuple(c.size), tuple(sorted(c.uv.items()))) for c in model.cubes()]
            if layout is None:
                layout = sig
                geo = model.to_json()
                bones = {b.name for b in model.bones}
                tex_size = (model.tex_w, model.tex_h)
            elif sig != layout:
                raise SystemExit(f"{sid}/{vname}: geometry differs between variants")
            tex, glow = paint_model(model, pal, seed=str_seed(sid) % 1000)
            tex.save(ASSETS / "textures" / "entity" / sid / f"{vname}.png")
            if glow is not None:
                glow.save(ASSETS / "textures" / "entity" / sid / f"{vname}_glow.png")
            report.append(f"{sid:22s} {vname:18s} {'rare ' if rare else '     '}{'glow' if glow else ''}")
        write_json(ASSETS / "geo" / "entity" / f"{sid}.geo.json", geo, compact=True)
        write_json(ASSETS / "animations" / "entity" / f"{sid}.animation.json", anims.build(rig, params, bones, sid), compact=True)
        print(f"  {sid:22s} {len(names)} variants, texture {tex_size[0]}x{tex_size[1]}, {len(bones)} bones")
    if MISSING:
        print("WARNING: materials missing from palettes:")
        for m in sorted(MISSING):
            print("   ", m)
    return report


def main():
    for d in CLEAN:
        if d.exists():
            shutil.rmtree(d)
    print("Creatures:")
    generate_creatures()
    from assetgen import data, items
    print("Items and blocks:")
    items.generate()
    print("Data:")
    data.generate()
    print("Done.")


if __name__ == "__main__":
    main()
