# app.py
import streamlit as st
from pathlib import Path
from textwrap import dedent

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


# ---------- LOGIQUE CONSOLE ----------
def help_text() -> str:
    lines = [
        "COMMANDES DISPONIBLES:",
        "  help              → affiche cette aide",
        "  list              → liste des nœuds disponibles",
        "  clear             → efface l'écran",
        "  connect <noeud>   → ouvre un portail vers un nœud",
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
                "action": "redirect",
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
            "action": "redirect",
            "target": lower,
            "url": SITES[lower]["url"],
        }

    # par défaut: commande inconnue
    return {
        "action": "print",
        "payload": f"COMMANDE INVALIDE: '{cmd}'\nTapez 'help' pour la liste des commandes.",
    }


# ---------- INIT SESSION ----------
if "console_log" not in st.session_state:
    st.session_state.console_log = []
if "last_command" not in st.session_state:
    st.session_state.last_command = ""


def append_log(line: str):
    st.session_state.console_log.append(line)


# ---------- UI PRINCIPALE ----------
def main():
    load_css()

    # Overlay scanlines
    st.markdown('<div class="scanlines"></div>', unsafe_allow_html=True)

    col_left, col_right = st.columns([2, 1])

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

        # Zone console
        st.markdown('<div class="console-shell">', unsafe_allow_html=True)

        # Affichage du log
        console_text = ""
        if st.session_state.console_log:
            console_text = "\n".join(st.session_state.console_log)
        else:
            console_text = dedent(
                """\
                Initialisation système…
                Tapez 'help' pour afficher la liste des commandes.
                """
            )

        st.text_area(
            label="",
            value=console_text,
            height=260,
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

            elif result["action"] == "redirect":
                target = result["target"]
                url = result["url"]
                append_log(f"Ouverture du portail vers '{target}' → {url}")
                # Affichage du lien cliquable + redirection automatique via meta-refresh
                st.markdown(
                    f"""
                    <meta http-equiv="refresh" content="0; url={url}">
                    <p class="redirect-msg">
                      Redirection vers <a href="{url}" target="_self">{url}</a>…
                    </p>
                    """,
                    unsafe_allow_html=True,
                )
            # Force refresh de l'affichage
            st.experimental_rerun()

        st.markdown("</div>", unsafe_allow_html=True)  # fin console-shell

    # --------- PANNEAU DROIT: CARDS DES NŒUDS ---------
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
            st.markdown(
                f"""
                <div class="node-card">
                  <div class="node-title">{meta['label']}</div>
                  <div class="node-url">{meta['url']}</div>
                  <div class="node-command">Commande: <span>{meta['code']}</span></div>
                  <a class="node-button" href="{meta['url']}" target="_blank">
                    OUVRIR LE NŒUD
                  </a>
                </div>
                """,
                unsafe_allow_html=True,
            )


if __name__ == "__main__":
    main()
