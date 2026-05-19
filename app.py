import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import warnings
warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="StartSe · KAM Analytics 2026",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

COLORS = {
    "primary":  "#0F2B5B",
    "accent":   "#E8512A",
    "green":    "#1DB954",
    "yellow":   "#F5A623",
    "red":      "#E8512A",
    "blue":     "#2D6BE4",
    "subtext":  "#6B7280",
}

KAM_COLORS = [
    "#0F2B5B","#2D6BE4","#E8512A","#1DB954","#F5A623",
    "#9B59B6","#1ABC9C","#E74C3C","#F39C12","#3498DB",
    "#2ECC71","#8E44AD","#16A085","#D35400","#2980B9",
]

GROUP_COLORS = {
    "Corporate":             "#0F2B5B",
    "Consulting":            "#E8512A",
    "Internacional":         "#2D6BE4",
    "Tech Academy":          "#1DB954",
    "Eventos/Offline":       "#F5A623",
    "Patrocínios Diversos":  "#9B59B6",
}

STATUS_COLORS = {
    "Pago":          "#1DB954",
    "Adimplente":    "#2D6BE4",
    "Não Iniciado":  "#F5A623",
    "Em Atraso":     "#E8512A",
    "??":            "#9B59B6",
}

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
  .main { background-color: #F7F8FA; }
  .hero {
    background: linear-gradient(135deg, #0F2B5B 0%, #1a3f7a 100%);
    border-radius: 16px; padding: 28px 36px; margin-bottom: 24px; color: white;
  }
  .hero h1 { font-size: 2rem; font-weight: 800; margin: 0; letter-spacing: -0.5px; }
  .hero p  { font-size: 0.95rem; opacity: 0.75; margin: 6px 0 0; }
  .kpi-card {
    background: white; border-radius: 12px; padding: 20px 24px;
    box-shadow: 0 1px 4px rgba(0,0,0,.08); border-left: 4px solid #0F2B5B; height: 100%;
  }
  .kpi-label { font-size: 0.75rem; font-weight: 600; color: #6B7280; text-transform: uppercase; letter-spacing: .5px; }
  .kpi-value { font-size: 2rem; font-weight: 800; color: #0F2B5B; margin: 4px 0 2px; }
  .kpi-sub   { font-size: 0.8rem; color: #6B7280; }
  .section-title {
    font-size: 1.1rem; font-weight: 700; color: #0F2B5B;
    margin: 24px 0 12px; padding-bottom: 8px;
    border-bottom: 2px solid #E8512A; display: inline-block;
  }
  .insight-box {
    background: #EFF6FF; border: 1px solid #BFDBFE; border-radius: 10px;
    padding: 14px 18px; margin-bottom: 10px; font-size: 0.88rem; color: #1E3A5F;
  }
  .insight-box.warn { background: #FFF7ED; border-color: #FED7AA; color: #7C2D12; }
  .insight-box.ok   { background: #F0FDF4; border-color: #BBF7D0; color: #14532D; }
  div[data-testid="stSidebarContent"] { background: #0F2B5B; }
  div[data-testid="stSidebarContent"] label { color: #CBD5E1 !important; }
  div[data-testid="stSidebarContent"] h2,
  div[data-testid="stSidebarContent"] h3 { color: white !important; }
</style>
""", unsafe_allow_html=True)

MES_ORDER  = ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"]
MES_NAMES  = {i+1: m for i, m in enumerate(MES_ORDER)}
ACTIVE_MONTHS = [1, 2, 3, 4]

NAME_MAP = {
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
    "Junior Borneli":                        "Junior Borneli",
    "Luis Fernando Roos Acosta":             "Luis Acosta",
    "B2C":                                   "B2C (KAM)",
}

SHORT_TO_FULL = {
    "Lobel":    "Pedro Lobel",
    "Fernanda": "Fernanda Bittencourt",
    "Kohama":   "André Kohama",
    "Álvaro":   "Álvaro Carnio",
    "Gustavo":  "Gustavo Almeida",
    "Caio P.":  "Caio Paixão",
    "Lígia":    "Lígia Franzini",
    "Felipe V.":"Felipe Vasconcelos",
    "Julia C.": "Julia Camargo",
}

PLOT_BASE = dict(plot_bgcolor="white", paper_bgcolor="white",
                 font=dict(family="Inter"), margin=dict(t=50, b=10))


@st.cache_data
def load_new_base(path):
    df = pd.read_excel(path, sheet_name="Base de Vendas")
    df["Data"] = pd.to_datetime(df["Data"], dayfirst=True, errors="coerce")
    df["Mês"]  = pd.to_numeric(df["Mês"], errors="coerce").fillna(0).astype(int)
    df["Venda Total"] = pd.to_numeric(df["Venda Total"], errors="coerce").fillna(0)
    df["Quantidade"]  = pd.to_numeric(df["Quantidade"],  errors="coerce").fillna(0)
    df["KAM"] = df["Vendedor"].map(NAME_MAP).fillna(df["Vendedor"])
    df["Mês_nome"] = df["Mês"].map(MES_NAMES)
    df = df[df["Mês"].isin(ACTIVE_MONTHS)].copy()
    return df


@st.cache_data
def load_sales_status(path):
    df = pd.read_excel(path, sheet_name="Sheet1")
    df["Data"]  = pd.to_datetime(df["Data"], dayfirst=True, errors="coerce")
    df["Mês"]   = pd.to_numeric(df["Mês"], errors="coerce").fillna(0).astype(int)
    df["Total"] = pd.to_numeric(df["Total"], errors="coerce").fillna(0)
    df["Status_financeiro"] = df["Status_financeiro"].fillna("??")
    df["KAM"]  = df["Vendedor"].map(NAME_MAP).fillna(df["Vendedor"])
    df["Mês_nome"] = df["Mês"].map(MES_NAMES)
    df = df[df["Mês"].isin(ACTIVE_MONTHS)].copy()
    df["Pago_flag"]   = (df["Status_financeiro"] == "Pago").astype(int)
    df["Atraso_flag"] = (df["Status_financeiro"] == "Em Atraso").astype(int)
    return df


@st.cache_data
def load_cohort(path):
    xl = pd.read_excel(path, sheet_name=None)
    months_low = ["jan","fev","mar","abr","mai","jun","jul","ago","set","out","nov","dez"]

    df_raw = xl["Venda x Mês 2026 KAM - Caio"]
    col_map = {df_raw.columns[i+3]: m for i, m in enumerate(months_low)}
    df_raw  = df_raw.rename(columns=col_map)
    df_raw.columns = [str(c).strip() for c in df_raw.columns]
    kam_meta = []
    for _, r in df_raw.iloc[1:12].iterrows():
        nm = str(r.get("KAM","")).strip()
        if not nm or nm == "nan":
            continue
        row = {"KAM_short": nm, "Tier": str(r.get("Unnamed: 0","")).strip(),
               "Total_meta": pd.to_numeric(r.get("Total"), errors="coerce")}
        for m in months_low:
            row[f"meta_{m}"] = pd.to_numeric(r.get(m, 0), errors="coerce")
        kam_meta.append(row)
    df_meta = pd.DataFrame(kam_meta)

    cohort = xl["Cohort venda x receita 2026"]

    def parse_meta(df_c, s, e):
        for i in range(s, e):
            if "Meta receita" in str(df_c.iloc[i].iloc[0]) or "Meta Receita" in str(df_c.iloc[i].iloc[0]):
                return {m: pd.to_numeric(df_c.iloc[i].iloc[4+j], errors="coerce")
                        for j, m in enumerate(MES_ORDER)}
        return {}

    def parse_real(df_c, s, e):
        for i in range(s, e):
            if "TOTAL" in str(df_c.iloc[i].iloc[0]):
                return {m: pd.to_numeric(df_c.iloc[i].iloc[4+j], errors="coerce")
                        for j, m in enumerate(MES_ORDER)}
        return {}

    meta_corp = parse_meta(cohort, 14, 22)
    meta_cons = parse_meta(cohort, 33, 42)
    real_rec  = parse_real(cohort, 50, 60)
    meta_combined = {m: (meta_corp.get(m) or 0) + (meta_cons.get(m) or 0) for m in MES_ORDER}

    def extract_cohort_sales(start_row, label):
        rows = []
        for i in range(start_row, min(start_row+15, len(cohort))):
            row = cohort.iloc[i]
            mes = str(row.iloc[0]).strip()
            if mes in MES_ORDER:
                rows.append({"mes": mes, "venda_2026": pd.to_numeric(row.iloc[2], errors="coerce"),
                             "segmento": label})
        return pd.DataFrame(rows)

    df_cv = pd.concat([extract_cohort_sales(4, "Corporate"),
                       extract_cohort_sales(23, "Consulting")], ignore_index=True)

    return df_meta, df_cv, meta_combined, real_rec


# ── Load ───────────────────────────────────────────────────────────────────────
NEW_BASE_FILE  = "Base_de_vendas_por_KAM_completa.xlsx"
OLD_SALES_FILE = "vendas_por_kam__2026_.xlsx"
COHORT_FILE    = "Analise_cohort_vendas_receita_2026_B2B__2_.xlsx"

try:
    df_new  = load_new_base(NEW_BASE_FILE)
    df_old  = load_sales_status(OLD_SALES_FILE)
    df_meta, df_cohort_vendas, meta_combined, real_rec = load_cohort(COHORT_FILE)
except FileNotFoundError as e:
    st.error(f"Arquivo não encontrado: {e}\n\nColoque os .xlsx na mesma pasta do app.py")
    st.stop()

df_kam = df_new[df_new["Canal"] == "KAM"].copy()

def fmt_brl(v):
    if pd.isna(v): return "R$ 0"
    if v >= 1_000_000: return f"R$ {v/1_000_000:.1f}M"
    if v >= 1_000:     return f"R$ {v/1_000:.0f}K"
    return f"R$ {v:.0f}"

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 🎯 Filtros")
    st.markdown("---")
    st.caption("📅 Período: Jan–Abr 2026 (Mai excluído)")

    all_kams = sorted([k for k in df_kam["KAM"].unique() if k != "B2C (KAM)"])
    selected_kams = st.multiselect("👤 KAM", options=all_kams, default=all_kams)

    selected_months = st.multiselect(
        "📅 Mês", options=ACTIVE_MONTHS, default=ACTIVE_MONTHS,
        format_func=lambda x: MES_NAMES[x])

    all_groups = sorted(df_kam["Group Accountability"].dropna().unique())
    selected_groups = st.multiselect("📦 Categoria", options=all_groups, default=all_groups)

    all_status = sorted(df_old["Status_financeiro"].unique())
    selected_status = st.multiselect("💳 Status Financeiro", options=all_status, default=all_status)

    st.markdown("---")
    st.markdown("""<div style='color:#94A3B8;font-size:0.75rem'>
    📊 <b style='color:white'>StartSe</b> · FP&A / RevOps<br>
    Jan–Abr 2026 · KAM Analytics
    </div>""", unsafe_allow_html=True)

# ── Filtros aplicados ──────────────────────────────────────────────────────────
dff = df_kam[
    df_kam["KAM"].isin(selected_kams) &
    df_kam["Mês"].isin(selected_months) &
    df_kam["Group Accountability"].isin(selected_groups)
].copy()

dff_old = df_old[
    df_old["KAM"].isin(selected_kams) &
    df_old["Mês"].isin(selected_months) &
    df_old["Status_financeiro"].isin(selected_status)
].copy()

months_show       = [MES_NAMES[m] for m in selected_months]
real_rec_f        = {m: real_rec.get(m, 0) or 0 for m in months_show}
meta_comb_f       = {m: meta_combined.get(m, 0) or 0 for m in months_show}

# ══════════════════════════════════════════════════════════════════════════════
# HERO + KPIs
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero">
  <h1>📊 KAM Sales Analytics · 2026</h1>
  <p>Jan–Abr 2026 · Performance do time B2B · FP&A | RevOps | Diretoria</p>
</div>""", unsafe_allow_html=True)

total_valor  = dff["Venda Total"].sum()
total_qtd    = int(dff["Quantidade"].sum())
n_trans      = len(dff)
pago_pct     = (dff_old["Status_financeiro"] == "Pago").mean() * 100 if len(dff_old) else 0
atraso_pct   = (dff_old["Status_financeiro"] == "Em Atraso").mean() * 100 if len(dff_old) else 0
ticket_medio = dff[dff["Venda Total"] > 0]["Venda Total"].mean() if (dff["Venda Total"] > 0).any() else 0

c1,c2,c3,c4,c5,c6 = st.columns(6)
for col, lbl, val, sub, cor in [
    (c1, "💰 Volume Total",   fmt_brl(total_valor),  f"{n_trans:,} transações",  "#0F2B5B"),
    (c2, "📦 Qtd Vendida",    f"{total_qtd:,}",      "unidades",                 "#2D6BE4"),
    (c3, "🎯 Ticket Médio",   fmt_brl(ticket_medio), "por transação (>0)",        "#9B59B6"),
    (c4, "✅ Taxa Pago",       f"{pago_pct:.1f}%",    "das transações",            "#1DB954"),
    (c5, "⚠️ Em Atraso",      f"{atraso_pct:.1f}%",  "das transações",            "#E8512A"),
    (c6, "👥 KAMs Ativos",    str(len(selected_kams)),"no filtro",                "#F5A623"),
]:
    with col:
        st.markdown(f"""<div class="kpi-card" style="border-left-color:{cor}">
          <div class="kpi-label">{lbl}</div>
          <div class="kpi-value" style="color:{cor}">{val}</div>
          <div class="kpi-sub">{sub}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📅 Volume por Mês",
    "👤 Performance KAM",
    "🗂️ Mix de Produtos",
    "💳 Qualidade da Carteira",
    "🎯 Meta vs Realizado",
    "📊 Cohort de Receita",
])

# ────────────────────────────────────────────────────────────────────────────
# TAB 1 – VOLUME POR MÊS
# ────────────────────────────────────────────────────────────────────────────
with tab1:
    st.markdown('<div class="section-title">Volume de Vendas KAM por Mês</div>', unsafe_allow_html=True)

    monthly = (dff.groupby("Mês")
               .agg(Valor=("Venda Total","sum"), Qtd=("Quantidade","sum"), Trans=("Guid","count"))
               .reset_index())
    monthly["Mês_nome"] = monthly["Mês"].map(MES_NAMES)
    monthly = monthly.sort_values("Mês")

    col_a, col_b = st.columns(2)
    with col_a:
        fig = go.Figure(go.Bar(x=monthly["Mês_nome"], y=monthly["Valor"],
            marker_color=COLORS["primary"],
            text=[fmt_brl(v) for v in monthly["Valor"]], textposition="outside"))
        fig.update_layout(title="Valor Total por Mês (R$)", height=360,
                          yaxis=dict(showgrid=True, gridcolor="#F0F0F0"), **PLOT_BASE)
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=monthly["Mês_nome"], y=monthly["Trans"],
            marker_color=COLORS["accent"], text=monthly["Trans"],
            textposition="outside", name="Transações"))
        fig2.add_trace(go.Scatter(x=monthly["Mês_nome"], y=monthly["Qtd"],
            mode="lines+markers", name="Qtd Itens",
            line=dict(color=COLORS["blue"], width=2), yaxis="y2"))
        fig2.update_layout(title="Transações e Quantidade", height=360,
            yaxis=dict(title="Transações"),
            yaxis2=dict(title="Qtd Itens", overlaying="y", side="right"),
            legend=dict(orientation="h", y=-0.2), **PLOT_BASE)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="section-title">Volume por KAM ao Longo dos Meses</div>', unsafe_allow_html=True)
    pivot = (dff.groupby(["Mês","KAM"])["Venda Total"].sum().reset_index()
             .pivot(index="Mês", columns="KAM", values="Venda Total").fillna(0).sort_index())
    pivot.index = pivot.index.map(MES_NAMES)
    fig3 = go.Figure()
    for i, kam in enumerate(pivot.columns):
        fig3.add_trace(go.Bar(name=kam, x=pivot.index.tolist(), y=pivot[kam].values,
                              marker_color=KAM_COLORS[i % len(KAM_COLORS)]))
    fig3.update_layout(barmode="stack", height=420,
                       legend=dict(orientation="h", y=-0.3, font_size=10), **PLOT_BASE)
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown('<div class="section-title">Volume por Categoria de Produto por Mês</div>', unsafe_allow_html=True)
    pivot_grp = (dff.groupby(["Mês","Group Accountability"])["Venda Total"].sum().reset_index()
                 .pivot(index="Mês", columns="Group Accountability", values="Venda Total").fillna(0).sort_index())
    pivot_grp.index = pivot_grp.index.map(MES_NAMES)
    fig4 = go.Figure()
    for grp in pivot_grp.columns:
        fig4.add_trace(go.Bar(name=grp, x=pivot_grp.index.tolist(), y=pivot_grp[grp].values,
                              marker_color=GROUP_COLORS.get(grp, "#999")))
    fig4.update_layout(barmode="stack", height=400,
                       legend=dict(orientation="h", y=-0.2, font_size=10), **PLOT_BASE)
    st.plotly_chart(fig4, use_container_width=True)

# ────────────────────────────────────────────────────────────────────────────
# TAB 2 – PERFORMANCE KAM
# ────────────────────────────────────────────────────────────────────────────
with tab2:
    st.markdown('<div class="section-title">Ranking de KAMs · Valor Total</div>', unsafe_allow_html=True)

    kam_agg = (dff.groupby("KAM")
               .agg(Valor=("Venda Total","sum"), Trans=("Guid","count"), Qtd=("Quantidade","sum"))
               .reset_index().sort_values("Valor", ascending=False))
    status_agg = dff_old.groupby("KAM").agg(
        Pago=("Pago_flag","mean"), Atraso=("Atraso_flag","mean"),
        Ticket=("Total", lambda x: x[x > 0].mean())).reset_index()
    kam_agg = kam_agg.merge(status_agg, on="KAM", how="left")
    for col in ["Pago","Atraso","Ticket"]:
        kam_agg[col] = kam_agg[col].fillna(0)
    kam_agg["Pago_pct"]   = kam_agg["Pago"]   * 100
    kam_agg["Atraso_pct"] = kam_agg["Atraso"] * 100

    col1, col2 = st.columns(2)
    with col1:
        fig = go.Figure(go.Bar(x=kam_agg["Valor"], y=kam_agg["KAM"], orientation="h",
            marker_color=[KAM_COLORS[i % len(KAM_COLORS)] for i in range(len(kam_agg))],
            text=[fmt_brl(v) for v in kam_agg["Valor"]], textposition="outside"))
        fig.update_layout(title="Volume Total por KAM", height=460,
                          yaxis=dict(autorange="reversed"), showlegend=False, **PLOT_BASE)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig2 = go.Figure(go.Bar(x=kam_agg["Trans"], y=kam_agg["KAM"], orientation="h",
            marker_color=COLORS["accent"], text=kam_agg["Trans"], textposition="outside"))
        fig2.update_layout(title="Número de Transações por KAM", height=460,
                           yaxis=dict(autorange="reversed"), showlegend=False, **PLOT_BASE)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="section-title">Eficiência: Volume vs. Taxa de Pagamento</div>', unsafe_allow_html=True)
    fig_sc = px.scatter(kam_agg, x="Valor", y="Pago_pct", size="Trans", color="KAM",
        color_discrete_sequence=KAM_COLORS, text="KAM",
        labels={"Valor":"Volume Total (R$)","Pago_pct":"Taxa Pago (%)","Trans":"Transações"},
        title="Volume Total vs. Taxa de Pagamento (tamanho = nº transações)")
    fig_sc.update_traces(textposition="top center", textfont_size=10)
    fig_sc.update_layout(height=480, showlegend=False,
        xaxis=dict(showgrid=True, gridcolor="#F0F0F0"),
        yaxis=dict(showgrid=True, gridcolor="#F0F0F0"), **PLOT_BASE)
    if len(kam_agg):
        fig_sc.add_hline(y=kam_agg["Pago_pct"].mean(), line_dash="dash",
                         line_color="gray", annotation_text="Média Pago%")
    st.plotly_chart(fig_sc, use_container_width=True)

    st.markdown('<div class="section-title">Tabela Detalhada por KAM</div>', unsafe_allow_html=True)
    tbl = kam_agg.copy()
    tbl["Volume"]   = tbl["Valor"].apply(fmt_brl)
    tbl["Ticket"]   = tbl["Ticket"].apply(fmt_brl)
    tbl["Pago %"]   = tbl["Pago_pct"].map("{:.1f}%".format)
    tbl["Atraso %"] = tbl["Atraso_pct"].map("{:.1f}%".format)
    st.dataframe(tbl[["KAM","Volume","Trans","Qtd","Ticket","Pago %","Atraso %"]]
        .rename(columns={"Trans":"Transações","Qtd":"Qtd Itens","Ticket":"Ticket Médio"}),
        use_container_width=True, hide_index=True)

# ────────────────────────────────────────────────────────────────────────────
# TAB 3 – MIX DE PRODUTOS
# ────────────────────────────────────────────────────────────────────────────
with tab3:
    st.markdown('<div class="section-title">Heatmap KAM × Categoria de Produto</div>', unsafe_allow_html=True)

    hm = (dff.groupby(["KAM","Group Accountability"])["Venda Total"].sum().reset_index()
          .pivot(index="KAM", columns="Group Accountability", values="Venda Total").fillna(0))
    fig_hm = px.imshow(hm, text_auto=".3s", color_continuous_scale="Blues", aspect="auto",
                       title="Valor por KAM e Categoria (R$)", labels=dict(color="Valor (R$)"))
    fig_hm.update_layout(height=420, **PLOT_BASE)
    st.plotly_chart(fig_hm, use_container_width=True)

    st.markdown('<div class="section-title">% do Mix de Receita por KAM</div>', unsafe_allow_html=True)
    mix = dff.groupby(["KAM","Group Accountability"])["Venda Total"].sum().reset_index()
    total_per_kam = mix.groupby("KAM")["Venda Total"].sum()
    mix["Pct"] = mix.apply(lambda r: r["Venda Total"] / total_per_kam[r["KAM"]] * 100
                           if total_per_kam[r["KAM"]] > 0 else 0, axis=1)
    fig_mix = go.Figure()
    for grp in sorted(mix["Group Accountability"].unique()):
        sub = mix[mix["Group Accountability"] == grp].sort_values("KAM")
        fig_mix.add_trace(go.Bar(name=grp, x=sub["KAM"], y=sub["Pct"],
            marker_color=GROUP_COLORS.get(grp, "#999"),
            text=[f"{v:.0f}%" for v in sub["Pct"]],
            textposition="inside", textfont_size=10))
    fig_mix.update_layout(barmode="stack", height=440,
        yaxis=dict(title="% do Mix", range=[0,105]),
        xaxis=dict(tickangle=-25),
        legend=dict(orientation="h", y=-0.25, font_size=11), **PLOT_BASE)
    st.plotly_chart(fig_mix, use_container_width=True)

    st.markdown('<div class="section-title">Detalhamento por Subproduto · Selecione um KAM</div>',
                unsafe_allow_html=True)
    col_sel, col_sun = st.columns([1, 2])
    with col_sel:
        kam_escolhido = st.selectbox("KAM:", sorted(dff["KAM"].unique()), key="sun_kam")
        mes_escolhido = st.multiselect("Mês:", options=[1,2,3,4], default=[1,2,3,4],
                                       format_func=lambda x: MES_NAMES[x], key="sun_mes")
    df_sun = dff[(dff["KAM"]==kam_escolhido) & (dff["Mês"].isin(mes_escolhido)) & (dff["Venda Total"]>0)]
    with col_sun:
        if df_sun.empty:
            st.info("Sem dados para a seleção.")
        else:
            fig_sun = px.sunburst(df_sun, path=["Group Accountability","Subproduto"],
                values="Venda Total", color="Group Accountability",
                color_discrete_map=GROUP_COLORS, title=f"Mix de {kam_escolhido}")
            fig_sun.update_traces(textinfo="label+percent entry")
            fig_sun.update_layout(height=460, **PLOT_BASE)
            st.plotly_chart(fig_sun, use_container_width=True)

    st.markdown('<div class="section-title">Tabela: Vendas por KAM × Subproduto × Mês</div>',
                unsafe_allow_html=True)
    tbl_sub = (dff[dff["Venda Total"]>0]
               .groupby(["KAM","Group Accountability","Subproduto","Mês"])["Venda Total"]
               .sum().reset_index())
    tbl_sub["Mês_nome"] = tbl_sub["Mês"].map(MES_NAMES)
    tbl_sub["Valor"]    = tbl_sub["Venda Total"].apply(fmt_brl)
    tbl_sub = tbl_sub.sort_values(["KAM","Venda Total"], ascending=[True,False])
    filter_tbl = st.selectbox("Filtrar KAM:", ["Todos"] + sorted(dff["KAM"].unique()), key="tbl_kam")
    show_tbl   = tbl_sub if filter_tbl == "Todos" else tbl_sub[tbl_sub["KAM"]==filter_tbl]
    st.dataframe(show_tbl[["KAM","Group Accountability","Subproduto","Mês_nome","Valor"]]
        .rename(columns={"Group Accountability":"Categoria","Mês_nome":"Mês","Valor":"Valor Vendido"}),
        use_container_width=True, hide_index=True, height=380)

    st.markdown('<div class="section-title">Top Subprodutos por Volume Total</div>', unsafe_allow_html=True)
    top_sub = (dff[dff["Venda Total"]>0]
               .groupby(["Subproduto","Group Accountability"])["Venda Total"]
               .sum().reset_index().sort_values("Venda Total", ascending=False).head(15))
    fig_top = go.Figure(go.Bar(x=top_sub["Venda Total"], y=top_sub["Subproduto"], orientation="h",
        marker_color=[GROUP_COLORS.get(g,"#999") for g in top_sub["Group Accountability"]],
        text=[fmt_brl(v) for v in top_sub["Venda Total"]], textposition="outside"))
    fig_top.update_layout(title="Top 15 Subprodutos por Valor", height=460,
                          yaxis=dict(autorange="reversed"), showlegend=False, **PLOT_BASE)
    st.plotly_chart(fig_top, use_container_width=True)

    st.markdown('<div class="section-title">Evolução Mensal por Categoria</div>', unsafe_allow_html=True)
    ev_grp = dff.groupby(["Mês","Group Accountability"])["Venda Total"].sum().reset_index()
    ev_grp["Mês_nome"] = ev_grp["Mês"].map(MES_NAMES)
    fig_ev = px.line(ev_grp.sort_values("Mês"), x="Mês_nome", y="Venda Total",
        color="Group Accountability", color_discrete_map=GROUP_COLORS, markers=True,
        labels={"Venda Total":"Valor (R$)","Mês_nome":"","Group Accountability":"Categoria"})
    fig_ev.update_layout(height=380,
                         legend=dict(orientation="h", y=-0.2, font_size=11), **PLOT_BASE)
    st.plotly_chart(fig_ev, use_container_width=True)

# ────────────────────────────────────────────────────────────────────────────
# TAB 4 – QUALIDADE DA CARTEIRA
# ────────────────────────────────────────────────────────────────────────────
with tab4:
    st.markdown('<div class="section-title">Status Financeiro Geral</div>', unsafe_allow_html=True)

    col_pie, col_bar = st.columns([1, 2])
    with col_pie:
        sc = dff_old["Status_financeiro"].value_counts()
        fig_pie = go.Figure(go.Pie(labels=sc.index.tolist(), values=sc.values.tolist(),
            marker_colors=[STATUS_COLORS.get(s,"#CCC") for s in sc.index],
            hole=0.45, textinfo="label+percent"))
        fig_pie.update_layout(title="Distribuição Status Financeiro", height=380,
                               showlegend=False, **PLOT_BASE)
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_bar:
        sf_kam = dff_old.groupby(["KAM","Status_financeiro"])["Total"].sum().reset_index()
        fig_stk = px.bar(sf_kam, x="KAM", y="Total", color="Status_financeiro",
            color_discrete_map=STATUS_COLORS, barmode="stack",
            labels={"Total":"Valor (R$)","Status_financeiro":"Status"})
        fig_stk.update_layout(title="Valor por KAM e Status", height=380,
            legend=dict(orientation="h", y=-0.25, font_size=11),
            xaxis=dict(tickangle=-30), **PLOT_BASE)
        st.plotly_chart(fig_stk, use_container_width=True)

    st.markdown('<div class="section-title">% Risco por KAM (Atraso + ??)</div>', unsafe_allow_html=True)
    risk = dff_old.groupby("KAM")["Status_financeiro"].apply(
        lambda x: x.isin(["Em Atraso","??"]).mean() * 100).reset_index(name="Risco_%")
    risk_val = dff_old.groupby("KAM").apply(
        lambda x: x[x["Status_financeiro"].isin(["Em Atraso","??"])]["Total"].sum()
    ).reset_index(name="Valor_Risco")
    risk = risk.merge(risk_val, on="KAM").sort_values("Risco_%", ascending=False)
    fig_risk = go.Figure(go.Bar(x=risk["KAM"], y=risk["Risco_%"],
        marker_color=[COLORS["red"] if v>70 else COLORS["yellow"] if v>40 else COLORS["green"]
                      for v in risk["Risco_%"]],
        text=[f"{v:.0f}%" for v in risk["Risco_%"]], textposition="outside"))
    fig_risk.update_layout(title="% Transações em Risco por KAM", height=360,
                           xaxis=dict(tickangle=-30), showlegend=False, **PLOT_BASE)
    st.plotly_chart(fig_risk, use_container_width=True)

    st.markdown('<div class="section-title">Evolução Mensal por Status</div>', unsafe_allow_html=True)
    mp = dff_old.groupby(["Mês","Status_financeiro"])["Total"].sum().reset_index()
    mp["Mês_nome"] = mp["Mês"].map(MES_NAMES)
    mp = mp.sort_values("Mês")
    fig_mp = px.bar(mp, x="Mês_nome", y="Total", color="Status_financeiro",
                    color_discrete_map=STATUS_COLORS, barmode="stack",
                    labels={"Total":"Valor (R$)","Status_financeiro":"Status"})
    fig_mp.update_layout(height=360,
                         legend=dict(orientation="h", y=-0.2, font_size=11), **PLOT_BASE)
    st.plotly_chart(fig_mp, use_container_width=True)

    st.markdown('<div class="section-title">🔍 Insights de Risco</div>', unsafe_allow_html=True)
    pago_geral = (dff_old["Status_financeiro"]=="Pago").mean()*100 if len(dff_old) else 0
    atraso_val = dff_old[dff_old["Status_financeiro"]=="Em Atraso"]["Total"].sum()
    melhor_pago = (dff_old.groupby("KAM")["Pago_flag"].mean().sort_values(ascending=False).index[0]
                   if len(dff_old) else "-")
    ci1, ci2, ci3 = st.columns(3)
    with ci1:
        cls = "ok" if pago_geral >= 30 else "warn"
        st.markdown(f"""<div class="insight-box {cls}"><b>Taxa Geral de Pagamento</b><br>
        {pago_geral:.1f}% das transações pagas.
        {"✅ Saudável." if pago_geral >= 30 else "⚠️ Abaixo do ideal de 30%."}</div>""",
        unsafe_allow_html=True)
    with ci2:
        st.markdown(f"""<div class="insight-box warn"><b>Valor em Atraso</b><br>
        {fmt_brl(atraso_val)} com pagamento em atraso no período.</div>""",
        unsafe_allow_html=True)
    with ci3:
        st.markdown(f"""<div class="insight-box ok"><b>Melhor Taxa de Pagamento</b><br>
        {melhor_pago} lidera em % de transações pagas.</div>""",
        unsafe_allow_html=True)

# ────────────────────────────────────────────────────────────────────────────
# TAB 5 – META VS REALIZADO
# ────────────────────────────────────────────────────────────────────────────
with tab5:
    st.markdown('<div class="section-title">Vendas Realizadas vs. Meta por KAM (Jan–Abr)</div>',
                unsafe_allow_html=True)

    if not df_meta.empty:
        months_low_sel = [MES_NAMES[m].lower() for m in selected_months]
        df_meta["meta_acum"] = df_meta[
            [f"meta_{m}" for m in months_low_sel if f"meta_{m}" in df_meta.columns]
        ].sum(axis=1) * 1000

        real_map = dff.groupby("KAM")["Venda Total"].sum().to_dict()
        df_meta["realizado"] = df_meta["KAM_short"].apply(
            lambda s: real_map.get(SHORT_TO_FULL.get(s, ""), 0))
        df_meta["ating_%"] = (df_meta["realizado"] / df_meta["meta_acum"] * 100).replace(
            [np.inf, -np.inf], np.nan).fillna(0)

        df_comp = df_meta[df_meta["meta_acum"] > 0].sort_values("ating_%", ascending=False)

        fig_comp = go.Figure()
        fig_comp.add_trace(go.Bar(name="Meta Acumulada", x=df_comp["KAM_short"],
            y=df_comp["meta_acum"], marker_color="#CBD5E1", opacity=0.7))
        fig_comp.add_trace(go.Bar(name="Realizado", x=df_comp["KAM_short"],
            y=df_comp["realizado"],
            marker_color=[COLORS["green"] if v>=100 else COLORS["yellow"] if v>=60 else COLORS["red"]
                          for v in df_comp["ating_%"]],
            text=[f"{v:.0f}%" for v in df_comp["ating_%"]], textposition="outside"))
        fig_comp.update_layout(barmode="overlay", height=420,
            legend=dict(orientation="h", y=-0.15), xaxis=dict(tickangle=-20), **PLOT_BASE)
        st.plotly_chart(fig_comp, use_container_width=True)

        st.markdown('<div class="section-title">% Atingimento por KAM</div>', unsafe_allow_html=True)
        fig_at = go.Figure(go.Bar(x=df_comp["KAM_short"], y=df_comp["ating_%"],
            marker_color=[COLORS["green"] if v>=100 else COLORS["yellow"] if v>=60 else COLORS["red"]
                          for v in df_comp["ating_%"]],
            text=[f"{v:.0f}%" for v in df_comp["ating_%"]], textposition="outside"))
        fig_at.add_hline(y=100, line_dash="dash", line_color="gray", annotation_text="100%")
        fig_at.update_layout(title="% Atingimento da Meta de Vendas", height=380,
            yaxis_title="% Atingimento", xaxis=dict(tickangle=-20), showlegend=False, **PLOT_BASE)
        st.plotly_chart(fig_at, use_container_width=True)

        df_tbl2 = df_comp[["KAM_short","Tier","meta_acum","realizado","ating_%"]].copy()
        df_tbl2.columns = ["KAM","Tier","Meta Acum.","Realizado","% Ating."]
        df_tbl2["Meta Acum."] = df_tbl2["Meta Acum."].apply(fmt_brl)
        df_tbl2["Realizado"]  = df_tbl2["Realizado"].apply(fmt_brl)
        df_tbl2["% Ating."]   = df_tbl2["% Ating."].map("{:.1f}%".format)
        st.dataframe(df_tbl2, use_container_width=True, hide_index=True)

# ────────────────────────────────────────────────────────────────────────────
# TAB 6 – COHORT DE RECEITA
# ── 4 séries fixas (visão macro, independente dos filtros da sidebar) ──────
# ────────────────────────────────────────────────────────────────────────────
_MES4 = ["Jan", "Fev", "Mar", "Abr"]
_xl   = pd.read_excel(COHORT_FILE, sheet_name="Cohort venda x receita 2026")

# 1. Vendas META orçadas — TOTAL "Corp+Cons Vendas 2026+Programado" (row 92)
_vendas_meta = [pd.to_numeric(_xl.iloc[92].iloc[4+j], errors="coerce") for j in range(4)]

# 2. Receita reconhecida META — "Meta receita Corp+Cons 2026" (row 94)
_rec_meta = [pd.to_numeric(_xl.iloc[94].iloc[4+j], errors="coerce") for j in range(4)]

# 3. Vendas REAIS KAM — base completa de vendas, canal KAM, Jan-Abr
_kam_all     = df_new[df_new["Canal"] == "KAM"]
_vendas_real = [float(_kam_all[_kam_all["Mês"] == m]["Venda Total"].sum()) for m in [1, 2, 3, 4]]

# 4. Receita reconhecida REAL — base de receita IFRS, BU Corporate+Consulting
@st.cache_data
def _load_rec_real(path):
    df = pd.read_excel(path)
    df["Total"] = pd.to_numeric(df["Total"], errors="coerce").fillna(0)
    return df

try:
    _df_rec  = _load_rec_real("Base_de_receita_ate_abril_2026.xlsx")
    _mes_col = "MÊS IFRS CONTABIL - REPORT"
    _cc       = _df_rec[_df_rec["BU"].isin(["Corporate", "Consulting"])]
    _rec_real = [float(_cc[_cc[_mes_col] == m]["Total"].sum()) for m in [1, 2, 3, 4]]
    _rec_ok   = True
except FileNotFoundError:
    _rec_real = [0.0, 0.0, 0.0, 0.0]
    _rec_ok   = False

with tab6:
    if not _rec_ok:
        st.warning("Arquivo `Base_de_receita_ate_abril_2026.xlsx` não encontrado. Adicione-o ao repositório.")

    st.markdown("""
    <div class="insight-box" style="margin-bottom:16px">
    <b>📖 Legenda das 4 séries:</b><br>
    🔵 <b>Vendas Reais KAM</b> — valor contratado no mês · <i>Base_de_vendas_por_KAM_completa</i><br>
    ⬛ <b>Vendas Meta (Orçamento)</b> — cohort orçado Corp+Cons · <i>Cohort venda x receita 2026</i><br>
    🟢 <b>Receita Reconhecida Real</b> — IFRS contábil Corp+Consulting · <i>Base_de_receita_ate_abril_2026</i><br>
    🔶 <b>Receita Meta</b> — meta de reconhecimento Corp+Cons · <i>Cohort venda x receita 2026</i>
    </div>
    """, unsafe_allow_html=True)

    # ── Gráfico 1: Vendas Reais vs Meta ─────────────────────────────────
    st.markdown('<div class="section-title">Vendas: Realizado vs. Orçamento</div>', unsafe_allow_html=True)

    fig_v = go.Figure()
    fig_v.add_trace(go.Bar(name="Vendas Reais KAM", x=_MES4, y=_vendas_real,
        marker_color="#2D6BE4",
        text=[fmt_brl(v) for v in _vendas_real], textposition="outside", offsetgroup=1))
    fig_v.add_trace(go.Bar(name="Vendas Meta (Orçamento)", x=_MES4, y=_vendas_meta,
        marker_color="#94A3B8",
        text=[fmt_brl(v) for v in _vendas_meta], textposition="outside", offsetgroup=2))
    for mes, real, meta in zip(_MES4, _vendas_real, _vendas_meta):
        if meta and meta > 0:
            pct = real / meta * 100
            fig_v.add_annotation(x=mes, y=max(real, meta) * 1.2,
                text=f"<b>{pct:.0f}%</b>", showarrow=False,
                font=dict(size=12, color=COLORS["green"] if pct>=100 else COLORS["yellow"] if pct>=70 else COLORS["red"]))
    fig_v.update_layout(barmode="group", height=460,
        title="Vendas Reais KAM vs. Meta Orçada — % atingimento no topo",
        legend=dict(orientation="h", y=-0.15, font_size=12),
        yaxis=dict(showgrid=True, gridcolor="#F0F0F0", title="Valor (R$)"), **PLOT_BASE)
    st.plotly_chart(fig_v, use_container_width=True)

    # ── Gráfico 2: Receita Reconhecida Real vs Meta ──────────────────────
    st.markdown('<div class="section-title">Receita Reconhecida (IFRS Corp+Cons): Realizado vs. Meta</div>',
                unsafe_allow_html=True)

    fig_r = go.Figure()
    fig_r.add_trace(go.Bar(name="Receita Reconhecida Real", x=_MES4, y=_rec_real,
        marker_color=COLORS["green"],
        text=[fmt_brl(v) for v in _rec_real], textposition="outside", offsetgroup=1))
    fig_r.add_trace(go.Bar(name="Receita Meta", x=_MES4, y=_rec_meta,
        marker_color="#94A3B8",
        text=[fmt_brl(v) for v in _rec_meta], textposition="outside", offsetgroup=2))
    for mes, real, meta in zip(_MES4, _rec_real, _rec_meta):
        if meta and meta > 0:
            pct = real / meta * 100
            fig_r.add_annotation(x=mes, y=max(real, meta) * 1.2,
                text=f"<b>{pct:.0f}%</b>", showarrow=False,
                font=dict(size=12, color=COLORS["green"] if pct>=100 else COLORS["yellow"] if pct>=70 else COLORS["red"]))
    fig_r.update_layout(barmode="group", height=460,
        title="Receita Reconhecida Real (IFRS) vs. Meta — % atingimento no topo",
        legend=dict(orientation="h", y=-0.15, font_size=12),
        yaxis=dict(showgrid=True, gridcolor="#F0F0F0", title="Valor (R$)"), **PLOT_BASE)
    st.plotly_chart(fig_r, use_container_width=True)

    # ── Gráfico 3: Visão consolidada das 4 séries ────────────────────────
    st.markdown('<div class="section-title">Visão Consolidada · 4 Séries</div>', unsafe_allow_html=True)

    fig_all = go.Figure()
    fig_all.add_trace(go.Scatter(name="Vendas Reais KAM", x=_MES4, y=_vendas_real,
        mode="lines+markers", line=dict(color="#2D6BE4", width=2.5), marker=dict(size=9)))
    fig_all.add_trace(go.Scatter(name="Vendas Meta", x=_MES4, y=_vendas_meta,
        mode="lines+markers", line=dict(color="#2D6BE4", width=2, dash="dot"),
        marker=dict(size=8, symbol="diamond")))
    fig_all.add_trace(go.Scatter(name="Receita Real (IFRS)", x=_MES4, y=_rec_real,
        mode="lines+markers", line=dict(color=COLORS["green"], width=2.5), marker=dict(size=9)))
    fig_all.add_trace(go.Scatter(name="Receita Meta", x=_MES4, y=_rec_meta,
        mode="lines+markers", line=dict(color=COLORS["green"], width=2, dash="dot"),
        marker=dict(size=8, symbol="diamond")))
    fig_all.update_layout(height=420,
        title="Comparativo: Vendas e Receita (Real vs. Meta)",
        legend=dict(orientation="h", y=-0.2, font_size=11),
        yaxis=dict(showgrid=True, gridcolor="#F0F0F0", title="Valor (R$)"), **PLOT_BASE)
    st.plotly_chart(fig_all, use_container_width=True)

    # ── Tabela resumo ────────────────────────────────────────────────────
    st.markdown('<div class="section-title">Tabela Resumo</div>', unsafe_allow_html=True)
    _rows = []
    for mes, vr, vm, rr, rm in zip(_MES4, _vendas_real, _vendas_meta, _rec_real, _rec_meta):
        _rows.append({
            "Mês":                 mes,
            "Vendas Reais KAM":    fmt_brl(vr),
            "Vendas Meta":         fmt_brl(vm),
            "% Ating. Vendas":     f"{vr/vm*100:.0f}%" if vm else "-",
            "Receita Real (IFRS)": fmt_brl(rr),
            "Receita Meta":        fmt_brl(rm),
            "% Ating. Receita":    f"{rr/rm*100:.0f}%" if rm else "-",
        })
    st.dataframe(pd.DataFrame(_rows), use_container_width=True, hide_index=True)

    # ── Insights ─────────────────────────────────────────────────────────
    st.markdown('<div class="section-title">🔍 Insights</div>', unsafe_allow_html=True)
    _gap_v = sum(_vendas_real) - sum(_vendas_meta)
    _gap_r = sum(_rec_real)    - sum(_rec_meta)
    ci1, ci2, ci3 = st.columns(3)
    with ci1:
        cls = "ok" if _gap_v >= 0 else "warn"
        pct = _gap_v / sum(_vendas_meta) * 100 if sum(_vendas_meta) else 0
        st.markdown(f"""<div class="insight-box {cls}">
        <b>{'✅ Vendas acima do orçamento' if _gap_v>=0 else '⚠️ Vendas abaixo do orçamento'}</b><br>
        Jan–Abr acumulado: {'+' if _gap_v>=0 else ''}{pct:.1f}% vs. meta.<br>
        Gap: {fmt_brl(abs(_gap_v))}.
        </div>""", unsafe_allow_html=True)
    with ci2:
        cls = "ok" if _gap_r >= 0 else "warn"
        pct = _gap_r / sum(_rec_meta) * 100 if sum(_rec_meta) else 0
        st.markdown(f"""<div class="insight-box {cls}">
        <b>{'✅ Receita acima da meta' if _gap_r>=0 else '⚠️ Receita abaixo da meta'}</b><br>
        Jan–Abr acumulado: {'+' if _gap_r>=0 else ''}{pct:.1f}% vs. meta.<br>
        Gap: {fmt_brl(abs(_gap_r))}.
        </div>""", unsafe_allow_html=True)
    with ci3:
        _diff = sum(_vendas_real) - sum(_rec_real)
        st.markdown(f"""<div class="insight-box">
        <b>📦 Vendas ainda não reconhecidas</b><br>
        {fmt_brl(_diff)} vendidos pelos KAMs ainda não entraram como receita IFRS.
        Serão reconhecidos nos próximos meses via cohort.
        </div>""", unsafe_allow_html=True)

st.markdown("---")
st.markdown("""<div style='text-align:center;color:#9CA3AF;font-size:0.78rem;padding:8px'>
  📊 <b>StartSe · KAM Analytics 2026</b> · Uso interno · FP&A / RevOps / Diretoria · Jan–Abr 2026
</div>""", unsafe_allow_html=True)
