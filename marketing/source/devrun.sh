#!/usr/bin/env bash
# Starts the Forge dev server and client used for the listing screenshots, under Xvfb with software rendering.
#   marketing/source/devrun.sh prepare        # writes run/server.properties, eula, ops and client options
#   marketing/source/devrun.sh display        # Xvfb on :1 at 1920x1080
#   marketing/source/devrun.sh server         # ./gradlew runServer (RCON on 25575, password "bunny")
#   marketing/source/devrun.sh client         # ./gradlew runClient, joins the server as "Sugarplum"
#   marketing/source/devrun.sh stop
# Logs go to $SHOT_LOGS (default /tmp/bunnyland-shots). Needs a Java 17 JDK (set JAVA_HOME), xdotool and ImageMagick.
set -u
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
RUN="$ROOT/run"
LOGS=${SHOT_LOGS:-/tmp/bunnyland-shots}
mkdir -p "$LOGS"
export DISPLAY=${DISPLAY:-:1}
case "$1" in
  prepare)
    mkdir -p "$RUN/defaultconfigs" "$RUN/config"
    cat > "$RUN/server.properties" <<'PROPS'
allow-flight=true
broadcast-rcon-to-ops=false
difficulty=peaceful
enable-rcon=true
gamemode=creative
generate-structures=true
level-name=showcase
level-seed=sugarplum-meadows
max-tick-time=-1
motd=Bunnyland showcase
online-mode=false
op-permission-level=4
rcon.password=bunny
rcon.port=25575
simulation-distance=8
spawn-monsters=false
spawn-protection=0
view-distance=12
PROPS
    echo "eula=true" > "$RUN/eula.txt"
    # The offline-mode UUID of "Sugarplum".
    echo '[{"uuid": "9a35cb9c-03d4-3dad-aeec-ede3017469e4", "name": "Sugarplum", "level": 4, "bypassesPlayerLimit": false}]' > "$RUN/ops.json"
    # Forge 47 dev servers crash advertising themselves to LAN (the pinger class is client-only in dev).
    printf '[server]\n\tadvertiseDedicatedServerToLan = false\n' > "$RUN/defaultconfigs/forge-server.toml"
    # Skip the first-run screens, GUI scale 3, fancy graphics, no pausing when the window loses focus.
    [ -f "$RUN/options.txt" ] || printf '%s\n' onboardAccessibility:false skipMultiplayerWarning:true joinedFirstServer:true \
      tutorialStep:none pauseOnLostFocus:false guiScale:3 graphicsMode:1 renderDistance:12 simulationDistance:8 fov:0.0 \
      renderClouds:\"true\" particles:0 entityShadows:true biomeBlendRadius:5 narrator:0 soundCategory_master:0.0 \
      chatVisibility:0 > "$RUN/options.txt"
    ;;
  display)
    pgrep -x Xvfb > /dev/null || nohup Xvfb "$DISPLAY" -screen 0 1920x1080x24 +extension GLX +render -noreset > "$LOGS/xvfb.log" 2>&1 &
    ;;
  server)
    cd "$ROOT" && nohup sh ./gradlew runServer --no-daemon > "$LOGS/server.log" 2>&1 &
    ;;
  client)
    export LIBGL_ALWAYS_SOFTWARE=1 GALLIUM_DRIVER=llvmpipe
    cd "$ROOT" && nohup sh ./gradlew runClient --no-daemon \
      --args="--username Sugarplum --width 1920 --height 1080 --quickPlayMultiplayer localhost:25565" > "$LOGS/client.log" 2>&1 &
    ;;
  stop)
    for pid in $(pgrep -x java); do
      cmd=$(tr '\0' ' ' < "/proc/$pid/cmdline")
      if echo "$cmd" | grep -qE 'forgeclientuserdev|forgeserveruserdev|GradleDaemon|GradleWrapperMain'; then kill "$pid"; fi
    done
    ;;
esac
