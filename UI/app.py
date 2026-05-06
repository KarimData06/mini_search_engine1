import streamlit as st
import requests
from streamlit_searchbox import st_searchbox

import os
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="Mini Search Engine", page_icon="🔎", layout="wide")

if "page" not in st.session_state: st.session_state.page = 1
if "query" not in st.session_state: st.session_state.query = ""

# ── Sidebar ────────────────────────────────────────────────────────
st.sidebar.header("Filtres")
filter_category = st.sidebar.selectbox("Catégorie", ["Toutes", "cs.LG", "stat.ML"])
filter_author   = st.sidebar.text_input("Auteur")
page_size       = st.sidebar.selectbox("Résultats par page", [5, 10, 20], index=1)
st.sidebar.markdown("---")
st.sidebar.caption("Mini Search Engine · arXiv ML")

col_logo, col_title = st.columns([1, 5])

with col_logo:
    st.image("assets/logo.png", width=120)

with col_title:
    st.title("arXiv ML Search")
    st.caption("Moteur de recherche d'articles ML sur arXiv")

# ── Fonction suggestions (appelée à chaque frappe) ─────────────────
def fetch_suggestions(q: str):
    if not q or len(q) < 2:
        return []
    try:
        resp = requests.get(f"{API_URL}/suggest", params={"q": q}, timeout=1)
        suggestions = resp.json().get("suggestions", [])
        # Retourne les suggestions complètes : "machine learn", "machine svm"...
        return [q + " " + s for s in suggestions]
    except:
        return []

# ── Barre de recherche avec autocomplete temps réel ────────────────
col1, col2 = st.columns([1, 6])

with col1:
    search_clicked = st.button("🔍", use_container_width=True)

with col2:
    selected = st_searchbox(
        fetch_suggestions,
        placeholder="Ex: transformer attention, gradient descent...",
        key="searchbox",
        default_use_searchterm=True,
    )

# ── Déclencher la recherche ────────────────────────────────────────
if search_clicked and selected:
    st.session_state.query = selected
    st.session_state.page  = 1

query = st.session_state.query
page  = st.session_state.page

# ── Résultats ──────────────────────────────────────────────────────
if query:
    api_params = {"q": query, "page": page, "size": page_size}
    if filter_category != "Toutes": api_params["category"] = filter_category
    if filter_author:               api_params["author"]   = filter_author

    with st.spinner("Recherche en cours..."):
        response = requests.get(f"{API_URL}/search", params=api_params)

    if response.status_code == 200:
        data    = response.json()
        results = data["results"]
        total   = data["total"]
        pages   = data["pages"]

        if not results:
            st.warning("Aucun résultat trouvé.")
        else:
            st.success(f"{total} résultats pour **{query}** — page {page}/{pages}")

            st.markdown("""<style>
            .card{background:#1e1e2e;border:1px solid #313244;border-radius:12px;
                  padding:20px 24px;margin-bottom:16px}
            .card-title{font-size:18px;font-weight:600;color:#cdd6f4;margin-bottom:6px}
            .card-meta{font-size:12px;color:#6c7086;margin-bottom:10px}
            .card-abstract{font-size:14px;color:#a6adc8;line-height:1.6;margin-bottom:12px}
            .badge{display:inline-block;background:#313244;color:#89b4fa;
                   border-radius:6px;padding:2px 10px;font-size:12px;margin-right:6px}
            .score-pill{display:inline-block;background:#a6e3a1;color:#1e1e2e;
                        border-radius:20px;padding:2px 10px;font-size:12px;font-weight:600}
            a.pdf-btn{display:inline-block;background:#89b4fa;color:#1e1e2e !important;
                      border-radius:8px;padding:4px 14px;font-size:13px;font-weight:600;
                      text-decoration:none;margin-top:8px}
            </style>""", unsafe_allow_html=True)

            for r in results:
                pdf = r.get("pdf", "")
                pdf_btn = f'<a class="pdf-btn" href="{pdf}" target="_blank">📄 Voir le PDF</a>' if pdf else ''
                st.markdown(f"""
                <div class="card">
                <div class="card-title">{r['title']}</div>
                <div class="card-meta">
                <span class="badge">📂 {r.get('category','')}</span>
                ✍️ {r.get('authors','')[:80]}
            </div>
            <div class="card-abstract">{r['abstract']}</div>
            <span class="score-pill">⭐ {r['score']}</span>
            {pdf_btn}
            </div>""", unsafe_allow_html=True)

            # ── Pagination ─────────────────────────────────────────
            if pages > 1:
                st.markdown("---")
                c1, c2, c3 = st.columns([1, 4, 1])
                with c1:
                    if page > 1:
                        if st.button("← Précédent"):
                            st.session_state.page = page - 1
                            st.rerun()
                with c2:
                    s = max(1, page - 3)
                    e = min(pages, s + 6)
                    pcols = st.columns(e - s + 1)
                    for i, p_num in enumerate(range(s, e + 1)):
                        with pcols[i]:
                            if st.button(f"**{p_num}**" if p_num == page else str(p_num), key=f"p{p_num}"):
                                st.session_state.page = p_num
                                st.rerun()
                with c3:
                    if page < pages:
                        if st.button("Suivant →"):
                            st.session_state.page = page + 1
                            st.rerun()
    else:
        st.error("Erreur API — vérifie que uvicorn tourne.")