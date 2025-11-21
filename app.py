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
# INTRO ONE-TIME
# ============================================================

if "intro_done" not in st.session_state:
    intro_html = """
    <div id="introScreen">
        <div class='introText'>BOOTING MAEGIA SYSTEM…</div>
    </div>
    """
    st.session_state.intro_done = True
    st.markdown(intro_html, unsafe_allow_html=True)
    st.stop()

# ============================================================
# SITES AVEC URL EMBED STREAMLIT + MODES PAR DÉFAUT
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

DEFAULT_MODES = {
    "game": "hardcore",
    "kragzouy": "holo",
    "oracle": "holo",
    "pali": "hardcore",
    "cybermind": "fullscreen",
}

# ============================================================
# SONS
# ============================================================

MODE_SOUNDS = {
    "holo": "https://assets.mixkit.co/sfx/preview/mixkit-game-ball-tap-2073.mp3",
    "hardcore": "https://assets.mixkit.co/sfx/preview/mixkit-fast-small-sweep-transition-166.mp3",
    "fullscreen": "https://assets.mixkit.co/sfx/preview/mixkit-arcade-mechanical-bling-2104.mp3",
}

WARP_SOUND = "https://assets.mixkit.co/sfx/preview/mixkit-quick-win-video-game-notification-269.mp3"

# ============================================================
# CSS LOADER
# ============================================================

def load_css():
    css_path = Path("style.css")
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)


# ============================================================
# HELP + LIST COMMANDS
# ============================================================

def help_text():
    return dedent("""
    COMMANDES DISPONIBLES :

      help                       → affiche cette aide
      list                       → liste des nœuds
      clear                      → efface la console

    CONNEXION :

      connect <node>             → charge un nœud
      connect <node> --mode X    → mode visuel personnalisé
      open <node>                → mode FULL WINDOW
      exit                       → sortir du mode FULL WINDOW

    MODES VISUELS :

      holo        → hologramme léger
      hardcore    → glitch + rgb split
      fullscreen  → mode plein écran API
    """)

def list_nodes():
    lines = ["NŒUDS DISPONIBLES :"]
    for key, meta in SITES.items():
        lines.append(f"  - {key:10} → {meta['label']} :: {meta['url']}")
    return "\n".join(lines)


# ============================================================
# PARSEUR DE COMMANDE
# ============================================================

def parse_command(cmd):
    cmd = cmd.strip()
    lower = cmd.lower()

    if lower in ["help", "?", "man"]:
        return {"action": "print", "payload": help_text()}

    if lower in ["clear", "cls"]:
        return {"action": "clear"}

    if lower in ["list", "ls"]:
        return {"action": "print", "payload": list_nodes()}

    if lower.startswith("open "):
        target = lower.split(" ", 1)[1]
        if target in SITES:
            return {
                "action": "fullscreen_app",
                "target": target,
                "url": SITES[target]["url"],
            }
        return {"action": "print", "payload": f"ERREUR : node inconnu '{target}'"}

    if lower in ["exit", "quit", "back"]:
        return {"action": "exit_fullwindow"}

    # CONNECT
    if lower.startswith("connect "):
        parts = lower.split()
        target = parts[1]
        if target not in SITES:
            return {"action": "print", "payload": f"ERREUR : node '{target}' inconnu"}

        mode = DEFAULT_MODES[target]

        if "--mode" in parts:
            idx = parts.index("--mode")
            if idx + 1 < len(parts):
                mode = parts[idx + 1]

        return {
            "action": "load_frame",
            "target": target,
            "url": SITES[target]["url"],
            "mode": mode,
        }

    # SHORT FORM
    if lower in SITES:
        return {
            "action": "load_frame",
            "target": lower,
            "url": SITES[lower]["url"],
            "mode": DEFAULT_MODES[lower],
        }

    return {"action": "print", "payload": f"Commande inconnue : {cmd}"}


# ============================================================
# SANDBOX IFRAME — VERSION FULL DYNAMIQUE
# ============================================================

def sandbox_iframe(url, mode="holo"):
    mode_class = {
        "holo": "cyber-holo cyber-holo-active",
        "hardcore": "cyber-hardcore",
        "fullscreen": ""
    }.get(mode, "cyber-holo")

    sound = MODE_SOUNDS.get(mode, MODE_SOUNDS["holo"])

    html = f"""
    <svg width="0" height="0">
      <filter id="rgb-split">
        <feColorMatrix in="SourceGraphic" type="matrix"
        values="1 0 0 0 0
                0 0 0 0 0
                0 0 0 0 0
                0 0 0 1 0"/>
        <feOffset dx="-2" dy="0" result="r"/>
        <feColorMatrix in="SourceGraphic" type="matrix"
        values="0 0 0 0 0
                0 1 0 0 0
                0 0 0 0 0
                0 0 0 1 0"/>
        <feOffset dx="2" dy="0" result="g"/>
        <feBlend in="r" in2="g" mode="screen"/>
      </filter>
    </svg>

    <audio id="modeSound" src="{sound}"></audio>
    <audio id="warpSound" src="{WARP_SOUND}"></audio>

    <div id="sandboxContainer" class="cybersandbox-frame warp-transition {mode_class}">
        <button class="cyber-fullscreen-btn" onclick="toggleFullscreen()">FULLSCREEN</button>
        <iframe id="sandboxIframe" src="{url}"></iframe>
    </div>

    <script>
    function resizeIframe() {{
        const frame = document.getElementById("sandboxIframe");
        const container = document.getElementById("sandboxContainer");

        let viewport = window.innerHeight;
        let rect = container.getBoundingClientRect();
        let newHeight = viewport - rect.top - 10;

        frame.style.height = newHeight + "px";
        container.style.height = newHeight + "px";
    }}

    window.addEventListener("load", resizeIframe);
    window.addEventListener("resize", resizeIframe);

    document.getElementById("modeSound").play();
    document.getElementById("warpSound").play();

    function toggleFullscreen() {{
        var el = document.getElementById("sandboxContainer");
        if (!document.fullscreenElement) el.requestFullscreen();
        else document.exitFullscreen();
    }}
    </script>
    """

    components.html(html, height=0, scrolling=False)


# ============================================================
# ORACLE AI — MINI IA INTERNE
# ============================================================

def afficher_oracle_ai():
    st.markdown("## ORACLE AI — Assistant Augmenté")
    q = st.text_input("Pose ta question à l’Oracle :")
    if st.button("Interroger"):
        # PLACEHOLDER IA (tu remplaceras par ton API)
        st.markdown("**Réponse :** " + q[::-1])


# ============================================================
# INIT SESSION
# ============================================================

if "console_log" not in st.session_state:
    st.session_state.console_log = [
        "Initialisation système…",
        "Nœud par défaut chargé : CYBERMIND",
        "Tape 'help' pour les commandes.",
    ]

if "current_node" not in st.session_state:
    st.session_state.current_node = "cybermind"

if "current_url" not in st.session_state:
    st.session_state.current_url = SITES["cybermind"]["url"]

if "current_mode" not in st.session_state:
    st.session_state.current_mode = DEFAULT_MODES["cybermind"]

if "fullwindow" not in st.session_state:
    st.session_state.fullwindow = False


# ============================================================
# UI PRINCIPALE
# ============================================================

load_css()

# MODE FULLWINDOW
if st.session_state.fullwindow:
    st.markdown("""
        <style>
        .block-container { padding: 0 !important; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div style='position:fixed;top:15px;left:15px;z-index:100000;'>
            <button onclick="window.location.reload()"
                style="background:rgba(0,246,255,0.3);
                       color:#00f6ff;
                       padding:6px 12px;
                       border:1px solid #00f6ff;
                       border-radius:8px;
                       font-family:Roboto Mono, monospace;">
                EXIT CONSOLE
            </button>
        </div>
    """, unsafe_allow_html=True)

    sandbox_iframe(st.session_state.current_url, "fullscreen")
    st.stop()

# MODE NORMAL
st.markdown('<div class="scanlines"></div>', unsafe_allow_html=True)

col_left, col_right = st.columns([2, 1])

with col_left:

    tab = st.radio(
        "Navigation",
        ["Console", "Info", "Oracle AI"],
        horizontal=True
    )

    if tab == "Console":

        st.markdown("""
        <div class="console-header">
            <div class="console-title">MAEGIA // CYBER CONSOLE</div>
            <div class="console-subtitle">Nœud d’accès aux instances distantes</div>
        </div>
        """, unsafe_allow_html=True)

        console_text = "\n".join(st.session_state.console_log)
        st.text_area("", console_text, height=210)

        with st.form("command", clear_on_submit=True):
            cmd = st.text_input(">_ COMMANDE")
            submit = st.form_submit_button("EXECUTER")

        if submit and cmd:
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
                    f"Chargement de {result['target']} en mode {result['mode']}…"
                )

            elif result["action"] == "fullscreen_app":
                st.session_state.current_node = result["target"]
                st.session_state.current_url = result["url"]
                st.session_state.fullwindow = True

            elif result["action"] == "exit_fullwindow":
                st.session_state.fullwindow = False
                st.session_state.console_log.append("Retour au mode console.")

            st.rerun()

        sandbox_iframe(
            st.session_state.current_url,
            st.session_state.current_mode
        )

    elif tab == "Info":
        st.markdown("## INFORMATIONS SYSTÈME")
        st.write("Nœud actif :", st.session_state.current_node)
        st.write("Mode visuel :", st.session_state.current_mode)
        st.write("URL :", st.session_state.current_url)

    elif tab == "Oracle AI":
        afficher_oracle_ai()


with col_right:
    st.markdown('<div class="right-panel-scroll">', unsafe_allow_html=True)
    st.markdown("""
    <div class="panel">
        <div class="panel-title">Nœuds Maegia</div>
        <div class="panel-subtitle">Accès direct</div>
    </div>
    """, unsafe_allow_html=True)

    for key, meta in SITES.items():
        active = " node-active" if key == st.session_state.current_node else ""
        st.markdown(
            f"""
            <div class="node-card{active}">
                <div class="node-title">{meta['label']}</div>
                <div class="node-url">{meta['url']}</div>
                <div class="node-command">Commande: <span>{meta['code']}</span></div>
                <a class="node-button" href="{meta['url']}" target="_blank">OUVRIR DIRECT</a>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)
