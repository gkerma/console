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
# INTRO CINEMATIQUE
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
# SITES + MODES PAR DÉFAUT
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
# SONS (Mode + Warp + CyberPack complet)
# ============================================================

MODE_SOUNDS = {
    "holo": "https://assets.mixkit.co/sfx/preview/mixkit-game-ball-tap-2073.mp3",
    "hardcore": "https://assets.mixkit.co/sfx/preview/mixkit-fast-small-sweep-transition-166.mp3",
    "fullscreen": "https://assets.mixkit.co/sfx/preview/mixkit-arcade-mechanical-bling-2104.mp3",
}

WARP_SOUND = "https://assets.mixkit.co/sfx/preview/mixkit-quick-win-video-game-notification-269.mp3"

CYBERPACK = [
    "https://assets.mixkit.co/sfx/preview/mixkit-select-click-1109.mp3",
    "https://assets.mixkit.co/sfx/preview/mixkit-retro-game-notification-212.mp3",
    "https://assets.mixkit.co/sfx/preview/mixkit-arcade-retro-coin-2042.mp3",
    "https://assets.mixkit.co/sfx/preview/mixkit-small-hit-in-a-game-2072.mp3",
    "https://assets.mixkit.co/sfx/preview/mixkit-retro-arcade-casino-notification-211.mp3",
    "https://assets.mixkit.co/sfx/preview/mixkit-cool-interface-click-tone-2562.mp3",
    "https://assets.mixkit.co/sfx/preview/mixkit-arcade-bonus-alert-767.mp3",
    "https://assets.mixkit.co/sfx/preview/mixkit-explainer-video-game-alert-1376.mp3",
    "https://assets.mixkit.co/sfx/preview/mixkit-modern-technology-select-3124.mp3",
    "https://assets.mixkit.co/sfx/preview/mixkit-tech-break-interface-2428.mp3",
]

# ============================================================
# CSS
# ============================================================

def load_css():
    css_path = Path("style.css")
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)

# Tilt 3D JS injection (1 seule fois)
st.markdown("""
<script>
document.addEventListener("mousemove", function(e){
    document.querySelectorAll('.node-card').forEach(card=>{
        const r = card.getBoundingClientRect();
        const x = e.clientX - r.left;
        const y = e.clientY - r.top;
        const mx = r.width/2;
        const my = r.height/2;
        const rx = (y - my)/20;
        const ry = (mx - x)/20;
        card.style.setProperty('--rx', rx + 'deg');
        card.style.setProperty('--ry', ry + 'deg');
        card.classList.add("tilt");
    })
});
</script>
""", unsafe_allow_html=True)


# ============================================================
# HELP + LIST COMMANDS
# ============================================================

def help_text():
    return dedent("""
    COMMANDES DISPONIBLES :

      help                       → aide
      list                       → liste des nœuds
      clear                      → efface la console
      exit                       → quitter mode fullwindow

    CONNEXION :
      connect <node>             → charge node
      connect <node> --mode X    → mode visuel personnalisé
      open <node>                → mode FULL WINDOW

    MODES :
      holo | hardcore | fullscreen
    """)

def list_nodes():
    out = ["NœUDS DISPONIBLES :"]
    for k, meta in SITES.items():
        out.append(f"  - {k:10} → {meta['label']} ({meta['url']})")
    return "\n".join(out)


# ============================================================
# PARSEUR DE COMMANDES
# ============================================================

def parse_command(cmd):
    cmd = cmd.strip()
    low = cmd.lower()

    if low in ["help", "?", "man"]:
        return {"action": "print", "payload": help_text()}

    if low in ["clear", "cls"]:
        return {"action": "clear"}

    if low in ["list", "ls"]:
        return {"action": "print", "payload": list_nodes()}

    if low.startswith("open "):
        node = low.split(" ", 1)[1]
        if node in SITES:
            return {"action": "fullscreen", "node": node}
        return {"action": "print", "payload": f"Node inconnu '{node}'"}

    if low in ["exit", "quit", "back"]:
        return {"action": "exit_fullwindow"}

    if low.startswith("connect "):
        parts = low.split()
        node = parts[1]
        if node not in SITES:
            return {"action": "print", "payload": f"Node inconnu '{node}'"}

        mode = DEFAULT_MODES[node]
        if "--mode" in parts:
            mode = parts[parts.index("--mode") + 1]

        return {"action": "load", "node": node, "mode": mode}

    if low in SITES:
        return {"action": "load", "node": low, "mode": DEFAULT_MODES[low]}

    return {"action": "print", "payload": f"Commande inconnue : {cmd}"}


# ============================================================
# SANDBOX IFRAME (Dynamique, Warp, Son)
# ============================================================

def sandbox_iframe(url, mode="holo"):

    klass = {
        "holo": "cyber-holo cyber-holo-active",
        "hardcore": "cyber-hardcore",
        "fullscreen": ""
    }.get(mode, "cyber-holo")

    mode_sound = MODE_SOUNDS.get(mode, MODE_SOUNDS["holo"])
    random_sound = CYBERPACK[0]

    html = f"""
    <audio id="modeSound" src="{mode_sound}"></audio>
    <audio id="warpSound" src="{WARP_SOUND}"></audio>
    <audio id="fxPack" src="{random_sound}"></audio>

    <div id="sandboxContainer" class="cybersandbox-frame warp-transition {klass}">
        <button class="cyber-fullscreen-btn" onclick="toggleFullscreen()">FULLSCREEN</button>
        <iframe id="sandboxIframe" src="{url}"></iframe>
    </div>

    <script>
    function resizeIframe(){{
        const f=document.getElementById("sandboxIframe");
        const c=document.getElementById("sandboxContainer");
        let vh=window.innerHeight;
        let t=c.getBoundingClientRect().top;
        let h=vh - t - 10;
        f.style.height=h+"px";
        c.style.height=h+"px";
    }}
    window.addEventListener("load",resizeIframe);
    window.addEventListener("resize",resizeIframe);

    document.getElementById("modeSound").play();
    document.getElementById("warpSound").play();
    document.getElementById("fxPack").play();

    function toggleFullscreen(){{
        var el = document.getElementById("sandboxContainer");
        if(!document.fullscreenElement) el.requestFullscreen();
        else document.exitFullscreen();
    }}
    </script>
    """

    components.html(html, height=0, scrolling=False)


# ============================================================
# ORACLE AI
# ============================================================

def oracle_ai():
    st.markdown("## ORACLE AI — Assistant Intégré")
    q = st.text_input("Pose ta question :")
    if st.button("Interroger"):
        st.write("Réponse :", q[::-1])  # Placeholder IA


# ============================================================
# INIT SESSION
# ============================================================

if "console" not in st.session_state:
    st.session_state.console = [
        "Initialisation système…",
        "Nœud par défaut : CYBERMIND",
        "Tape 'help' pour les commandes."
    ]

if "node" not in st.session_state:
    st.session_state.node = "cybermind"

if "mode" not in st.session_state:
    st.session_state.mode = DEFAULT_MODES["cybermind"]

if "url" not in st.session_state:
    st.session_state.url = SITES["cybermind"]["url"]

if "fullwindow" not in st.session_state:
    st.session_state.fullwindow = False


# ============================================================
# UI PRINCIPALE
# ============================================================

load_css()

# FULLWINDOW
if st.session_state.fullwindow:
    st.markdown("""
        <style>.block-container {padding:0!important;}</style>
        <div style="position:fixed;top:15px;left:15px;z-index:999999;">
            <button onclick="window.location.reload()"
                style="background:rgba(0,246,255,0.3);
                       border:1px solid #00f6ff;
                       color:#00f6ff;padding:6px 12px;
                       border-radius:8px;font-family:Roboto Mono;">
                EXIT
            </button>
        </div>
    """, unsafe_allow_html=True)

    sandbox_iframe(st.session_state.url, "fullscreen")
    st.stop()

st.markdown('<div class="scanlines"></div>', unsafe_allow_html=True)

col_left, col_right = st.columns([2, 1])

# ============================================================
# COLONNE GAUCHE
# ============================================================

with col_left:

    tab = st.radio("Navigation", ["Console", "Info", "Oracle AI"], horizontal=True)

    if tab == "Console":

        console_text = "\n".join(st.session_state.console)
        st.text_area("", console_text, height=200)

        with st.form("cmd", clear_on_submit=True):
            cmd = st.text_input(">_")
            go = st.form_submit_button("EXECUTER")

        if go and cmd:
            st.session_state.console.append("> " + cmd)
            result = parse_command(cmd)

            if result["action"] == "print":
                st.session_state.console.append(result["payload"])

            elif result["action"] == "clear":
                st.session_state.console = ["Console effacée."]

            elif result["action"] == "exit_fullwindow":
                st.session_state.fullwindow = False

            elif result["action"] == "fullscreen":
                st.session_state.node = result["node"]
                st.session_state.url = SITES[result["node"]]["url"]
                st.session_state.fullwindow = True

            elif result["action"] == "load":
                st.session_state.node = result["node"]
                st.session_state.mode = result["mode"]
                st.session_state.url = SITES[result["node"]]["url"]
                st.session_state.console.append(f"Chargement {result['node']} en mode {result['mode']}…")

            st.rerun()

        sandbox_iframe(st.session_state.url, st.session_state.mode)

    elif tab == "Info":
        st.write("Nœud actif :", st.session_state.node)
        st.write("Mode :", st.session_state.mode)
        st.write("URL :", st.session_state.url)

    elif tab == "Oracle AI":
        oracle_ai()


# ============================================================
# COLONNE DROITE — CARDS 3D + BOUTONS
# ============================================================

with col_right:
    st.markdown('<div class="right-panel-scroll">', unsafe_allow_html=True)

    for key, meta in SITES.items():

        active = " node-active" if key == st.session_state.node else ""

        st.markdown(
            f"""
            <div class="node-card {active}">
                <div class="node-title">{meta['label']}</div>
                <div class="node-url">{meta['url']}</div>
            </div>
            """, unsafe_allow_html=True
        )

        # Bouton console connect
        if st.button(f"connect {key}", key=f"b_{key}_connect"):
            cmd = f"connect {key} --mode {DEFAULT_MODES[key]}"
            st.session_state.console.append("> " + cmd)
            st.session_state.node = key
            st.session_state.url = meta["url"]
            st.session_state.mode = DEFAULT_MODES[key]
            st.rerun()

        # FULLWINDOW
        if st.button(f"FULLWINDOW {key}", key=f"b_{key}_fw"):
            st.session_state.console.append("> open " + key)
            st.session_state.node = key
            st.session_state.url = meta["url"]
            st.session_state.fullwindow = True
            st.rerun()

        # Modes HOLO / HARDCORE / FULLSCREEN
        m1, m2, m3 = st.columns(3)

        if m1.button(f"HOLO {key}", key=f"h_{key}"):
            cmd = f"connect {key} --mode holo"
            st.session_state.console.append("> " + cmd)
            st.session_state.node = key
            st.session_state.mode = "holo"
            st.session_state.url = meta["url"]
            st.rerun()

        if m2.button(f"HARD {key}", key=f"hc_{key}"):
            cmd = f"connect {key} --mode hardcore"
            st.session_state.console.append("> " + cmd)
            st.session_state.node = key
            st.session_state.mode = "hardcore"
            st.session_state.url = meta["url"]
            st.rerun()

        if m3.button(f"FULL {key}", key=f"fl_{key}"):
            cmd = f"connect {key} --mode fullscreen"
            st.session_state.console.append("> " + cmd)
            st.session_state.node = key
            st.session_state.mode = "fullscreen"
            st.session_state.url = meta["url"]
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
