#!/bin/bash
# One entrance shot, safely (Roman's session was killed twice by uncapped Blender): the real Blender binary (the `blender` snap
# wrapper escapes the systemd cap), a 26 GB cap (the stage 5 scene peaks ~22 GB), and only when enough RAM is free.
#   landscape/render.sh SHOT [draft]
cd "$(dirname "$0")/.." || exit 1
until [ "$(free -g | awk '/^Mem:/{print $7}')" -ge 34 ]; do echo "waiting for free RAM ($(free -g | awk '/^Mem:/{print $7}') GB available)"; sleep 30; done
systemd-run --user --scope -p MemoryMax=26G -p MemorySwapMax=0 nice -n 19 /usr/bin/time -v /snap/blender/current/blender \
    -b construction/out/stage_5.blend -t 12 --python landscape/entrance_study.py -- "$@" > "/tmp/ent_$1.log" 2>&1
f=$(grep -oE "stage_5_ent_$1_v[0-9]+\.jpg" "/tmp/ent_$1.log" | tail -1)
[ -n "$f" ] && python3 tools/material_out.py add plants "entrance_$1" "construction/renders/$f" "Entrance: $1" > /dev/null
echo "$1 ${f:-FAILED} peak=$(grep 'Maximum resident' "/tmp/ent_$1.log" | awk '{printf "%.1f GB", $NF/1e6}') $(grep -c 'ut of memory\|out of GPU' "/tmp/ent_$1.log") gpu-oom"
