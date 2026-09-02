import os
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Dashboard Produksi Spinning 4", page_icon="🏭", layout="wide"
)

st.title("🏭 Dashboard Kinerja Produksi Spinning 4")
st.write("Analisis visual komparatif indikator kinerja produksi bulanan.")

# Tombol upload (opsional)
uploaded_file = st.file_uploader(
    "Pilih file Excel (.xlsx) atau CSV Produksi", type=["csv", "xlsx"]
)

# Prioritas data: Upload File > File Default di GitHub
data_source = None
if uploaded_file is not None:
  data_source = uploaded_file
elif os.path.exists("data_produksi.csv"):
  data_source = "data_produksi.csv"

if data_source is not None:
  try:
    file_name = (
        data_source.name if hasattr(data_source, "name") else data_source
    )
    if file_name.endswith(".xlsx"):
      df_raw = pd.read_excel(data_source, header=2)
    else:
      df_raw = pd.read_csv(data_source, skiprows=2)

    df_raw.columns = [str(col).strip() for col in df_raw.columns]

    if "Keterangan" in df_raw.columns:
      df = df_raw.dropna(subset=["Keterangan"])
      month_cols = [col for col in df.columns if col != "Keterangan"]

      for m_col in month_cols:
        df[m_col] = df[m_col].astype(str).str.replace(",", "")
        df[m_col] = pd.to_numeric(df[m_col], errors="coerce")

      st.success("Data berhasil diproses!")
      st.markdown("---")

      # 1. Ringkasan Kartu Utama (KPI) - Perbandingan 2 Bulan Terakhir
      st.subheader("📌 Ringkasan Indikator Utama")

      if len(month_cols) >= 2:
        m_prev = month_cols[-2]  # Juni 2024
        m_curr = month_cols[-1]  # Juli 2024
        st.caption(f"Perbandingan angka kinerja: **{m_curr}** vs **{m_prev}**")
      else:
        m_prev = None
        m_curr = month_cols[-1]

      col1, col2, col3, col4 = st.columns(4)

      def get_val(ket_keyword, month):
        if not month:
          return 0
        val = df[
            df["Keterangan"].str.contains(ket_keyword, case=False, na=False)
        ][month].values
        return val[0] if len(val) > 0 else 0

      with col1:
        val_curr = get_val("Produksi Total", m_curr)
        val_prev = get_val("Produksi Total", m_prev)
        delta = val_curr - val_prev if m_prev else None
        st.metric(
            "Total Produksi",
            f"{val_curr:,.2f} Bale",
            delta=f"{delta:,.2f} Bale" if delta is not None else None,
        )

      with col2:
        val_curr = get_val("SDM Total", m_curr)
        val_prev = get_val("SDM Total", m_prev)
        delta = val_curr - val_prev if m_prev else None
        st.metric(
            "Jumlah SDM Total",
            f"{int(val_curr)} Orang",
            delta=f"{int(delta)} Orang" if delta is not None else None,
        )

      with col3:
        val_curr = get_val("Hari Kerja", m_curr)
        val_prev = get_val("Hari Kerja", m_prev)
        delta = val_curr - val_prev if m_prev else None
        st.metric(
            "Hari Kerja",
            f"{int(val_curr)} Hari",
            delta=f"{int(delta)} Hari" if delta is not None else None,
        )

      with col4:
        val_curr = get_val("Effisiensi", m_curr)
        val_prev = get_val("Effisiensi", m_prev)
        delta = val_curr - val_prev if m_prev else None
        st.metric(
            "Effisiensi Akumulasi",
            f"{val_curr:.2f}%",
            delta=f"{delta:.2f}%" if delta is not None else None,
        )

      st.markdown("---")

      # 2. Grafik Komparasi Berdasarkan Kategori Data
      st.subheader("📊 Grafik Komparasi Berdasarkan Kategori Data")

      tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
          "📦 Total Produksi",
          "📈 Rerata Produksi & Count",
          "🎥 SDM & Hari Kerja",
          "⚡ Pemakaian Listrik",
          "💰 Biaya Upah",
          "📋 Tabel Lengkap",
      ])

      with tab1:
        df_prod = df[
            df["Keterangan"].str.contains("Produksi", case=False, na=False)
        ]
        df_prod_melted = df_prod.melt(
            id_vars=["Keterangan"],
            value_vars=month_cols,
            var_name="Bulan",
            value_name="Nilai",
        )
        fig_prod = px.bar(
            df_prod_melted,
            x="Keterangan",
            y="Nilai",
            color="Bulan",
            barmode="group",
            text_auto=".2f",
            title="Perbandingan Produksi (Bale & Lbs)",
        )
        st.plotly_chart(fig_prod, use_container_width=True)

      with tab2:
        df_avg = df[
            df["Keterangan"].str.contains(
                "Rerata|Count", case=False, na=False
            )
        ]
        df_avg_melted = df_avg.melt(
            id_vars=["Keterangan"],
            value_vars=month_cols,
            var_name="Bulan",
            value_name="Nilai",
        )
        fig_avg = px.bar(
            df_avg_melted,
            x="Keterangan",
            y="Nilai",
            color="Bulan",
            barmode="group",
            text_auto=".2f",
            title="Rerata Produksi Harian & Ne Count",
        )
        st.plotly_chart(fig_avg, use_container_width=True)

      with tab3:
        df_sdm = df[
            df["Keterangan"].str.contains(
                "SDM|Hari Kerja|Effisiensi", case=False, na=False
            )
        ]
        df_sdm_melted = df_sdm.melt(
            id_vars=["Keterangan"],
            value_vars=month_cols,
            var_name="Bulan",
            value_name="Nilai",
        )
        fig_sdm = px.bar(
            df_sdm_melted,
            x="Keterangan",
            y="Nilai",
            color="Bulan",
            barmode="group",
            text_auto=".2f",
            title="Ketenagakerjaan & Jam Kerja",
        )
        st.plotly_chart(fig_sdm, use_container_width=True)

      with tab4:
        df_elec = df[
            df["Keterangan"].str.contains(
                "kWh|Listrik", case=False, na=False
            )
        ]
        df_elec_melted = df_elec.melt(
            id_vars=["Keterangan"],
            value_vars=month_cols,
            var_name="Bulan",
            value_name="Nilai",
        )
        fig_elec = px.bar(
            df_elec_melted,
            x="Keterangan",
            y="Nilai",
            color="Bulan",
            barmode="group",
            text_auto=".2f",
            title="Konsumsi Pemakaian Listrik (kWh)",
        )
        st.plotly_chart(fig_elec, use_container_width=True)

      with tab5:
        df_upah = df[
            df["Keterangan"].str.contains("Upah", case=False, na=False)
        ]
        df_upah_melted = df_upah.melt(
            id_vars=["Keterangan"],
            value_vars=month_cols,
            var_name="Bulan",
            value_name="Nilai",
        )
        fig_upah = px.bar(
            df_upah_melted,
            x="Keterangan",
            y="Nilai",
            color="Bulan",
            barmode="group",
            text_auto=".2f",
            title="Perbandingan Biaya Upah SDM (Rupiah)",
        )
        st.plotly_chart(fig_upah, use_container_width=True)

      with tab6:
        st.dataframe(df, use_container_width=True)

  except Exception as e:
    st.error(f"Terjadi kesalahan saat memproses data: {e}")
