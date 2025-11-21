import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path
import random

# ------------------------------------------------------------
# CONFIG
# ------------------------------------------------------------
st.set_page_config(
    page_title="MAEGIA Console",
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
# DATA
# ------------------------------------------------------------
SITES = {
    "game":      {"label": "GAME // Arcade",        "url": "https://game.maegia.tv/?embed=true"},
    "kragzouy":  {"label": "KRAGZOUY // Zone X",    "url": "https://kragzouy.maegia.tv/?embed=true"},
    "oracle":    {"label": "ORACLE // Divination",  "url": "https://oracle.maegia.tv/?embed=true"},
    "pali":      {"label": "PALI // Linguistique",  "url": "https://pali.maegia.tv/?embed=true"},
    "cybermind": {"label": "CYBERMIND // Central",  "url": "https://cybermind.fr"}
}

DEFAULT_MODE = {
    "game": "hardcore",
    "kragzouy": "holo",
    "oracle": "holo",
    "pali": "hardcore",
    "cybermind": "holo"
}

MODES = ["holo", "hardcore", "hacker", "elite"]

# ------------------------------------------------------------
# SESSION STATE
# ------------------------------------------------------------
st.session_state.setdefault("console", [
    "System initialized.",
    "Default node : cybermind",
    "Type 'help' for commands."
])
st.session_state.setdefault("node", "cybermind")
st.session_state.setdefault("url", SITES["cybermind"]["url"])
st.session_state.setdefault("mode", DEFAULT_MODE["cybermind"])
st.session_state.setdefault("theme", "cyan")
st.session_state.setdefault("flux", False)
st.session_state.setdefault("ascii", False)
st.session_state.setdefault("theme_before_hacker", "cyan")

# ------------------------------------------------------------
# HELP / COMMANDS
# ------------------------------------------------------------
def help_text():
    return """
COMMANDS:
  help                Show help
  list                List nodes
  clear               Clear console

  connect <node>
  connect <node> --mode holo/hardcore/hacker/elite

OTHER:
  theme cyan/purple
  flux on/off
  ascii on/off
"""

def list_nodes():
    return "\n".join([f"- {k}: {v['label']}" for k,v in SITES.items()])


def parse(cmd):
    c = cmd.strip().lower()

    if c in ["help", "?"]:
        return ("print", help_text())
    if c in ["list", "ls"]:
        return ("print", list_nodes())
    if c in ["clear", "cls"]:
        return ("clear", None)

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

        mode = DEFAULT_MODE[node]
        if "--mode" in parts:
            m = parts[parts.index("--mode")+1]
            if m in MODES:
                mode = m

        return ("load", (node, mode))

    return ("print", f"Unknown command '{cmd}'")

# ------------------------------------------------------------
# ASCII RAIN
# ------------------------------------------------------------
def ascii_line():
    chars = "01░▒▓█"
    st.session_state.console.append(
        "".join(random.choice(chars) for _ in range(60))
    )

# ------------------------------------------------------------
# SANDBOX (iframe simple)
# ------------------------------------------------------------
def sandbox(url, mode):

    klass = {
        "holo": "mode-holo",
        "hardcore": "mode-hardcore",
        "hacker": "mode-hacker",
        "elite": "mode-elite"
    }[mode]

    overlay = "<div class='flux-overlay'></div>" if st.session_state.flux else ""

    html = f"""
    <div class="sandbox-frame {klass}">
        {overlay}
        <iframe src="{url}" class="sandbox-iframe"></iframe>
    </div>
    """

    components.html(html, height=0)

# ------------------------------------------------------------
# THEME SWITCH
# ------------------------------------------------------------
st.markdown(f"""
<script>
document.body.classList.remove('cyan','purple','hacker');
document.body.classList.add('{st.session_state.theme}');
</script>
""", unsafe_allow_html=True)

# ------------------------------------------------------------
# LAYOUT (console left, cards right)
# ------------------------------------------------------------
col_left, col_right = st.columns([2,1])

# ------------------------------------------------------------
# LEFT : CONSOLE
# ------------------------------------------------------------
with col_left:

    tab = st.radio("Navigation", ["Console","Info","Oracle AI"], horizontal=True)

    if tab == "Console":

        if st.session_state.ascii:
            ascii_line()

        st.text_area("Console", "\n".join(st.session_state.console), height=230)

        with st.form("cmdform", clear_on_submit=True):
            cmd = st.text_input(">_")
            run = st.form_submit_button("EXECUTE")

        if run and cmd:
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

                # theme switch if hacker
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
# RIGHT : CARDS (sans fullscreen)
# ------------------------------------------------------------
with col_right:
    st.markdown("<div class='right-scroll'>", unsafe_allow_html=True)

    for key, meta in SITES.items():

        active = " node-active" if key == st.session_state.node else ""

        st.markdown(
            f"""
            <div class="node-card{active}">
                <div class="node-title">{meta['label']}</div>
                <div class="node-url">{meta['url']}</div>
            </div>
            """, unsafe_allow_html=True
        )

        if st.button(f"CONNECT {key}"):
            st.session_state.node = key
            st.session_state.url = meta["url"]
            st.session_state.mode = DEFAULT_MODE[key]
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
