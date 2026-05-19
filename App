import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import warnings
warnings.filterwarnings("ignore")

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="StartSe · KAM Analytics 2026",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Color palette ──────────────────────────────────────────────────────────────
COLORS = {
    "primary":   "#0F2B5B",
    "accent":    "#E8512A",
    "green":     "#1DB954",
    "yellow":    "#F5A623",
    "red":       "#E8512A",
    "blue":      "#2D6BE4",
    "light_bg":  "#F7F8FA",
    "card_bg":   "#FFFFFF",
    "text":      "#1A1A2E",
    "subtext":   "#6B7280",
}

KAM_COLORS = [
    "#0F2B5B","#2D6BE4","#E8512A","#1DB954","#F5A623",
    "#9B59B6","#1ABC9C","#E74C3C","#F39C12","#3498DB",
    "#2ECC71","#E67E22","#8E44AD","#16A085","#D35400",
]

STATUS_COLORS = {
    "Pago":         "#1DB954",
    "Adimplente":   "#2D6BE4",
    "Não Iniciado": "#F5A623",
    "Em Atraso":    "#E8512A",
    "??":           "#9B59B6",
}

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

  .main { background-color: #F7F8FA; }

  /* Hero header */
  .hero {
    background: linear-gradient(135deg, #0F2B5B 0%, #1a3f7a 100%);
    border-radius: 16px;
    padding: 28px 36px;
    margin-bottom: 24px;
    color: white;
  }
  .hero h1 { font-size: 2rem; font-weight: 800; margin: 0; letter-spacing: -0.5px; }
  .hero p  { font-size: 0.95rem; opacity: 0.75; margin: 6px 0 0; }

  /* KPI cards */
  .kpi-card {
    background: white;
    border-radius: 12px;
    padding: 20px 24px;
    box-shadow: 0 1px 4px rgba(0,0,0,.08);
    border-left: 4px solid #0F2B5B;
    height: 100%;
  }
  .kpi-label { font-size: 0.75rem; font-weight: 600; color: #6B7280; text-transform: uppercase; letter-spacing: .5px; }
  .kpi-value { font-size: 2rem; font-weight: 800; color: #0F2B5B; margin: 4px 0 2px; }
  .kpi-sub   { font-size: 0.8rem; color: #6B7280; }

  /* Section headers */
  .section-title {
    font-size: 1.1rem; font-weight: 700; color: #0F2B5B;
    margin: 24px 0 12px; padding-bottom: 8px;
    border-bottom: 2px solid #E8512A;
    display: inline-block;
  }

  /* Insight box */
  .insight-box {
    background: #EFF6FF;
    border: 1px solid #BFDBFE;
    border-radius: 10px;
    padding: 14px 18px;
    margin-bottom: 10px;
    font-size: 0.88rem;
    color: #1E3A5F;
  }
  .insight-box.warn {
    background: #FFF7ED; border-color: #FED7AA; color: #7C2D12;
  }
  .insight-box.ok {
    background: #F0FDF4; border-color: #BBF7D0; color: #14532D;
  }

  div[data-testid="stSidebarContent"] { background: #0F2B5B; }
  div[data-testid="stSidebarContent"] label { color: #CBD5E1 !important; }
  div[data-testid="stSidebarContent"] .stSelectbox label { color: #CBD5E1 !important; }
  div[data-testid="stSidebarContent"] h2, div[data-testid="stSidebarContent"] h3 { color: white !important; }
  .stMultiSelect span { font-size: 0.8rem; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# DATA LOADING & PROCESSING
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_data
def load_sales(path: str) -> pd.DataFrame:
    df = pd.read_excel(path, sheet_name="Sheet1")
    df["Data"] = pd.to_datetime(df["Data"], dayfirst=True, errors="coerce")
    df["Mês"] = df["Mês"].astype(int)
    df["Total"] = pd.to_numeric(df["Total"], errors="coerce").fillna(0)
    df["Quantidade"] = pd.to_numeric(df["Quantidade"], errors="coerce").fillna(0)
    df["Status_financeiro"] = df["Status_financeiro"].fillna("??")

    # Friendly KAM names
    name_map = {
        "Alvaro Carnio":                         "Álvaro Carnio",
        "CAIO BATISTA PAIXAO":                   "Caio Paixão",
        "JULIA CHAGAS DINIZ CAMARGO":            "Julia Camargo",
        "GUSTAVO MARQUES DE ALMEIDA":            "Gustavo Almeida",
        "LIGIA TORCATTO FRANZINI":               "Lígia Franzini",
        "FELIPE BARBOSA DOS SANTOS VASCONCELOS": "Felipe Vasconcelos",
        "Leticia Lenox Lage Paulino":            "Leticia Paulino",
        "Pedro Lobel":                           "Pedro Lobel",
        "Fernanda França Bittencourt":           "Fernanda Bittencourt",
        "Andre Luis Kohama":                     "André Kohama",
        "Felipe Frias Ceitlin":                  "Felipe Ceitlin",
        "Bruna Freire Silva":                    "Bruna Silva",
        "Junior Borneli":                        "Junior Borneli",
        "Luis Fernando Roos Acosta":             "Luis Acosta",
        "Moises Cicero Brito Irmao":             "Moises Irmão",
    }
    df["KAM"] = df["Vendedor"].map(name_map).fillna(df["Vendedor"])

    # Payment health
    df["Pago_flag"]   = (df["Status_financeiro"] == "Pago").astype(int)
    df["Atraso_flag"] = (df["Status_financeiro"] == "Em Atraso").astype(int)

    # Product group (short label)
    def prod_group(p):
        p = str(p)
        for kw, label in [
            ("AI Festival", "AI Festival"),
            ("SLD", "SLD"),
            ("AI for Leaders", "AI for Leaders"),
            ("RH Leadership", "RH Leadership"),
            ("China", "Imersão China"),
            ("Executive Program", "Executive Program"),
            ("AI Strategy", "AI Strategy"),
            ("NRF", "NRF Download"),
            ("Consulting", "Consulting"),
            ("COMPESA", "Corporate Program"),
            ("Sebrae", "Corporate Program"),
            ("New Brokers", "Corporate Program"),
            ("Renovação", "Renovação/Renewal"),
            ("Talks", "Talks/Eventos"),
        ]:
            if kw.lower() in p.lower():
                return label
        return "Outros"
    df["Produto_grupo"] = df["Produto"].apply(prod_group)

    # Month name
    mes_map = {1:"Jan",2:"Fev",3:"Mar",4:"Abr",5:"Mai",6:"Jun",
               7:"Jul",8:"Ago",9:"Set",10:"Out",11:"Nov",12:"Dez"}
    df["Mês_nome"] = df["Mês"].map(mes_map)
    return df


@st.cache_data
def load_cohort(path: str):
    xl = pd.read_excel(path, sheet_name=None)

    # ── KAM meta sheet ──────────────────────────────────────────────────────
    df_kam_raw = xl["Venda x Mês 2026 KAM - Caio"]
    months = ["jan","fev","mar","abr","mai","jun","jul","ago","set","out","nov","dez"]
    col_map = {df_kam_raw.columns[i+3]: m for i, m in enumerate(months)}
    df_kam_raw = df_kam_raw.rename(columns=col_map)
    df_kam_raw.columns = [str(c).strip() for c in df_kam_raw.columns]

    # rows 1-11 are KAMs
    kam_rows = df_kam_raw.iloc[1:12].copy()
    kam_rows.columns = df_kam_raw.columns
    kam_meta = []
    for _, r in kam_rows.iterrows():
        if pd.notna(r.get("KAM")):
            row = {
                "KAM_short": str(r["KAM"]).strip(),
                "Tier": str(r.get("Unnamed: 0", "")).strip(),
                "Atuacao": str(r.get("Unnamed: 1", "")).strip(),
                "Total_meta": pd.to_numeric(r.get("Total"), errors="coerce"),
            }
            for m in months:
                row[f"meta_{m}"] = pd.to_numeric(r.get(m, 0), errors="coerce")
            kam_meta.append(row)
    df_meta = pd.DataFrame(kam_meta)

    # Realizado 2025 by KAM (columns 22-25 area)
    df_kam_real = df_kam_raw.copy()
    for idx, r in df_kam_raw.iloc[1:12].iterrows():
        nm = str(r.get("KAM", "")).strip()
        real = pd.to_numeric(r.get("Unnamed: 23", None), errors="coerce")
        if nm and pd.notna(real):
            df_meta.loc[df_meta["KAM_short"] == nm, "realizado_2025"] = real

    # ── Corporate cohort sheet ─────────────────────────────────────────────
    cohort = xl["Cohort venda x receita 2026"]
    c = cohort.copy()

    def extract_cohort_section(start_row, label):
        # Find the rows with month data
        rows = []
        for i in range(start_row, min(start_row+15, len(c))):
            row = c.iloc[i]
            mes = str(row.iloc[0]).strip()
            if mes in ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"]:
                venda_2026 = pd.to_numeric(row.iloc[2], errors="coerce")
                rows.append({"mes": mes, "venda_2026": venda_2026, "segmento": label})
        return pd.DataFrame(rows)

    corp_df = extract_cohort_section(4, "Corporate")
    cons_df = extract_cohort_section(23, "Consulting")

    # Revenue meta from cohort (rows 17/37)
    def extract_meta_receita(start_row):
        for i in range(start_row, min(start_row+6, len(c))):
            row = c.iloc[i]
            label = str(row.iloc[0]).strip()
            if "Meta receita" in label or "Meta Receita" in label:
                vals = {}
                month_labels = ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"]
                for j, m in enumerate(month_labels):
                    vals[m] = pd.to_numeric(c.iloc[i].iloc[4+j], errors="coerce")
                return vals
        return {}

    meta_corp   = extract_meta_receita(14)
    meta_cons   = extract_meta_receita(33)

    # Real receita (row 54 = Corp+Cons actual)
    real_rec = {}
    month_labels = ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"]
    for i in range(50, 60):
        if i < len(c):
            row = c.iloc[i]
            if "TOTAL" in str(row.iloc[0]):
                for j, m in enumerate(month_labels):
                    real_rec[m] = pd.to_numeric(row.iloc[4+j], errors="coerce")
                break

    # Meta receita corp + cons combined
    meta_combined = {m: (meta_corp.get(m, 0) or 0) + (meta_cons.get(m, 0) or 0)
                     for m in month_labels}

    return df_meta, pd.concat([corp_df, cons_df], ignore_index=True), meta_combined, real_rec


# ── Load ───────────────────────────────────────────────────────────────────────
SALES_FILE  = "vendas_por_kam__2026_.xlsx"
COHORT_FILE = "Analise_cohort_vendas_receita_2026_B2B__2_.xlsx"

try:
    df = load_sales(SALES_FILE)
    df_meta, df_cohort_vendas, meta_combined, real_rec = load_cohort(COHORT_FILE)
    data_ok = True
except FileNotFoundError:
    st.error("❌ Arquivos não encontrados. Coloque os arquivos .xlsx na mesma pasta do app.py")
    st.stop()


# ── KAM short name → full mapping ─────────────────────────────────────────────
short_to_full = {
    "Lobel":       "Pedro Lobel",
    "Fernanda":    "Fernanda Bittencourt",
    "Kohama":      "André Kohama",
    "Álvaro":      "Álvaro Carnio",
    "Gustavo":     "Gustavo Almeida",
    "Caio P.":     "Caio Paixão",
    "Lígia":       "Lígia Franzini",
    "Felipe V.":   "Felipe Vasconcelos",
    "Julia C.":    "Julia Camargo",
    "KAM 1":       "KAM 1 (Inbound)",
    "KAM 2":       "KAM 2 (Inbound)",
}

MES_ORDER   = ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"]
MES_NUM     = {m: i+1 for i, m in enumerate(MES_ORDER)}
ACTIVE_KAMS = [k for k in df["KAM"].unique() if df[df["KAM"]==k]["Total"].sum() > 0]


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 🎯 Filtros")
    st.markdown("---")

    selected_months = st.multiselect(
        "📅 Mês",
        options=sorted(df["Mês"].unique()),
        default=sorted(df["Mês"].unique()),
        format_func=lambda x: MES_ORDER[x-1],
    )

    all_kams = sorted(df["KAM"].unique())
    selected_kams = st.multiselect(
        "👤 KAM",
        options=all_kams,
        default=all_kams,
    )

    all_status = sorted(df["Status_financeiro"].unique())
    selected_status = st.multiselect(
        "💳 Status Financeiro",
        options=all_status,
        default=all_status,
    )

    min_val, max_val = 0, int(df["Total"].max())
    valor_range = st.slider(
        "💰 Valor da Venda (R$)",
        min_value=0,
        max_value=max_val,
        value=(0, max_val),
        step=1000,
        format="R$ %d",
    )

    all_prods = sorted(df["Produto_grupo"].unique())
    selected_prods = st.multiselect(
        "📦 Grupo de Produto",
        options=all_prods,
        default=all_prods,
    )

    st.markdown("---")
    st.markdown("""
    <div style='color:#94A3B8;font-size:0.75rem'>
    📊 <b style='color:white'>StartSe</b> · FP&A / RevOps<br>
    Dados: vendas KAM 2026
    </div>
    """, unsafe_allow_html=True)


# ── Apply filters ──────────────────────────────────────────────────────────────
mask = (
    df["Mês"].isin(selected_months) &
    df["KAM"].isin(selected_kams) &
    df["Status_financeiro"].isin(selected_status) &
    df["Total"].between(valor_range[0], valor_range[1]) &
    df["Produto_grupo"].isin(selected_prods)
)
dff = df[mask].copy()


# ══════════════════════════════════════════════════════════════════════════════
# HERO HEADER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero">
  <h1>📊 KAM Sales Analytics · 2026</h1>
  <p>Painel de performance do time B2B · FP&A | RevOps | Diretoria</p>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# KPI CARDS
# ══════════════════════════════════════════════════════════════════════════════
def fmt_brl(v):
    if v >= 1_000_000:
        return f"R$ {v/1_000_000:.1f}M"
    if v >= 1_000:
        return f"R$ {v/1_000:.0f}K"
    return f"R$ {v:.0f}"

total_vendas = dff["Total"].sum()
total_qtd    = int(dff["Quantidade"].sum())
n_transacoes = len(dff)
pago_pct     = (dff["Status_financeiro"] == "Pago").mean() * 100
atraso_pct   = (dff["Status_financeiro"] == "Em Atraso").mean() * 100
ticket_medio = dff[dff["Total"] > 0]["Total"].mean() if (dff["Total"] > 0).any() else 0

c1, c2, c3, c4, c5, c6 = st.columns(6)
kpis = [
    (c1, "💰 Volume Total", fmt_brl(total_vendas), f"{n_transacoes:,} transações", "#0F2B5B"),
    (c2, "📦 Qtd Vendida", f"{total_qtd:,}", "unidades", "#2D6BE4"),
    (c3, "🎯 Ticket Médio", fmt_brl(ticket_medio), "por transação (>0)", "#9B59B6"),
    (c4, "✅ Taxa Pago", f"{pago_pct:.1f}%", "das transações", "#1DB954"),
    (c5, "⚠️ Em Atraso", f"{atraso_pct:.1f}%", "das transações", "#E8512A"),
    (c6, "👥 KAMs Ativos", str(len(selected_kams)), "no filtro atual", "#F5A623"),
]
for col, label, value, sub, color in kpis:
    with col:
        st.markdown(f"""
        <div class="kpi-card" style="border-left-color:{color}">
          <div class="kpi-label">{label}</div>
          <div class="kpi-value" style="color:{color}">{value}</div>
          <div class="kpi-sub">{sub}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB NAVIGATION
# ══════════════════════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📅 Volume por Mês",
    "👤 Performance KAM",
    "💳 Qualidade da Carteira",
    "📦 Produtos",
    "🎯 Meta vs Realizado",
])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 – Volume por Mês
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown('<div class="section-title">Volume de Vendas por Mês</div>', unsafe_allow_html=True)

    # Aggregation by month
    monthly = (
        dff.groupby("Mês")
        .agg(Valor=("Total", "sum"), Quantidade=("Quantidade", "sum"), Transacoes=("Guid", "count"))
        .reset_index()
    )
    monthly["Mês_nome"] = monthly["Mês"].map({i+1: m for i, m in enumerate(MES_ORDER)})
    monthly = monthly.sort_values("Mês")

    col_a, col_b = st.columns(2)

    with col_a:
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=monthly["Mês_nome"], y=monthly["Valor"],
            marker_color=COLORS["primary"],
            text=[fmt_brl(v) for v in monthly["Valor"]],
            textposition="outside", textfont_size=11,
            name="Valor Total",
        ))
        fig.update_layout(
            title="Valor Total por Mês (R$)",
            xaxis_title="", yaxis_title="",
            plot_bgcolor="white", paper_bgcolor="white",
            showlegend=False, height=380,
            yaxis=dict(showgrid=True, gridcolor="#F0F0F0"),
            font=dict(family="Inter"),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            x=monthly["Mês_nome"], y=monthly["Transacoes"],
            marker_color=COLORS["accent"],
            text=monthly["Transacoes"],
            textposition="outside", textfont_size=11,
            name="Transações",
        ))
        fig2.add_trace(go.Scatter(
            x=monthly["Mês_nome"], y=monthly["Quantidade"],
            mode="lines+markers",
            line=dict(color=COLORS["blue"], width=2),
            marker=dict(size=7),
            name="Qtd Itens",
            yaxis="y2",
        ))
        fig2.update_layout(
            title="Transações e Quantidade por Mês",
            xaxis_title="", yaxis_title="Transações",
            yaxis2=dict(title="Qtd Itens", overlaying="y", side="right"),
            plot_bgcolor="white", paper_bgcolor="white",
            legend=dict(orientation="h", y=-0.15),
            height=380,
            font=dict(family="Inter"),
        )
        st.plotly_chart(fig2, use_container_width=True)

    # Stacked by KAM per month
    st.markdown('<div class="section-title">Volume por KAM ao Longo dos Meses</div>', unsafe_allow_html=True)

    pivot = (
        dff.groupby(["Mês", "KAM"])["Total"]
        .sum().reset_index()
        .pivot(index="Mês", columns="KAM", values="Total")
        .fillna(0)
        .reindex(index=sorted(dff["Mês"].unique()))
    )
    pivot.index = pivot.index.map({i+1: m for i, m in enumerate(MES_ORDER)})

    fig3 = go.Figure()
    for i, kam in enumerate(pivot.columns):
        fig3.add_trace(go.Bar(
            name=kam,
            x=pivot.index.tolist(),
            y=pivot[kam].values,
            marker_color=KAM_COLORS[i % len(KAM_COLORS)],
        ))
    fig3.update_layout(
        barmode="stack",
        xaxis_title="", yaxis_title="Valor (R$)",
        plot_bgcolor="white", paper_bgcolor="white",
        legend=dict(orientation="h", y=-0.25, font_size=11),
        height=420,
        font=dict(family="Inter"),
    )
    st.plotly_chart(fig3, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 – Performance KAM
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-title">Ranking de KAMs · Valor Total e Transações</div>', unsafe_allow_html=True)

    kam_agg = (
        dff.groupby("KAM")
        .agg(
            Valor=("Total", "sum"),
            Transacoes=("Guid", "count"),
            Qtd=("Quantidade", "sum"),
            Pago=("Pago_flag", "mean"),
            Atraso=("Atraso_flag", "mean"),
            Ticket=("Total", lambda x: x[x > 0].mean()),
        )
        .reset_index()
        .sort_values("Valor", ascending=False)
    )
    kam_agg["Ticket"] = kam_agg["Ticket"].fillna(0)

    col1, col2 = st.columns(2)

    with col1:
        fig = go.Figure(go.Bar(
            x=kam_agg["Valor"],
            y=kam_agg["KAM"],
            orientation="h",
            marker_color=[KAM_COLORS[i % len(KAM_COLORS)] for i in range(len(kam_agg))],
            text=[fmt_brl(v) for v in kam_agg["Valor"]],
            textposition="outside",
        ))
        fig.update_layout(
            title="Volume Total por KAM",
            xaxis_title="", yaxis_title="",
            plot_bgcolor="white", paper_bgcolor="white",
            height=460, showlegend=False,
            yaxis=dict(autorange="reversed"),
            font=dict(family="Inter"),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig2 = go.Figure(go.Bar(
            x=kam_agg["Transacoes"],
            y=kam_agg["KAM"],
            orientation="h",
            marker_color=COLORS["accent"],
            text=kam_agg["Transacoes"],
            textposition="outside",
        ))
        fig2.update_layout(
            title="Número de Transações por KAM",
            xaxis_title="", yaxis_title="",
            plot_bgcolor="white", paper_bgcolor="white",
            height=460, showlegend=False,
            yaxis=dict(autorange="reversed"),
            font=dict(family="Inter"),
        )
        st.plotly_chart(fig2, use_container_width=True)

    # Scatter: Valor x Taxa de Pagamento
    st.markdown('<div class="section-title">Eficiência: Volume Vendido vs. Taxa de Pagamento</div>', unsafe_allow_html=True)

    kam_agg["Pago_pct"]  = kam_agg["Pago"]  * 100
    kam_agg["Atraso_pct"] = kam_agg["Atraso"] * 100

    fig_sc = px.scatter(
        kam_agg,
        x="Valor", y="Pago_pct",
        size="Transacoes", color="KAM",
        color_discrete_sequence=KAM_COLORS,
        text="KAM",
        hover_data={"Valor": ":,.0f", "Pago_pct": ":.1f", "Ticket": ":.0f"},
        labels={"Valor": "Volume Total (R$)", "Pago_pct": "Taxa Pago (%)"},
        title="Volume Total vs. Taxa de Pagamento por KAM (tamanho = nº transações)",
    )
    fig_sc.update_traces(textposition="top center", textfont_size=10)
    fig_sc.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        height=480, showlegend=False,
        font=dict(family="Inter"),
        xaxis=dict(showgrid=True, gridcolor="#F0F0F0"),
        yaxis=dict(showgrid=True, gridcolor="#F0F0F0"),
    )
    fig_sc.add_hline(y=kam_agg["Pago_pct"].mean(), line_dash="dash",
                     line_color="gray", annotation_text="Média Pago%")
    st.plotly_chart(fig_sc, use_container_width=True)

    # Detailed table
    st.markdown('<div class="section-title">Tabela Detalhada por KAM</div>', unsafe_allow_html=True)
    table = kam_agg.copy()
    table["Valor_fmt"]  = table["Valor"].apply(fmt_brl)
    table["Ticket_fmt"] = table["Ticket"].apply(fmt_brl)
    table["Pago_%"]     = table["Pago_pct"].map("{:.1f}%".format)
    table["Atraso_%"]   = table["Atraso_pct"].map("{:.1f}%".format)
    st.dataframe(
        table[["KAM","Valor_fmt","Transacoes","Qtd","Ticket_fmt","Pago_%","Atraso_%"]]
        .rename(columns={
            "KAM": "KAM", "Valor_fmt": "Volume Total",
            "Transacoes": "Transações", "Qtd": "Qtd Itens",
            "Ticket_fmt": "Ticket Médio", "Pago_%": "% Pago", "Atraso_%": "% Atraso",
        }),
        use_container_width=True, hide_index=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 – Qualidade da Carteira
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-title">Status Financeiro Geral</div>', unsafe_allow_html=True)

    col_pie, col_bar = st.columns([1, 2])

    with col_pie:
        status_cnt = dff["Status_financeiro"].value_counts()
        fig_pie = go.Figure(go.Pie(
            labels=status_cnt.index.tolist(),
            values=status_cnt.values.tolist(),
            marker_colors=[STATUS_COLORS.get(s, "#CCC") for s in status_cnt.index],
            hole=0.45,
            textinfo="label+percent",
        ))
        fig_pie.update_layout(
            title="Distribuição por Status Financeiro",
            height=380, showlegend=False,
            font=dict(family="Inter"),
            paper_bgcolor="white",
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_bar:
        status_kam = (
            dff.groupby(["KAM", "Status_financeiro"])["Total"].sum()
            .reset_index()
        )
        fig_stk = px.bar(
            status_kam, x="KAM", y="Total", color="Status_financeiro",
            color_discrete_map=STATUS_COLORS,
            barmode="stack",
            labels={"Total": "Valor (R$)", "Status_financeiro": "Status"},
            title="Valor por KAM e Status Financeiro",
        )
        fig_stk.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            height=380,
            legend=dict(orientation="h", y=-0.25, font_size=11),
            xaxis=dict(tickangle=-30),
            font=dict(family="Inter"),
        )
        st.plotly_chart(fig_stk, use_container_width=True)

    # KAMs com maior risco (% Atraso e ??)
    st.markdown('<div class="section-title">Risco por KAM · % Em Atraso e Não Identificado</div>', unsafe_allow_html=True)

    risk = dff.groupby("KAM")["Status_financeiro"].apply(
        lambda x: (x.isin(["Em Atraso", "??"])).mean() * 100
    ).reset_index(name="Risco_%")
    risk_val = dff.groupby("KAM").apply(
        lambda x: x[x["Status_financeiro"].isin(["Em Atraso", "??"])]["Total"].sum()
    ).reset_index(name="Valor_Risco")
    risk = risk.merge(risk_val, on="KAM").sort_values("Risco_%", ascending=False)

    fig_risk = go.Figure()
    fig_risk.add_trace(go.Bar(
        name="% Risco",
        x=risk["KAM"], y=risk["Risco_%"],
        marker_color=[
            COLORS["red"] if v > 70 else COLORS["yellow"] if v > 40 else COLORS["green"]
            for v in risk["Risco_%"]
        ],
        text=[f"{v:.0f}%" for v in risk["Risco_%"]],
        textposition="outside",
        yaxis="y",
    ))
    fig_risk.update_layout(
        title="% de Transações em Risco por KAM (Atraso + Não Identificado)",
        xaxis_title="", yaxis_title="% Risco",
        plot_bgcolor="white", paper_bgcolor="white",
        height=380,
        xaxis=dict(tickangle=-30),
        showlegend=False,
        font=dict(family="Inter"),
    )
    st.plotly_chart(fig_risk, use_container_width=True)

    # Month evolution of payment health
    st.markdown('<div class="section-title">Evolução Mensal da Taxa de Pagamento</div>', unsafe_allow_html=True)
    monthly_pay = dff.groupby(["Mês", "Status_financeiro"])["Total"].sum().reset_index()
    monthly_pay["Mês_nome"] = monthly_pay["Mês"].map({i+1: m for i, m in enumerate(MES_ORDER)})
    monthly_pay = monthly_pay.sort_values("Mês")

    fig_pay = px.bar(
        monthly_pay, x="Mês_nome", y="Total", color="Status_financeiro",
        color_discrete_map=STATUS_COLORS,
        barmode="stack",
        labels={"Total": "Valor (R$)", "Status_financeiro": "Status"},
    )
    fig_pay.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        height=380,
        legend=dict(orientation="h", y=-0.25, font_size=11),
        font=dict(family="Inter"),
    )
    st.plotly_chart(fig_pay, use_container_width=True)

    # Insights
    st.markdown('<div class="section-title">🔍 Insights de Risco</div>', unsafe_allow_html=True)

    higher_risk = risk[risk["Risco_%"] > 70]["KAM"].tolist()
    lower_pay   = (
        dff.groupby("KAM")["Pago_flag"].mean()
        .sort_values(ascending=False)
        .head(3).index.tolist()
    )
    pago_total  = (dff["Status_financeiro"] == "Pago").mean() * 100
    atraso_val  = dff[dff["Status_financeiro"] == "Em Atraso"]["Total"].sum()

    c1_, c2_, c3_ = st.columns(3)
    with c1_:
        cls = "warn" if pago_total < 30 else "ok"
        st.markdown(f"""<div class="insight-box {cls}">
        <b>Taxa Geral de Pagamento</b><br>
        {pago_total:.1f}% das transações estão pagas.
        {"⚠️ Abaixo do ideal de 30%." if pago_total < 30 else "✅ Saudável."}
        </div>""", unsafe_allow_html=True)
    with c2_:
        st.markdown(f"""<div class="insight-box warn">
        <b>Valor em Atraso</b><br>
        {fmt_brl(atraso_val)} estão com pagamento em atraso no período selecionado.
        </div>""", unsafe_allow_html=True)
    with c3_:
        best_pay = lower_pay[0] if lower_pay else "-"
        st.markdown(f"""<div class="insight-box ok">
        <b>Melhor taxa de pagamento</b><br>
        {best_pay} lidera em % de transações pagas — modelo a ser replicado.
        </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 – Produtos
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-title">Mix de Produtos Vendidos</div>', unsafe_allow_html=True)

    prod_agg = (
        dff.groupby("Produto_grupo")
        .agg(Valor=("Total","sum"), Qtd=("Quantidade","sum"), Transacoes=("Guid","count"))
        .reset_index().sort_values("Valor", ascending=False)
    )

    col_p1, col_p2 = st.columns(2)

    with col_p1:
        fig_p = px.treemap(
            prod_agg, path=["Produto_grupo"], values="Valor",
            color="Valor", color_continuous_scale="Blues",
            title="Participação por Grupo de Produto (Valor)",
        )
        fig_p.update_layout(height=400, font=dict(family="Inter"))
        st.plotly_chart(fig_p, use_container_width=True)

    with col_p2:
        fig_p2 = go.Figure(go.Bar(
            x=prod_agg["Valor"], y=prod_agg["Produto_grupo"],
            orientation="h",
            marker_color=COLORS["primary"],
            text=[fmt_brl(v) for v in prod_agg["Valor"]],
            textposition="outside",
        ))
        fig_p2.update_layout(
            title="Ranking Valor por Produto",
            plot_bgcolor="white", paper_bgcolor="white",
            height=400, showlegend=False,
            yaxis=dict(autorange="reversed"),
            font=dict(family="Inter"),
        )
        st.plotly_chart(fig_p2, use_container_width=True)

    # Product by KAM heatmap
    st.markdown('<div class="section-title">Heatmap · KAM × Produto (Valor R$)</div>', unsafe_allow_html=True)

    hm_data = (
        dff.groupby(["KAM", "Produto_grupo"])["Total"]
        .sum().reset_index()
        .pivot(index="KAM", columns="Produto_grupo", values="Total")
        .fillna(0)
    )
    fig_hm = px.imshow(
        hm_data, text_auto=".0f",
        color_continuous_scale="Blues",
        aspect="auto",
        title="Valor por KAM e Produto (R$)",
        labels=dict(color="Valor (R$)"),
    )
    fig_hm.update_layout(height=420, font=dict(family="Inter"))
    st.plotly_chart(fig_hm, use_container_width=True)

    # Top 10 produtos individuais por KAM selecionado
    st.markdown('<div class="section-title">Top Produtos por KAM</div>', unsafe_allow_html=True)
    selected_kam_prod = st.selectbox("Selecione um KAM:", sorted(dff["KAM"].unique()))
    top_prods = (
        dff[dff["KAM"] == selected_kam_prod]
        .groupby("Produto")[["Total","Quantidade"]].sum()
        .sort_values("Total", ascending=False)
        .head(15)
        .reset_index()
    )
    top_prods["Total_fmt"] = top_prods["Total"].apply(fmt_brl)
    st.dataframe(
        top_prods.rename(columns={"Produto": "Produto", "Total_fmt": "Valor", "Quantidade": "Qtd"})[
            ["Produto", "Valor", "Qtd"]
        ],
        use_container_width=True, hide_index=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 – Meta vs Realizado
# ══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown('<div class="section-title">Corporate + Consulting · Receita Realizada vs. Meta 2026</div>',
                unsafe_allow_html=True)

    months_avail = [m for m in MES_ORDER if m in real_rec and pd.notna(real_rec.get(m))]
    real_vals = [real_rec.get(m, 0) or 0 for m in months_avail]
    meta_vals = [meta_combined.get(m, 0) or 0 for m in months_avail]

    fig_mv = go.Figure()
    fig_mv.add_trace(go.Bar(
        name="Receita Realizada",
        x=months_avail, y=real_vals,
        marker_color=COLORS["primary"],
        text=[fmt_brl(v) for v in real_vals],
        textposition="outside",
    ))
    fig_mv.add_trace(go.Scatter(
        name="Meta de Receita",
        x=months_avail, y=meta_vals,
        mode="lines+markers",
        line=dict(color=COLORS["accent"], width=2.5, dash="dash"),
        marker=dict(size=8),
    ))
    fig_mv.update_layout(
        title="Receita Reconhecida vs. Meta por Mês (R$)",
        xaxis_title="", yaxis_title="Valor (R$)",
        plot_bgcolor="white", paper_bgcolor="white",
        height=420,
        legend=dict(orientation="h", y=-0.15),
        font=dict(family="Inter"),
        yaxis=dict(showgrid=True, gridcolor="#F0F0F0"),
    )
    st.plotly_chart(fig_mv, use_container_width=True)

    # Atingimento %
    st.markdown('<div class="section-title">% Atingimento da Meta por Mês</div>', unsafe_allow_html=True)
    ating = []
    for m, r, me in zip(months_avail, real_vals, meta_vals):
        if me and me > 0:
            ating.append({"Mês": m, "Atingimento_%": r/me*100, "Realizado": r, "Meta": me})
    if ating:
        df_ating = pd.DataFrame(ating)
        fig_at = go.Figure(go.Bar(
            x=df_ating["Mês"], y=df_ating["Atingimento_%"],
            marker_color=[
                COLORS["green"] if v >= 100 else COLORS["yellow"] if v >= 70 else COLORS["red"]
                for v in df_ating["Atingimento_%"]
            ],
            text=[f"{v:.0f}%" for v in df_ating["Atingimento_%"]],
            textposition="outside",
        ))
        fig_at.add_hline(y=100, line_dash="dash", line_color="gray", annotation_text="100%")
        fig_at.update_layout(
            title="% Atingimento da Meta de Receita",
            xaxis_title="", yaxis_title="% Atingimento",
            plot_bgcolor="white", paper_bgcolor="white",
            height=380, showlegend=False,
            font=dict(family="Inter"),
        )
        st.plotly_chart(fig_at, use_container_width=True)

    # KAM individual meta
    st.markdown('<div class="section-title">Meta Individual de Vendas por KAM (Orçamento 2026)</div>',
                unsafe_allow_html=True)

    if not df_meta.empty:
        kam_meta_months = [c.replace("meta_","") for c in df_meta.columns if c.startswith("meta_")]
        df_meta_long = df_meta.melt(
            id_vars=["KAM_short","Tier","Atuacao"],
            value_vars=[f"meta_{m}" for m in kam_meta_months],
            var_name="mes", value_name="meta_val",
        )
        df_meta_long["mes"] = df_meta_long["mes"].str.replace("meta_","")
        df_meta_long["mes_label"] = df_meta_long["mes"].str.capitalize()

        # Add realizado from dff (map short names)
        def short_match(kam_full):
            for short, full in short_to_full.items():
                if full == kam_full:
                    return short
            return kam_full.split()[0]

        df_meta_long["KAM_short_clean"] = df_meta_long["KAM_short"].apply(
            lambda x: x.strip().rstrip(".")
        )

        fig_meta = px.bar(
            df_meta_long[df_meta_long["meta_val"].notna()],
            x="mes_label", y="meta_val", color="KAM_short",
            barmode="group",
            labels={"meta_val": "Meta (R$ mil)", "mes_label": "", "KAM_short": "KAM"},
            title="Meta Mensal de Vendas por KAM (R$ mil)",
            color_discrete_sequence=KAM_COLORS,
        )
        fig_meta.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            height=420,
            legend=dict(orientation="h", y=-0.25, font_size=10),
            font=dict(family="Inter"),
        )
        st.plotly_chart(fig_meta, use_container_width=True)

        # Meta vs realizado por KAM
        st.markdown('<div class="section-title">Meta Total Anual vs. Realizado (acumulado 2026)</div>',
                    unsafe_allow_html=True)

        # Sum up meta for months present in data
        months_in_data = [MES_ORDER[m-1].lower() for m in sorted(dff["Mês"].unique())]
        df_meta["meta_acum"] = df_meta[[f"meta_{m}" for m in months_in_data
                                         if f"meta_{m}" in df_meta.columns]].sum(axis=1) * 1000

        # Map short name to realizado
        realizado_map = dff.groupby("KAM")["Total"].sum().to_dict()
        def get_realizado(short):
            full = short_to_full.get(short)
            return realizado_map.get(full, 0)

        df_meta["realizado"] = df_meta["KAM_short"].apply(get_realizado)
        df_meta["ating_%"] = (df_meta["realizado"] / df_meta["meta_acum"] * 100).replace(
            [np.inf, -np.inf], np.nan
        ).fillna(0)

        df_comp = df_meta[df_meta["meta_acum"] > 0].copy().sort_values("ating_%", ascending=False)

        fig_comp = go.Figure()
        fig_comp.add_trace(go.Bar(
            name="Meta Acumulada",
            x=df_comp["KAM_short"], y=df_comp["meta_acum"],
            marker_color=COLORS["subtext"],
            opacity=0.6,
        ))
        fig_comp.add_trace(go.Bar(
            name="Realizado",
            x=df_comp["KAM_short"], y=df_comp["realizado"],
            marker_color=[
                COLORS["green"] if v >= 100 else COLORS["yellow"] if v >= 60 else COLORS["red"]
                for v in df_comp["ating_%"]
            ],
            text=[f"{v:.0f}%" for v in df_comp["ating_%"]],
            textposition="outside",
        ))
        fig_comp.update_layout(
            barmode="overlay",
            title="Realizado vs. Meta Acumulada por KAM (meses no filtro)",
            xaxis_title="", yaxis_title="Valor (R$)",
            plot_bgcolor="white", paper_bgcolor="white",
            height=420,
            legend=dict(orientation="h", y=-0.15),
            font=dict(family="Inter"),
        )
        st.plotly_chart(fig_comp, use_container_width=True)

    # Cohort Vendas corporativas
    st.markdown('<div class="section-title">Cohort de Vendas · Corporate vs. Consulting 2026</div>',
                unsafe_allow_html=True)

    if not df_cohort_vendas.empty:
        df_cohort_vendas["mes_num"] = df_cohort_vendas["mes"].map(
            {m: i+1 for i, m in enumerate(MES_ORDER)}
        )
        df_cv_sorted = df_cohort_vendas.sort_values("mes_num")

        fig_cv = px.bar(
            df_cv_sorted, x="mes", y="venda_2026", color="segmento",
            barmode="group",
            color_discrete_map={"Corporate": COLORS["primary"], "Consulting": COLORS["accent"]},
            labels={"venda_2026": "Vendas (R$)", "mes": "", "segmento": "Segmento"},
            title="Vendas B2B 2026 por Segmento (Orçamento Cohort)",
            category_orders={"mes": MES_ORDER},
        )
        fig_cv.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            height=380,
            legend=dict(orientation="h", y=-0.15),
            font=dict(family="Inter"),
        )
        st.plotly_chart(fig_cv, use_container_width=True)

    # Insights box
    st.markdown('<div class="section-title">🔍 Insights Estratégicos</div>', unsafe_allow_html=True)

    total_meta_rec = sum(meta_vals)
    total_real_rec = sum(real_vals)
    gap = total_real_rec - total_meta_rec
    gap_pct = (gap / total_meta_rec * 100) if total_meta_rec > 0 else 0

    i1, i2, i3 = st.columns(3)
    with i1:
        cls = "ok" if gap >= 0 else "warn"
        st.markdown(f"""<div class="insight-box {cls}">
        <b>{'✅ Acima da meta' if gap >= 0 else '⚠️ Abaixo da meta'}</b><br>
        Receita acumulada {'+' if gap >= 0 else ''}{gap_pct:.1f}% vs. meta no período.
        Gap de {fmt_brl(abs(gap))}.
        </div>""", unsafe_allow_html=True)
    with i2:
        best_m = df_ating.loc[df_ating["Atingimento_%"].idxmax()]["Mês"] if ating else "-"
        st.markdown(f"""<div class="insight-box ok">
        <b>📈 Melhor mês</b><br>
        {best_m} foi o mês com maior % de atingimento da meta de receita.
        </div>""", unsafe_allow_html=True)
    with i3:
        worst_m = df_ating.loc[df_ating["Atingimento_%"].idxmin()]["Mês"] if ating else "-"
        st.markdown(f"""<div class="insight-box warn">
        <b>📉 Mês de atenção</b><br>
        {worst_m} teve o menor % de atingimento. Investigar pipeline e causas.
        </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown("""
<div style='text-align:center; color:#9CA3AF; font-size:0.78rem; padding:8px'>
  📊 <b>StartSe · KAM Analytics 2026</b> · Uso interno · FP&A / RevOps / Diretoria
</div>
""", unsafe_allow_html=True)
