# app.py
import streamlit as st
from pathlib import Path
from textwrap import dedent
import streamlit.components.v1 as components

# ---------- CONFIG GLOBALE ----------
st.set_page_config(
    page_title="Maegia Cyber Console",
    page_icon="⬢",
    layout="wide",
)

SITES = {
    "game": {
        "label": "GAME // Arcade dimensionnelle",
        "url": "https://game.maegia.tv",
        "code": "connect game",
    },
    "kragzouy": {
        "label": "KRAGZOUY // Zone expérimentale",
        "url": "https://kragzouy.maegia.tv",
        "code": "connect kragzouy",
    },
    "oracle": {
        "label": "ORACLE // Divination système",
        "url": "https://oracle.maegia.tv",
        "code": "connect oracle",
    },
    "pali": {
        "label": "PALI // Protocoles linguistiques",
        "url": "https://pali.maegia.tv",
        "code": "connect pali",
    },
    "cybermind": {
        "label": "CYBERMIND // Nœud central",
        "url": "https://cybermind.fr",
        "code": "connect cybermind",
    },
}


# ---------- CSS CUSTOM ----------
def load_css():
    css_path = Path("style.css")
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)


# ---------- TEXTES AIDE / LISTE ----------
def help_text() -> str:
    lines = [
        "COMMANDES DISPONIBLES:",
        "  help              → affiche cette aide",
        "  list              → liste des nœuds disponibles",
        "  clear             → efface l'écran",
        "  connect <noeud>   → charge un nœud dans la fenêtre centrale",
        "",
        "NŒUDS:",
    ]
    for key, meta in SITES.items():
        lines.append(f"  {meta['code']:<20} → {meta['url']}")
    return "\n".join(lines)


def list_nodes() -> str:
    lines = ["NŒUDS DISPONIBLES:"]
    for key, meta in SITES.items():
        lines.append(f"  - {key:10} → {meta['url']}  :: {meta['label']}")
    return "\n".join(lines)


# ---------- PARSEUR DE COMMANDE ----------
def parse_command(cmd: str):
    cmd = cmd.strip()
    if not cmd:
        return {"action": "noop"}

    lower = cmd.lower()

    # help
    if lower in ["help", "?", "man"]:
        return {"action": "print", "payload": help_text()}

    # clear
    if lower in ["clear", "cls", "reset"]:
        return {"action": "clear"}

    # list
    if lower in ["list", "ls", "nodes"]:
        return {"action": "print", "payload": list_nodes()}

    # connect <node>
    if lower.startswith("connect "):
        target = lower.split(" ", 1)[1].strip()
        if target in SITES:
            return {
                "action": "load_frame",
                "target": target,
                "url": SITES[target]["url"],
            }
        else:
            return {
                "action": "print",
                "payload": f"ERREUR: nœud inconnu '{target}'. Tapez 'list' pour voir les nœuds disponibles.",
            }

    # commande brute = nom de nœud (ex: game)
    if lower in SITES:
        return {
            "action": "load_frame",
            "target": lower,
            "url": SITES[lower]["url"],
        }

    # commande inconnue
    return {
        "action": "print",
        "payload": f"COMMANDE INVALIDE: '{cmd}'\nTapez 'help' pour la liste des commandes.",
    }


# ---------- INIT SESSION ----------
if "console_log" not in st.session_state:
    st.session_state.console_log = []
if "last_command" not in st.session_state:
    st.session_state.last_command = ""
if "current_node" not in st.session_state:
    st.session_state.current_node = None
if "current_url" not in st.session_state:
    st.session_state.current_url = None


def append_log(line: str):
    st.session_state.console_log.append(line)


# ---------- UI PRINCIPALE ----------
def main():
    load_css()

    # Overlay scanlines
    st.markdown('<div class="scanlines"></div>', unsafe_allow_html=True)

    col_left, col_right = st.columns([2, 1])

    # --------- COLONNE GAUCHE : CONSOLE + IFRAME ---------
    with col_left:
        st.markdown(
            """
            <div class="console-header">
              <div class="console-title">MAEGIA // CYBER CONSOLE</div>
              <div class="console-subtitle">Nœud d’accès aux instances distantes</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Coquille console
        st.markdown('<div class="console-shell">', unsafe_allow_html=True)

        # Affichage du log
        console_text = (
            "\n".join(st.session_state.console_log)
            if st.session_state.console_log
            else dedent(
                """\
                Initialisation système…
                Tapez 'help' pour afficher la liste des commandes.
                """
            )
        )

        st.text_area(
            label="",
            value=console_text,
            height=220,
            key="console_output",
        )

        # Entrée commande
        with st.form("command_form", clear_on_submit=True):
            cmd = st.text_input(
                label=">_ COMMANDE",
                placeholder="ex: connect game, help, list, clear…",
            )
            submitted = st.form_submit_button("EXECUTER")

        if submitted and cmd:
            st.session_state.last_command = cmd
            append_log(f"> {cmd}")
            result = parse_command(cmd)

            if result["action"] == "print":
                append_log(result["payload"])

            elif result["action"] == "clear":
                st.session_state.console_log = []
                append_log("Console effacée. Tapez 'help' pour commencer.")

            elif result["action"] == "load_frame":
                target = result["target"]
                url = result["url"]
                st.session_state.current_node = target
                st.session_state.current_url = url
                append_log(f"Chargement du nœud '{target}' dans la fenêtre centrale → {url}")

            # rafraîchit pour mettre à jour le iframe
            st.experimental_rerun()

        st.markdown("</div>", unsafe_allow_html=True)  # fin console-shell

        # --------- IFRAME CENTRALE ---------
        if st.session_state.current_url:
            node_label = SITES[st.session_state.current_node]["label"]
            st.markdown(
                f"""
                <div class="panel panel-inline">
                  <div class="panel-title">Fenêtre centrale</div>
                  <div class="panel-subtitle">Nœud actif: {node_label}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # IFRAME avec le site
            components.iframe(
                st.session_state.current_url,
                height=600,
            )
        else:
            st.markdown(
                """
                <div class="panel panel-inline">
                  <div class="panel-title">Fenêtre centrale</div>
                  <div class="panel-subtitle">Aucun nœud chargé. Tapez 'connect game' par exemple.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # --------- COLONNE DROITE: CARDS DES NŒUDS ----------
    with col_right:
        st.markdown(
            """
            <div class="panel">
              <div class="panel-title">Nœuds Maegia</div>
              <div class="panel-subtitle">Accès direct</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        for key, meta in SITES.items():
            active_class = " node-active" if st.session_state.current_node == key else ""
            st.markdown(
                f"""
                <div class="node-card{active_class}">
                  <div class="node-title">{meta['label']}</div>
                  <div class="node-url">{meta['url']}</div>
                  <div class="node-command">Commande: <span>{meta['code']}</span></div>
                  <a class="node-button" href="{meta['url']}" target="_blank">
                    OUVRIR DANS UN ONGLET
                  </a>
                </div>
                """,
                unsafe_allow_html=True,
            )


if __name__ == "__main__":
    main()
