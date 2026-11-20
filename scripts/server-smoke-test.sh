#!/usr/bin/env bash
# Starts a dev server for one Minecraft version and loader, spawns every Bunnyland creature next to world spawn
# (five Rainbow Butterflies first), lets them live for 30 seconds and stops. Fails if the server crashes.
#   usage: scripts/server-smoke-test.sh <minecraft version folder> <fabric|forge|neoforge>
set -u
VERSION="$1"; LOADER="$2"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/$VERSION"
RUN="$LOADER/run"
rm -rf "$RUN/world" "$RUN/crash-reports" "$RUN/logs"
mkdir -p "$RUN/world/datapacks/bunnyland_smoke"
PACK="$RUN/world/datapacks/bunnyland_smoke"
echo "eula=true" > "$RUN/eula.txt"
cat > "$RUN/server.properties" <<PROPS
online-mode=false
function-permission-level=4
spawn-protection=0
view-distance=4
simulation-distance=4
level-seed=20261120
initial-enabled-packs=vanilla,file/bunnyland_smoke
PROPS
sed 's/\${mod_id}/bunnyland_smoke/' common/src/main/resources/pack.mcmeta > "$PACK/pack.mcmeta"

CREATURES="cotton_bunny strawberry_bunny moon_bunny lavender_bunny snowball_bunny blossom_fox cloud_kitty strawberry_mouse honey_bear moon_deer pastel_axolotl tiny_swan cherry_blossom_bird dreamy_hamster"
for dir in function functions; do
  mkdir -p "$PACK/data/bunnyland_smoke/$dir" "$PACK/data/minecraft/tags/$dir"
  echo '{"values":["bunnyland_smoke:start"]}' > "$PACK/data/minecraft/tags/$dir/load.json"
  printf 'forceload add -32 -32 32 32\nschedule function bunnyland_smoke:spawn 100t\n' > "$PACK/data/bunnyland_smoke/$dir/start.mcfunction"
  {
    echo 'time set noon'
    for x in -4 -2 0 2 4; do echo "execute positioned $x 0 4 positioned over world_surface run summon bunnyland:rainbow_butterfly ~ ~1 ~"; done
    z=-12
    for c in $CREATURES; do echo "execute positioned 8 0 $z positioned over world_surface run summon bunnyland:$c"; z=$((z + 2)); done
    echo 'say BUNNYLAND_SMOKE_SPAWNED'
    echo 'schedule function bunnyland_smoke:finish 600t'
  } > "$PACK/data/bunnyland_smoke/$dir/spawn.mcfunction"
  printf 'execute if entity @e[type=bunnyland:rainbow_butterfly] run say BUNNYLAND_BUTTERFLIES_ALIVE\nsay BUNNYLAND_SMOKE_OK\nstop\n' > "$PACK/data/bunnyland_smoke/$dir/finish.mcfunction"
done

LOG="$ROOT/server-smoke-$VERSION-$LOADER.log"
./gradlew ":$LOADER:runServer" --stacktrace < /dev/null > "$LOG" 2>&1 &
PID=$!
result=timeout
for _ in $(seq 1 180); do
  sleep 5
  if grep -q "BUNNYLAND_SMOKE_OK" "$LOG"; then result=ok; break; fi
  if grep -q -E "This crash report has been saved|Encountered an unexpected exception|Failed to start the minecraft server" "$LOG"; then result=crash; break; fi
  if ! kill -0 $PID 2>/dev/null; then result=exited; break; fi
done
sleep 10
pkill -P $PID 2>/dev/null; kill $PID 2>/dev/null; wait $PID 2>/dev/null

grep -n -E "BUNNYLAND_SMOKE|bunnyland|Bunnyland" "$LOG" | grep -v -E "Download|Task :" | head -40
for f in "$RUN"/crash-reports/*.txt; do [ -f "$f" ] && { echo "=== $f"; head -80 "$f"; }; done
grep -n -E "ERROR|Exception|Caused by" "$LOG" | head -60
echo "Result: $result"
if [ "$result" != ok ] || grep -q "This crash report has been saved" "$LOG"; then exit 1; fi
if ! grep -q "BUNNYLAND_BUTTERFLIES_ALIVE" "$LOG"; then echo "No Rainbow Butterfly was alive at the end"; exit 1; fi
