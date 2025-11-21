import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path
import random

# ------------------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------------------
st.set_page_config(
    page_title="MAEGIA Cyber Console",
    page_icon="⬢",
    layout="wide"
)

# ------------------------------------------------------------
# LOAD CSS
# ------------------------------------------------------------
def load_css():
    css = Path("style.css").read_text()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

load_css()

# ------------------------------------------------------------
# INTRO (non bloquante)
# ------------------------------------------------------------
if "intro_done" not in st.session_state:
    st.session_state.intro_done = True

# Intro soft (fade CSS only)
st.markdown("""
<div id="introScreen">
    <div style='font-family:Orbitron;font-size:42px;color:#C86BFA;'>MAEGIA SYSTEM</div>
    <div style='margin-top:10px;color:#FFF;opacity:0.75;font-size:18px;'>BOOTING...</div>
</div>
""", unsafe_allow_html=True)


# ------------------------------------------------------------
# DATA
# ------------------------------------------------------------
SITES = {
    "game": {"label": "GAME // Arcade", "url": "https://game.maegia.tv/?embed=true"},
    "kragzouy": {"label": "KRAGZOUY // Zone X", "url": "https://kragzouy.maegia.tv/?embed=true"},
    "oracle": {"label": "ORACLE // Divination", "url": "https://oracle.maegia.tv/?embed=true"},
    "pali": {"label": "PALI // Linguistique", "url": "https://pali.maegia.tv/?embed=true"},
    "cybermind": {"label": "CYBERMIND // Central", "url": "https://cybermind.fr"}
}

DEFAULT_MODES = {
    "game": "hardcore",
    "kragzouy": "holo",
    "oracle": "holo",
    "pali": "hardcore",
    "cybermind": "holo"      # plus de fullscreen
}

MODES = ["holo", "hardcore", "hacker", "elite"]


MODE_SOUNDS = {
    "holo": "https://assets.mixkit.co/sfx/preview/mixkit-game-ball-tap-2073.mp3",
    "hardcore": "https://assets.mixkit.co/sfx/preview/mixkit-fast-small-sweep-transition-166.mp3",
    "hacker": "https://assets.mixkit.co/sfx/preview/mixkit-old-computer-boot-up-2328.mp3",
    "elite": "https://assets.mixkit.co/sfx/preview/mixkit-data-select-1101.mp3",
}

WARP_SOUND = "https://assets.mixkit.co/sfx/preview/mixkit-quick-win-video-game-notification-269.mp3"


# ------------------------------------------------------------
# SESSION DEFAULTS
# ------------------------------------------------------------
DEFAULTS = {
    "console": [
        "System initialized.",
        "Default node : cybermind",
        "Type 'help' for commands."
    ],
    "node": "cybermind",
    "mode": DEFAULT_MODES["cybermind"],
    "url": SITES["cybermind"]["url"],
    "theme": "cyan",
    "flux": False,
    "ascii": False,
    "theme_before_hacker": "cyan"
}

for k, v in DEFAULTS.items():
    st.session_state.setdefault(k, v)


# ------------------------------------------------------------
# HELP / COMMANDS
# ------------------------------------------------------------
def help_text():
    return """
COMMANDS:
  help                Show help
  list                List nodes
  clear               Clear console
  connect <node>      Load a node
  connect <node> --mode X

MODES:
  holo | hardcore | hacker | elite

OTHER:
  theme cyan/purple
  flux on/off
  ascii on/off
"""

def list_nodes():
    return "\n".join([f"- {k} : {v['label']}" for k, v in SITES.items()])


def parse(cmd):
    c = cmd.lower().strip()

    if c in ["help", "?"]: return ("print", help_text())
    if c in ["list", "ls"]: return ("print", list_nodes())
    if c in ["clear", "cls"]: return ("clear", None)

    if c == "flux on": return ("flux", True)
    if c == "flux off": return ("flux", False)

    if c == "ascii on": return ("ascii", True)
    if c == "ascii off": return ("ascii", False)

    if c.startswith("theme "):
        return ("theme", c.split()[1])

    if c.startswith("connect "):
        parts = c.split()
        node = parts[1]

        if node not in SITES:
            return ("print", f"Unknown node '{node}'")

        mode = DEFAULT_MODES[node]

        if "--mode" in parts:
            m = parts[parts.index("--mode") + 1]
            if m in MODES:
                mode = m

        return ("load", (node, mode))

    if c in SITES:
        return ("load", (c, DEFAULT_MODES[c]))

    return ("print", f"Unknown command '{cmd}'")


# ------------------------------------------------------------
# ASCII RAIN
# ------------------------------------------------------------
def ascii_line():
    chars = "01░▒▓█"
    st.session_state.console.append(
        "".join(random.choice(chars) for _ in range(70))
    )


# ------------------------------------------------------------
# IFRAME
# ------------------------------------------------------------
def sandbox(url, mode):
    klass = {
        "holo": "cyber-holo cyber-holo-active",
        "hardcore": "cyber-hardcore",
        "hacker": "hacker-mode",
        "elite": "hacker-elite-mode"
    }[mode]

    overlay = "<div class='data-matrix'></div>" if st.session_state.flux else ""

    html = f"""
    <audio id='modeSound' src='{MODE_SOUNDS[mode]}'></audio>
    <audio id='warpSound' src='{WARP_SOUND}'></audio>

    <div class='cybersandbox-frame warp-transition {klass}'>
        {overlay}
        <iframe id='sandboxIframe' src='{url}'></iframe>
    </div>

    <script>
    function resizeIframe(){{
        let f = document.getElementById("sandboxIframe");
        let c = f.parentElement;
        let h = window.innerHeight - c.getBoundingClientRect().top - 10;
        f.style.height = h + "px";
        c.style.height = h + "px";
    }}
    window.onload = resizeIframe;
    window.onresize = resizeIframe;

    document.getElementById("modeSound").play();
    document.getElementById("warpSound").play();
    </script>
    """

    components.html(html, height=0)


# ------------------------------------------------------------
# MAIN UI
# ------------------------------------------------------------
st.markdown("<div class='scanlines'></div>", unsafe_allow_html=True)

# THEME SWITCH
st.markdown(f"""
<script>
document.body.classList.remove('cyan','purple','hacker');
document.body.classList.add('{st.session_state.theme}');
</script>
""", unsafe_allow_html=True)


col_left, col_right = st.columns([2, 1])


# ------------------------------------------------------------
# LEFT PANEL — CONSOLE
# ------------------------------------------------------------
with col_left:

    tab = st.radio("Navigation", ["Console", "Info", "Oracle AI"], horizontal=True)

    if tab == "Console":

        if st.session_state.ascii:
            ascii_line()

        st.text_area("Console", "\n".join(st.session_state.console), height=230)

        with st.form("cmd", clear_on_submit=True):
            cmd = st.text_input(">_")
            go = st.form_submit_button("EXECUTE")

        if go and cmd:
            st.session_state.console.append("> " + cmd)
            act, pay = parse(cmd)

            if act == "print":
                st.session_state.console.append(pay)

            elif act == "clear":
                st.session_state.console = ["Console cleared."]

            elif act == "flux":
                st.session_state.flux = pay

            elif act == "ascii":
                st.session_state.ascii = pay

            elif act == "theme":
                if st.session_state.theme != "hacker":
                    st.session_state.theme_before_hacker = st.session_state.theme
                st.session_state.theme = pay

            elif act == "load":
                node, mode = pay

                if mode in ["hacker", "elite"]:
                    st.session_state.theme_before_hacker = st.session_state.theme
                    st.session_state.theme = "hacker"
                else:
                    if st.session_state.theme == "hacker":
                        st.session_state.theme = st.session_state.theme_before_hacker

                st.session_state.node = node
                st.session_state.url = SITES[node]["url"]
                st.session_state.mode = mode
                st.session_state.console.append(f"Loading {node} [{mode}]")

            st.rerun()

        sandbox(st.session_state.url, st.session_state.mode)

    elif tab == "Info":
        st.write(st.session_state)

    else:
        q = st.text_input("Question:")
        if st.button("Ask"):
            st.write("Response:", q[::-1])


# ------------------------------------------------------------
# RIGHT PANEL — CARDS
# ------------------------------------------------------------
with col_right:
    st.markdown("<div class='right-panel-scroll'>", unsafe_allow_html=True)

    for key, meta in SITES.items():

        active = " node-active" if key == st.session_state.node else ""

        st.markdown(
            f"""
            <div class='node-card{active}'>
                <div class='node-title'>{meta['label']}</div>
                <div class='node-url'>{meta['url']}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        if st.button(f"CONNECT {key}"):
            st.session_state.node = key
            st.session_state.url = meta["url"]
            st.session_state.mode = DEFAULT_MODES[key]
            st.rerun()

        c1, c2, c3, c4 = st.columns(4)

        if c1.button("HOLO", key=f"holo_{key}"):
            st.session_state.node = key
            st.session_state.url = meta["url"]
            st.session_state.mode = "holo"
            st.rerun()

        if c2.button("HARD", key=f"hard_{key}"):
            st.session_state.node = key
            st.session_state.url = meta["url"]
            st.session_state.mode = "hardcore"
            st.rerun()

        if c3.button("HACK", key=f"hacker_{key}"):
            st.session_state.node = key
            st.session_state.url = meta["url"]
            st.session_state.mode = "hacker"
            st.session_state.theme_before_hacker = st.session_state.theme
            st.session_state.theme = "hacker"
            st.rerun()

        if c4.button("ELITE", key=f"elite_{key}"):
            st.session_state.node = key
            st.session_state.url = meta["url"]
            st.session_state.mode = "elite"
            st.session_state.theme_before_hacker = st.session_state.theme
            st.session_state.theme = "hacker"
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
