import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Dashboard Produksi Spinning 4",
    page_icon="🏭",
    layout="wide"
)

st.title("🏭 Dashboard Kinerja Produksi Spinning 4")
st.write("Analisis visual komparatif indikator kinerja produksi bulanan.")

uploaded_file = st.file_uploader("Pilih file Excel (.xlsx) atau CSV Produksi", type=["csv", "xlsx"])

if uploaded_file is not None:
    try:
        # Membaca data (header berada di baris ke-3 Excel / index 2)
        if uploaded_file.name.endswith('.xlsx'):
            df_raw = pd.read_excel(uploaded_file, header=2)
        else:
            df_raw = pd.read_csv(uploaded_file, skiprows=2)

        df_raw.columns = [str(col).strip() for col in df_raw.columns]
        
        if 'Keterangan' in df_raw.columns:
            df = df_raw.dropna(subset=['Keterangan']).copy()
            month_cols = [col for col in df.columns if col not in ['No.', 'Keterangan'] and not col.startswith('Unnamed')]

            # Bersihkan format angka
            for m_col in month_cols:
                df[m_col] = df[m_col].astype(str).str.replace(',', '').str.strip()
                df[m_col] = pd.to_numeric(df[m_col], errors='coerce')

            st.success("Data berhasil diproses!")
            st.markdown("---")

            # 1. Ringkasan Kartu Utama (KPI)
            latest_month = month_cols[-1]
            st.subheader(f"📌 Ringkasan Indikator Utama ({latest_month})")
            
            col1, col2, col3, col4 = st.columns(4)
            
            def get_val(ket_keyword):
                val = df[df['Keterangan'].str.contains(ket_keyword, case=False, na=False)][latest_month].values
                return val[0] if len(val) > 0 else 0

            with col1:
                st.metric("Total Produksi", f"{get_val('Produksi Total'):,.2f} Bale")
            with col2:
                st.metric("Jumlah SDM Total", f"{int(get_val('SDM Total'))} Orang")
            with col3:
                st.metric("Hari Kerja", f"{int(get_val('Hari Kerja'))} Hari")
            with col4:
                st.metric("Effisiensi Akumulasi", f"{get_val('Effisiensi'):.2f}%")

            st.markdown("---")

            # 2. Fungsi Pembuat Grafik Grouped Bar Chart (Plotly)
            def buat_grafik_plotly(df_sub, judul_grafik):
                if not df_sub.empty:
                    df_melted = df_sub.melt(id_vars=['Keterangan'], value_vars=month_cols, var_name='Bulan', value_name='Nilai')
                    
                    fig = px.bar(
                        df_melted,
                        x='Keterangan',
                        y='Nilai',
                        color='Bulan',
                        barmode='group',
                        text_auto='.2f',
                        title=judul_grafik,
                        labels={'Nilai': 'Nilai/Ukuran', 'Keterangan': 'Indikator Performance'}
                    )
                    fig.update_layout(
                        xaxis_tickangle=-15,
                        legend_title_text='Bulan',
                        height=450,
                        margin=dict(l=20, r=20, t=50, b=100)
                    )
                    st.plotly_chart(fig, use_container_width=True)

            # 3. Tab Per Kategori Satuan
            st.subheader("📊 Grafik Komparasi Berdasarkan Kategori Data")

            tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
                "📦 Total Produksi", 
                "📈 Rerata Produksi & Count", 
                "👥 SDM & Hari Kerja", 
                "⚡ Pemakaian Listrik", 
                "💰 Biaya Upah",
                "📋 Tabel Lengkap"
            ])

            with tab1:
                df_sub = df[df['Keterangan'].str.contains("Produksi Total", case=False, na=False)]
                buat_grafik_plotly(df_sub, "Perbandingan Total Produksi Per Bulan (Bale)")

            with tab2:
                df_sub = df[df['Keterangan'].str.contains("Produksi Rerata|Average Count", case=False, na=False)]
                buat_grafik_plotly(df_sub, "Perbandingan Produksi Rerata Per Hari (Bale) & Average Count (RSF)")

            with tab3:
                df_sub = df[df['Keterangan'].str.contains("Hari Kerja|SDM|Man Per Bale", case=False, na=False)]
                buat_grafik_plotly(df_sub, "Perbandingan Ketenagakerjaan, Hari Kerja & Ratio Man Per Bale")

            with tab4:
                df_sub = df[df['Keterangan'].str.contains("KWH", case=False, na=False)]
                buat_grafik_plotly(df_sub, "Perbandingan Pemakaian Listrik (KWH)")

            with tab5:
                df_sub = df[df['Keterangan'].str.contains("Biaya Upah", case=False, na=False)]
                buat_grafik_plotly(df_sub, "Perbandingan Biaya Upah SDM (Rupiah)")

            with tab6:
                st.write("### Tabel Laporan Kinerja Lengkap")
                st.dataframe(df, use_container_width=True)

        else:
            st.error("Kolom 'Keterangan' tidak ditemukan dalam file. Pastikan struktur tabel sesuai.")

    except Exception as e:
        st.error(f"Gagal memproses file: {e}")
        