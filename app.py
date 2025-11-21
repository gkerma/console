# MAEGIA Console - Fusion Sandbox (Mirror + Iframe)
# Layout 3 Colonnes – Cyberpunk Light Mode

import streamlit as st
import streamlit.components.v1 as components
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from pathlib import Path

st.set_page_config(page_title="MAEGIA Console", layout="wide", page_icon="⬢")

# ------------------------------------------------------------
# LOAD CSS
# ------------------------------------------------------------
if Path("style.css").exists():
    st.markdown(
        f"<style>{Path('style.css').read_text()}</style>",
        unsafe_allow_html=True
    )

# ------------------------------------------------------------
# NODE DEFINITIONS
# ------------------------------------------------------------
NODES = {
    "game": {
        "label": "GAME // Arcade",
        "url": "https://game.maegia.tv/?embed=true",
    },
    "kragzouy": {
        "label": "KRAGZOUY // Zone X",
        "url": "https://kragzouy.maegia.tv/?embed=true",
    },
    "oracle": {
        "label": "ORACLE // Divination",
        "url": "https://oracle.maegia.tv/?embed=true",
    },
    "pali": {
        "label": "PALI // Linguistique",
        "url": "https://pali.maegia.tv/?embed=true",
    },
    "cybermind": {
        "label": "CYBERMIND // Central",
        "url": "https://cybermind.fr",
    },
    "ganimed": {
        "label": "GANIMED // Nexus",
        "url": "https://ganimed.fr",
    },
}

DEFAULT_MODE = {
    "game": "holo",
    "kragzouy": "holo",
    "oracle": "holo",
    "pali": "hardcore",
    "cybermind": "holo",
    "ganimed": "holo",
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
st.session_state.setdefault("mode", DEFAULT_MODE["cybermind"])
st.session_state.setdefault("theme", "cyan")
st.session_state.setdefault("flux", False)
st.session_state.setdefault("ascii", False)

# ------------------------------------------------------------
# CONSOLE ENGINE
# ------------------------------------------------------------
def help_text():
    return (
        "COMMANDS:\n"
        "  help                Show help\n"
        "  list                List nodes\n"
        "  clear               Clear console\n\n"
        "  connect <node>\n"
        "  connect <node> --mode holo/hardcore/hacker/elite\n\n"
        "OTHER:\n"
        "  theme cyan/purple\n"
        "  flux on/off\n"
        "  ascii on/off\n"
    )

def list_nodes():
    return "\n".join([f"- {k}: {v['label']}" for k, v in NODES.items()])

def parse(cmd):
    c = cmd.strip().lower()

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
        if node not in NODES:
            return ("print", f"Unknown node '{node}'")

        mode = DEFAULT_MODE[node]
        if "--mode" in parts:
            idx = parts.index("--mode") + 1
            if idx < len(parts) and parts[idx] in MODES:
                mode = parts[idx]
        return ("load", (node, mode))

    return ("print", f"Unknown command '{cmd}'")

# ------------------------------------------------------------
# SANDBOX FUSION (IFRAME OR MIRROR)
# ------------------------------------------------------------
def is_streamlit_app(url: str) -> bool:
    host = urlparse(url).hostname or ""
    return host.endswith("streamlit.app") or "maegia.tv" in host

def sandbox(node: str, mode: str):
    url = NODES[node]["url"]

    # 1) MIRROR for Streamlit apps
    if "?embed=true" in url or is_streamlit_app(url):
        try:
            html = requests.get(url, timeout=6).text
            soup = BeautifulSoup(html, "html.parser")
            for s in soup.find_all("script"):
                s.decompose()
            snapshot = str(soup)
        except Exception as e:
            snapshot = f"<p style='color:red;'>Mirror error: {e}</p>"

        components.html(
            f"""
            <div class='sandbox-frame mode-{mode}'>{snapshot}</div>
            """,
            height=800,
            scrolling=True
        )
        return

    # 2) IFRAME for standard HTML websites
    components.html(
        f"""
        <div class='sandbox-frame mode-{mode}' id='sandboxContainer'>
            <iframe id='sandboxIframe' src='{url}'></iframe>
        </div>
        <script>
        function resizeIframe() {{
            const f = document.getElementById('sandboxIframe');
            const c = document.getElementById('sandboxContainer');
            if (!f || !c) return;
            const top = c.getBoundingClientRect().top;
            const h = window.innerHeight - top - 30;
            f.style.height = h + 'px';
            c.style.height = h + 'px';
        }}
        resizeIframe();
        setTimeout(resizeIframe, 150);
        window.addEventListener('resize', resizeIframe);
        </script>
        """,
        height=0
    )

# ------------------------------------------------------------
# APPLY THEME
# ------------------------------------------------------------
st.markdown(
    f"""
<script>
document.body.classList.remove('cyan','purple','hacker');
document.body.classList.add('{st.session_state.theme}');
</script>
""",
    unsafe_allow_html=True
)

# ------------------------------------------------------------
# LAYOUT 3 COLONNES
# ------------------------------------------------------------
col_console, col_sandbox, col_nodes = st.columns([1.2, 2.2, 1])

# ------------------------------------------------------------
# CONSOLE LEFT
# ------------------------------------------------------------
with col_console:
    st.markdown("### Console")

    st.text_area("", "\n".join(st.session_state.console), height=360)

    with st.form("cmdform", clear_on_submit=True):
        cmd = st.text_input(" >_")
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
            st.session_state.theme = pay
        elif act == "load":
            node, mode = pay
            st.session_state.node = node
            st.session_state.mode = mode
            st.session_state.console.append(f"Loading {node} [{mode}]")
        st.rerun()

# ------------------------------------------------------------
# SANDBOX CENTER
# ------------------------------------------------------------
with col_sandbox:
    st.markdown(f"### Sandbox — {NODES[st.session_state.node]['label']}")
    sandbox(st.session_state.node, st.session_state.mode)

# ------------------------------------------------------------
# NODES RIGHT
# ------------------------------------------------------------
with col_nodes:
    st.markdown("### Nodes")

    for key, meta in NODES.items():
        active = " node-active" if key == st.session_state.node else ""

        st.markdown(
            f"<div class='node-card{active}'>"
            f"<div class='node-title'>{meta['label']}</div>"
            f"<div class='node-url'>{meta['url']}</div></div>",
            unsafe_allow_html=True
        )

        if st.button(f"CONNECT {key}"):
            st.session_state.node = key
            st.session_state.mode = DEFAULT_MODE[key]
            st.rerun()

        c1, c2, c3, c4 = st.columns(4)

        if c1.button("HOLO", key=f"holo_{key}"):
            st.session_state.node = key
            st.session_state.mode = "holo"
            st.rerun()

        if c2.button("HARD", key=f"hard_{key}"):
            st.session_state.node = key
            st.session_state.mode = "hardcore"
            st.rerun()

        if c3.button("HACK", key=f"hacker_{key}"):
            st.session_state.node = key
            st.session_state.mode = "hacker"
            st.rerun()

        if c4.button("ELITE", key=f"elite_{key}"):
            st.session_state.node = key
            st.session_state.mode = "elite"
            st.rerun()

# ------------------------------------------------------------
# END OF FILE
# ------------------------------------------------------------

