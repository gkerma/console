import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path
from textwrap import dedent

st.set_page_config(
    page_title="Maegia Cyber Console",
    page_icon="⬢",
    layout="wide",
)

# ============================================================
# CONFIG MODES PAR DÉFAUT
# ============================================================

DEFAULT_MODES = {
    "game": "hardcore",
    "kragzouy": "holo",
    "oracle": "holo",
    "pali": "hardcore",
    "cybermind": "fullscreen",
}

# ============================================================
# SITES AVEC URL EMBED
# ============================================================

SITES = {
    "game": {
        "label": "GAME // Arcade dimensionnelle",
        "url": "https://game.maegia.tv/?embed=true&embed_options=dark_theme&embed_options=disable_scrolling",
        "code": "connect game",
    },
    "kragzouy": {
        "label": "KRAGZOUY // Zone expérimentale",
        "url": "https://kragzouy.maegia.tv/?embed=true&embed_options=dark_theme&embed_options=disable_scrolling",
        "code": "connect kragzouy",
    },
    "oracle": {
        "label": "ORACLE // Divination système",
        "url": "https://oracle.maegia.tv/?embed=true&embed_options=dark_theme&embed_options=disable_scrolling",
        "code": "connect oracle",
    },
    "pali": {
        "label": "PALI // Protocoles linguistiques",
        "url": "https://pali.maegia.tv/?embed=true&embed_options=dark_theme&embed_options=disable_scrolling",
        "code": "connect pali",
    },
    "cybermind": {
        "label": "CYBERMIND // Nœud central",
        "url": "https://cybermind.fr",
        "code": "connect cybermind",
    },
}

# ============================================================
# CSS LOADER
# ============================================================

def load_css():
    css_path = Path("style.css")
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)


# ============================================================
# MESSAGE AIDE
# ============================================================

def help_text() -> str:
    return dedent("""
    COMMANDES DISPONIBLES :

      help                     → affiche cette aide
      list                     → liste des nœuds disponibles
      clear                    → efface la console

      connect <noeud>          → ouvre un nœud
      connect <noeud> --mode X → ouvre un nœud avec le mode visuel

    MODES VISUELS DISPONIBLES :

      holo        → hologramme léger
      hardcore    → glitch, RGB, distortion
      fullscreen  → plein écran API

    EXEMPLES :
      connect oracle
      connect oracle --mode hardcore
      connect game --mode holo

    """)


# ============================================================
# LISTE DES NŒUDS
# ============================================================

def list_nodes() -> str:
    lines = ["NŒUDS DISPONIBLES :"]
    for key, meta in SITES.items():
        lines.append(f"  - {key:10} → {meta['url']}  :: {meta['label']}")
    return "\n".join(lines)


# ============================================================
# PARSEUR DE COMMANDE
# ============================================================

def parse_command(cmd: str):
    cmd = cmd.strip()
    if not cmd:
        return {"action": "noop"}

    lower = cmd.lower()

    if lower in ["help", "?", "man"]:
        return {"action": "print", "payload": help_text()}

    if lower in ["clear", "cls", "reset"]:
        return {"action": "clear"}

    if lower in ["list", "ls", "nodes"]:
        return {"action": "print", "payload": list_nodes()}

    # CONNECT + optional mode
    if lower.startswith("connect "):
        parts = lower.split()

        if len(parts) >= 2:
            target = parts[1]

            if target not in SITES:
                return {
                    "action": "print",
                    "payload": f"ERREUR : nœud inconnu '{target}'"
                }

            # MODE PERSONNALISÉ
            mode = DEFAULT_MODES.get(target, "holo")

            if "--mode" in parts:
                mode_index = parts.index("--mode")
                if len(parts) > mode_index + 1:
                    mode = parts[mode_index + 1]

            return {
                "action": "load_frame",
                "target": target,
                "url": SITES[target]["url"],
                "mode": mode,
            }

    # COMMANDES COURTES (ex : game)
    if lower in SITES:
        target = lower
        mode = DEFAULT_MODES[target]
        return {
            "action": "load_frame",
            "target": target,
            "url": SITES[target]["url"],
            "mode": mode,
        }

    return {
        "action": "print",
        "payload": f"COMMANDE INVALIDE : '{cmd}'\nTape 'help' pour les commandes."
    }


# ============================================================
# SANDBOX EMBED + MODES VISUELS + SON
# ============================================================

def sandbox_iframe(url: str, mode="holo", height: int = 750):
    mode_class = {
        "holo": "cyber-holo cyber-holo-active",
        "hardcore": "cyber-hardcore",
        "fullscreen": ""
    }.get(mode, "cyber-holo")

    html = f"""
    <svg width="0" height="0">
      <filter id="rgb-split">
        <feColorMatrix in="SourceGraphic" type="matrix"
          values="1 0 0 0 0
                  0 0 0 0 0
                  0 0 0 0 0
                  0 0 0 1 0"/>
        <feOffset dx="-2" dy="0" result="r" />
        <feColorMatrix in="SourceGraphic" type="matrix"
          values="0 0 0 0 0
                  0 1 0 0 0
                  0 0 0 0 0
                  0 0 0 1 0"/>
        <feOffset dx="2" dy="0" result="g" />
        <feBlend in="r" in2="g" mode="screen" />
      </filter>
    </svg>

    <audio id="modeSound" src="https://assets.mixkit.co/sfx/preview/mixkit-select-click-1109.mp3"></audio>

    <div class="cybersandbox-frame {mode_class}" id="sandboxFrame" style="height:{height}px;">
        <button class="cyber-fullscreen-btn" onclick="toggleFullscreen()">FULLSCREEN</button>
        <iframe id="sandboxIframe" src="{url}"></iframe>
    </div>

    <script>
    function toggleFullscreen() {{
        var frame = document.getElementById("sandboxFrame");
        if (!document.fullscreenElement) {{
            frame.requestFullscreen();
        }} else {{
            document.exitFullscreen();
        }}
    }}

    document.getElementById("modeSound").play();
    </script>
    """

    components.html(html, height=height+60, scrolling=False)


# ============================================================
# INITIALISATION SESSION
# ============================================================

if "console_log" not in st.session_state:
    st.session_state.console_log = [
        "Initialisation système…",
        "Nœud par défaut chargé : CYBERMIND",
        "Tape 'help' pour afficher les commandes.",
    ]

if "current_node" not in st.session_state:
    st.session_state.current_node = "cybermind"

if "current_url" not in st.session_state:
    st.session_state.current_url = SITES["cybermind"]["url"]

if "current_mode" not in st.session_state:
    st.session_state.current_mode = DEFAULT_MODES["cybermind"]


# ============================================================
# UI PRINCIPALE
# ============================================================

load_css()

st.markdown('<div class="scanlines"></div>', unsafe_allow_html=True)

col_left, col_right = st.columns([2, 1])

with col_left:

    st.markdown("""
        <div class="console-header">
            <div class="console-title">MAEGIA // CYBER CONSOLE</div>
            <div class="console-subtitle">Nœud d’accès aux instances distantes</div>
        </div>
    """, unsafe_allow_html=True)

    # Console
    console_text = "\n".join(st.session_state.console_log)

    st.text_area("", console_text, height=210, key="console_output")

    with st.form("command_form", clear_on_submit=True):
        cmd = st.text_input(">_ COMMANDE", "")
        submitted = st.form_submit_button("EXECUTER")

    if submitted and cmd:
        st.session_state.console_log.append("> " + cmd)
        result = parse_command(cmd)

        if result["action"] == "print":
            st.session_state.console_log.append(result["payload"])

        elif result["action"] == "clear":
            st.session_state.console_log = [
                "Console effacée.",
                "Tape 'help' pour recommencer."
            ]

        elif result["action"] == "load_frame":
            st.session_state.current_node = result["target"]
            st.session_state.current_url = result["url"]
            st.session_state.current_mode = result["mode"]

            st.session_state.console_log.append(
                f"Chargement du nœud '{result['target']}' en mode {result['mode']} → {result['url']}"
            )

        st.rerun()

    # AFFICHAGE IFRAME
    st.markdown(
        f"""
        <div class="panel panel-inline">
            <div class="panel-title">Fenêtre centrale</div>
            <div class="panel-subtitle">Nœud actif : {SITES[st.session_state.current_node]['label']}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    sandbox_iframe(
        st.session_state.current_url,
        mode=st.session_state.current_mode,
        height=750
    )


# ============================================================
# COLONNE DROITE (cartes nœuds)
# ============================================================

with col_right:
    st.markdown("""
    <div class="panel">
        <div class="panel-title">Nœuds Maegia</div>
        <div class="panel-subtitle">Accès direct</div>
    </div>
    """, unsafe_allow_html=True)

    for key, meta in SITES.items():
        active_class = " node-active" if st.session_state.current_node == key else ""
        st.markdown(
            f"""
            <div class="node-card{active_class}">
              <div class="node-title">{meta['label']}</div>
              <div class="node-url">{meta['url']}</div>
              <div class="node-command">Commande: <span>{meta['code']}</span></div>
              <a class="node-button" href="{meta['url']}" target="_blank">OUVRIR DIRECT</a>
            </div>
            """,
            unsafe_allow_html=True,
        )
