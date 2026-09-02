import os
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Dashboard Produksi Spinning 4", page_icon="🏭", layout="wide"
)

st.title("🏭 Dashboard Kinerja Produksi Spinning 4")
st.write("Analisis visual komparatif 16 indikator kinerja produksi bulanan.")

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
      df = df_raw.dropna(subset=["Keterangan"]).copy()

      # Filter kolom bulan (membuang 'No.', 'Keterangan', dan Unnamed)
      month_cols = [
          col
          for col in df.columns
          if col not in ["No.", "Keterangan"] and not col.startswith("Unnamed")
      ]

      for m_col in month_cols:
        df[m_col] = df[m_col].astype(str).str.replace(",", "")
        df[m_col] = pd.to_numeric(df[m_col], errors="coerce")

      st.success(
          f"Data berhasil diproses! Total {len(df)} indikator/variabel"
          " terdeteksi."
      )
      st.markdown("---")

      # 1. Ringkasan Kartu Utama (KPI)
      st.subheader("📌 Ringkasan Indikator Utama")

      if len(month_cols) >= 2:
        m_prev = month_cols[-2]
        m_curr = month_cols[-1]
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
          "📈 Rerata & Count",
          "👥 SDM & Hari Kerja",
          "💰 Biaya Upah SDM",
          "⚡ Listrik & Efisiensi",
          "📋 Tabel Lengkap (16 Variabel)",
      ])

      # Fungsi pembuat grafik reusable
      def create_bar_chart(sub_df, title):
        df_melted = sub_df.melt(
            id_vars=["Keterangan"],
            value_vars=month_cols,
            var_name="Bulan",
            value_name="Nilai",
        )
        fig = px.bar(
            df_melted,
            x="Keterangan",
            y="Nilai",
            color="Bulan",
            barmode="group",
            text_auto=".2f",
            title=title,
        )
        st.plotly_chart(fig, use_container_width=True)

      with tab1:
        # Total Produksi (Bale & Lbs)
        df_sub = df[
            df["Keterangan"].str.contains(
                "Produksi Total", case=False, na=False
            )
        ]
        create_bar_chart(df_sub, "Perbandingan Total Produksi (Bale & Lbs)")

      with tab2:
        # Rerata & Count
        df_sub = df[
            df["Keterangan"].str.contains(
                "Rerata|Count", case=False, na=False
            )
        ]
        create_bar_chart(df_sub, "Rerata Produksi Harian & Average Count (RSF)")

      with tab3:
        # Ketenagakerjaan & Jam Kerja
        df_sub = df[
            df["Keterangan"].str.contains(
                "SDM|Hari Kerja|Man Per Bale", case=False, na=False
            )
            & ~df["Keterangan"].str.contains("Upah", case=False, na=False)
        ]
        create_bar_chart(df_sub, "Ketenagakerjaan, Shift & Man Per Bale")

      with tab4:
        st.markdown("#### 💵 Analisis Biaya Upah SDM (Skala Dipisah)")
        # Upah SDM Shift
        df_upah_shift = df[
            df["Keterangan"].str.contains("Upah", case=False, na=False)
            & df["Keterangan"].str.contains("Shift", case=False, na=False)
        ]
        if not df_upah_shift.empty:
          create_bar_chart(df_upah_shift, "Biaya Upah SDM Produksi Shift")

        # Upah SDM Total
        df_upah_total = df[
            df["Keterangan"].str.contains("Upah", case=False, na=False)
            & df["Keterangan"].str.contains("Total", case=False, na=False)
        ]
        if not df_upah_total.empty:
          create_bar_chart(df_upah_total, "Biaya Upah SDM Total")

     with tab5:
        st.markdown("#### ⚡ Analisis Pemakaian Listrik & Efisiensi")

        # 1. Total KWH Listrik (Skala Ratusan Ribu)
        df_kwh_total = df[
            df["Keterangan"].str.contains(
                "Total KWH Pemakaian Listrik", case=False, na=False
            )
        ]
        if not df_kwh_total.empty:
          create_bar_chart(
              df_kwh_total, "1. Total Pemakaian Listrik (KWH Total)"
          )

        # 2. KWH Per Satuan / Ratio (Skala Ratusan & Desimal)
        df_kwh_ratio = df[
            df["Keterangan"].str.contains(
                "KWH Listrik Per", case=False, na=False
            )
        ]
        if not df_kwh_ratio.empty:
          create_bar_chart(
              df_kwh_ratio, "2. Konsumsi Listrik Per Satuan (Per Bale & Per Kg)"
          )

        # 3. Effisiensi Akumulasi (Skala Persentase %)
        df_eff = df[
            df["Keterangan"].str.contains("Effisiensi", case=False, na=False)
        ]
        if not df_eff.empty:
          create_bar_chart(df_eff, "3. Effisiensi Akumulasi (%)")

      with tab6:
        st.markdown(
            "### 📋 Seluruh 16 Variabel Indikator Kinerja Produksi Spinning 4"
        )
        st.dataframe(df, use_container_width=True)

  except Exception as e:
    st.error(f"Terjadi kesalahan saat memproses data: {e}")
