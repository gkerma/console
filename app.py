import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path
from textwrap import dedent
import random

# -------------------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------------------
st.set_page_config(
    page_title="MAEGIA Cyber Console",
    page_icon="⬢",
    layout="wide"
)

# -------------------------------------------------------------
# LOAD CSS
# -------------------------------------------------------------
def load_css():
    css_path = Path("style.css")
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)

load_css()

# -------------------------------------------------------------
# INITIAL INTRO (CSS HANDLES EVERYTHING)
# -------------------------------------------------------------
if "intro_done" not in st.session_state:
    st.session_state.intro_done = True
    st.markdown("<div id='introScreen'></div>", unsafe_allow_html=True)
    st.stop()

# -------------------------------------------------------------
# SITES
# -------------------------------------------------------------
SITES = {
    "game": {
        "label": "GAME // Arcade dimensionnelle",
        "url": "https://game.maegia.tv/?embed=true&embed_options=dark_theme",
    },
    "kragzouy": {
        "label": "KRAGZOUY // Zone expérimentale",
        "url": "https://kragzouy.maegia.tv/?embed=true&embed_options=dark_theme",
    },
    "oracle": {
        "label": "ORACLE // Divination système",
        "url": "https://oracle.maegia.tv/?embed=true&embed_options=dark_theme",
    },
    "pali": {
        "label": "PALI // Protocoles linguistiques",
        "url": "https://pali.maegia.tv/?embed=true&embed_options=dark_theme",
    },
    "cybermind": {
        "label": "CYBERMIND // Nœud central",
        "url": "https://cybermind.fr",
    },
}

DEFAULT_MODES = {
    "game": "hardcore",
    "kragzouy": "holo",
    "oracle": "holo",
    "pali": "hardcore",
    "cybermind": "fullscreen",
}

MODES = ["holo", "hardcore", "fullscreen", "hacker", "elite"]

# -------------------------------------------------------------
# SOUNDS (mapping, CSS/JS plays them)
# -------------------------------------------------------------
MODE_SOUNDS = {
    "holo": "https://assets.mixkit.co/sfx/preview/mixkit-game-ball-tap-2073.mp3",
    "hardcore": "https://assets.mixkit.co/sfx/preview/mixkit-fast-small-sweep-transition-166.mp3",
    "fullscreen": "https://assets.mixkit.co/sfx/preview/mixkit-arcade-mechanical-bling-2104.mp3",
    "hacker": "https://assets.mixkit.co/sfx/preview/mixkit-old-computer-boot-up-2328.mp3",
    "elite": "https://assets.mixkit.co/sfx/preview/mixkit-data-select-1101.mp3",
}

WARP_SOUND = "https://assets.mixkit.co/sfx/preview/mixkit-quick-win-video-game-notification-269.mp3"

# PACK SFX CYBERPUNK
CYBERPACK = [
    "https://assets.mixkit.co/sfx/preview/mixkit-select-click-1109.mp3",
    "https://assets.mixkit.co/sfx/preview/mixkit-retro-game-notification-212.mp3",
    "https://assets.mixkit.co/sfx/preview/mixkit-arcade-retro-coin-2042.mp3",
]

# -------------------------------------------------------------
# SESSION STATE
# -------------------------------------------------------------
if "console" not in st.session_state:
    st.session_state.console = [
        "System initialized.",
        "Default node : cybermind",
        "Type 'help' for commands."
    ]

if "node" not in st.session_state:
    st.session_state.node = "cybermind"

if "mode" not in st.session_state:
    st.session_state.mode = DEFAULT_MODES["cybermind"]

if "url" not in st.session_state:
    st.session_state.url = SITES["cybermind"]["url"]

if "fullwindow" not in st.session_state:
    st.session_state.fullwindow = False

if "theme" not in st.session_state:
    st.session_state.theme = "cyan"

if "flux" not in st.session_state:
    st.session_state.flux = False

if "ascii" not in st.session_state:
    st.session_state.ascii = False

if "theme_before_hacker" not in st.session_state:
    st.session_state.theme_before_hacker = "cyan"

# -------------------------------------------------------------
# ASCII RAIN FUNCTION
# -------------------------------------------------------------
def append_ascii_line():
    chars = "01░▒▓█"
    line = "".join(random.choice(chars) for _ in range(80))
    st.session_state.console.append("> " + line)

# -------------------------------------------------------------
# HELP + LIST
# -------------------------------------------------------------
def help_text():
    return dedent("""
    COMMANDS :

      help                       → show help
      list                       → list nodes
      clear                      → clear console

    CONNECTION :

      connect <node>             → open node
      connect <node> --mode X    → choose mode
      open <node>                → fullwindow mode
      exit                       → close fullwindow

    MODES :

      holo | hardcore | fullscreen | hacker | elite

    OTHER :

      flux on/off                → flux data matrix overlay
      ascii on/off               → ASCII rain mode
      theme cyan/purple          → UI theme
    """)

def list_nodes():
    msg = ["NODES :"]
    for key, meta in SITES.items():
        msg.append(f" - {key:12} → {meta['label']}")
    return "\n".join(msg)

# -------------------------------------------------------------
# COMMAND PARSER
# -------------------------------------------------------------
def parse_command(cmd):
    cmd = cmd.strip()
    low = cmd.lower()

    if low in ["help", "?", "man"]:
        return {"action": "print", "payload": help_text()}

    if low in ["list", "ls"]:
        return {"action": "print", "payload": list_nodes()}

    if low in ["clear", "cls"]:
        return {"action": "clear"}

    if low.startswith("open "):
        node = low.split()[1]
        if node in SITES:
            return {"action": "fullwindow", "node": node}
        return {"action": "print", "payload": f"Unknown node '{node}'"}

    if low in ["exit", "quit"]:
        return {"action": "exit"}

    if low == "flux on":
        return {"action": "flux", "payload": True}
    if low == "flux off":
        return {"action": "flux", "payload": False}

    if low == "ascii on":
        return {"action": "ascii", "payload": True}
    if low == "ascii off":
        return {"action": "ascii", "payload": False}

    if low.startswith("theme "):
        t = low.split()[1]
        if t in ["cyan", "purple"]:
            return {"action": "theme", "payload": t}
        return {"action": "print", "payload": "Unknown theme."}

    if low.startswith("connect "):
        parts = low.split()
        node = parts[1]
        if node not in SITES:
            return {"action": "print", "payload": f"Unknown node '{node}'"}

        mode = DEFAULT_MODES[node]

        if "--mode" in parts:
            idx = parts.index("--mode")
            if idx + 1 < len(parts):
                m = parts[idx + 1]
                if m in MODES:
                    mode = m

        return {"action": "load", "node": node, "mode": mode}

    if low in SITES:
        return {"action": "load", "node": low, "mode": DEFAULT_MODES[low]}

    return {"action": "print", "payload": f"Unknown command '{cmd}'"}

# -------------------------------------------------------------
# SANDBOX IFRAME (dynamic, CSS-driven)
# -------------------------------------------------------------
def sandbox_iframe(url, mode):
    overlay = ""
    if st.session_state.flux:
        overlay = "<div class='data-matrix'></div>"

    klass = {
        "holo": "cyber-holo cyber-holo-active",
        "hardcore": "cyber-hardcore",
        "fullscreen": "",
        "hacker": "hacker-mode",
        "elite": "hacker-elite-mode",
    }.get(mode, "cyber-holo")

    mode_sound = MODE_SOUNDS.get(mode, MODE_SOUNDS["holo"])
    random_fx = random.choice(CYBERPACK)

    html = f"""
    <audio id="modeSound" src="{mode_sound}"></audio>
    <audio id="warpSound" src="{WARP_SOUND}"></audio>
    <audio id="fxPack" src="{random_fx}"></audio>

    <div id="sandboxContainer" class="cybersandbox-frame warp-transition {klass}">
        {overlay}
        <button class="cyber-fullscreen-btn" onclick="toggleFullscreen()">FULLSCREEN</button>
        <iframe id="sandboxIframe" src="{url}"></iframe>
    </div>

    <script>
    function resizeIframe(){{
        const f=document.getElementById("sandboxIframe");
        const c=document.getElementById("sandboxContainer");
        let vh=window.innerHeight; 
        let t=c.getBoundingClientRect().top;
        let h=vh-t-10;
        f.style.height=h+"px";
        c.style.height=h+"px";
    }}
    window.addEventListener("load",resizeIframe);
    window.addEventListener("resize",resizeIframe);

    document.getElementById("modeSound").play();
    document.getElementById("warpSound").play();
    document.getElementById("fxPack").play();

    function toggleFullscreen(){{
        let el=document.getElementById("sandboxContainer");
        if(!document.fullscreenElement) el.requestFullscreen();
        else document.exitFullscreen();
    }}
    </script>
    """
    components.html(html, height=0, scrolling=False)

# -------------------------------------------------------------
# ORACLE AI
# -------------------------------------------------------------
def oracle_ai():
    st.write("## ORACLE AI — Assistant Neural")
    q = st.text_input("Question :")
    if st.button("Interroger"):
        st.write("Réponse :", q[::-1])  # placeholder

# -------------------------------------------------------------
# FULLWINDOW MODE
# -------------------------------------------------------------
if st.session_state.fullwindow:
    st.markdown("""
        <style>
        .block-container {padding:0!important;}
        </style>
        <div class='fw-exit'>
            <button onclick="window.location.reload()">EXIT</button>
        </div>
    """, unsafe_allow_html=True)
    sandbox_iframe(st.session_state.url, "fullscreen")
    st.stop()

# -------------------------------------------------------------
# MAIN UI
# -------------------------------------------------------------
st.markdown("<div class='scanlines'></div>", unsafe_allow_html=True)

# APPLY THEME (CSS handles it)
st.markdown(
    f"<script>document.body.classList.add('{st.session_state.theme}');</script>",
    unsafe_allow_html=True
)

col_left, col_right = st.columns([2, 1])

# -------------------------------------------------------------
# LEFT COLUMN
# -------------------------------------------------------------
with col_left:

    tab = st.radio("Navigation", ["Console", "Info", "Oracle AI"], horizontal=True)

    # ----------- CONSOLE -----------
    if tab == "Console":
        if st.session_state.ascii:
            append_ascii_line()

        console_text = "\n".join(st.session_state.console)
        st.text_area("", console_text, height=200)

        with st.form("cmd", clear_on_submit=True):
            cmd = st.text_input(">_ Command")
            go = st.form_submit_button("EXECUTE")

        if go and cmd:
            st.session_state.console.append("> " + cmd)
            result = parse_command(cmd)

            if result["action"] == "print":
                st.session_state.console.append(result["payload"])

            elif result["action"] == "clear":
                st.session_state.console = ["Console cleared."]

            elif result["action"] == "flux":
                st.session_state.flux = result["payload"]

            elif result["action"] == "ascii":
                st.session_state.ascii = result["payload"]

            elif result["action"] == "theme":
                # save previous theme before hacker
                if st.session_state.theme not in ["hacker"]:
                    st.session_state.theme_before_hacker = st.session_state.theme
                st.session_state.theme = result["payload"]

            elif result["action"] == "exit":
                st.session_state.fullwindow = False

            elif result["action"] == "fullwindow":
                node = result["node"]
                st.session_state.node = node
                st.session_state.url = SITES[node]["url"]
                st.session_state.fullwindow = True

            elif result["action"] == "load":
                node = result["node"]
                mode = result["mode"]

                # HANDLE GLOBAL HACKER/ELITE THEME
                if mode in ["hacker", "elite"]:
                    st.session_state.theme_before_hacker = st.session_state.theme
                    st.session_state.theme = "hacker"
                else:
                    if st.session_state.theme == "hacker":
                        st.session_state.theme = st.session_state.theme_before_hacker

                st.session_state.node = node
                st.session_state.url = SITES[node]["url"]
                st.session_state.mode = mode
                st.session_state.console.append(f"Loading {node} in mode {mode}…")

            st.rerun()

        sandbox_iframe(st.session_state.url, st.session_state.mode)

    # ----------- INFO -----------
    elif tab == "Info":
        st.write("Node :", st.session_state.node)
        st.write("Mode :", st.session_state.mode)
        st.write("URL :", st.session_state.url)
        st.write("Theme :", st.session_state.theme)
        st.write("Flux :", st.session_state.flux)
        st.write("ASCII :", st.session_state.ascii)

    # ----------- ORACLE AI -----------
    elif tab == "Oracle AI":
        oracle_ai()

# -------------------------------------------------------------
# RIGHT COLUMN (Node Cards)
# -------------------------------------------------------------
with col_right:
    st.markdown("<div class='right-panel-scroll'>", unsafe_allow_html=True)

    for key, meta in SITES.items():
        active = " node-active" if key == st.session_state.node else ""

        # NODE CARD
        st.markdown(
            f"""
            <div class="node-card {active}">
                <div class="node-title">{meta['label']}</div>
                <div class="node-url">{meta['url']}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # BUTTON : CONNECT
        if st.button(f"CONNECT {key}", key=f"{key}_connect"):
            cmd = f"connect {key} --mode {DEFAULT_MODES[key]}"
            st.session_state.console.append("> " + cmd)
            st.session_state.node = key
            st.session_state.url = meta["url"]
            st.session_state.mode = DEFAULT_MODES[key]
            st.rerun()

        # BUTTON : FULLWINDOW
        if st.button(f"FW {key}", key=f"{key}_fw"):
            st.session_state.console.append(f"> open {key}")
            st.session_state.node = key
            st.session_state.url = meta["url"]
            st.session_state.fullwindow = True
            st.rerun()

        # BUTTONS FOR MODES
        c1, c2, c3, c4, c5 = st.columns(5)

        if c1.button("HOLO", key=f"holo_{key}"):
            st.session_state.mode = "holo"
            st.session_state.node = key
            st.session_state.url = meta["url"]
            st.session_state.console.append(f"> connect {key} --mode holo")
            # restore theme if needed
            if st.session_state.theme == "hacker":
                st.session_state.theme = st.session_state.theme_before_hacker
            st.rerun()

        if c2.button("HARD", key=f"hard_{key}"):
            st.session_state.mode = "hardcore"
            st.session_state.node = key
            st.session_state.url = meta["url"]
            st.session_state.console.append(f"> connect {key} --mode hardcore")
            if st.session_state.theme == "hacker":
                st.session_state.theme = st.session_state.theme_before_hacker
            st.rerun()

        if c3.button("FULL", key=f"full_{key}"):
            st.session_state.mode = "fullscreen"
            st.session_state.node = key
            st.session_state.url = meta["url"]
            st.session_state.console.append(f"> connect {key} --mode fullscreen")
            if st.session_state.theme == "hacker":
                st.session_state.theme = st.session_state.theme_before_hacker
            st.rerun()

        if c4.button("HACK", key=f"hacker_{key}"):
            st.session_state.mode = "hacker"
            st.session_state.node = key
            st.session_state.url = meta["url"]
            st.session_state.console.append(f"> connect {key} --mode hacker")
            st.session_state.theme_before_hacker = st.session_state.theme
            st.session_state.theme = "hacker"
            st.rerun()

        if c5.button("ELITE", key=f"elite_{key}"):
            st.session_state.mode = "elite"
            st.session_state.node = key
            st.session_state.url = meta["url"]
            st.session_state.console.append(f"> connect {key} --mode elite")
            st.session_state.theme_before_hacker = st.session_state.theme
            st.session_state.theme = "hacker"
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
