import streamlit as st
import pandas as pd
import plotly.express as px
import openpyxl
import os

logo_path = os.path.join(os.path.dirname(__file__), "assets", "LOgo.png")

# Konfigurasi halaman
st.set_page_config(
    layout="wide",
    page_title="Dashboard Investasi Indonesia",
    initial_sidebar_state="expanded"
)

# Style
st.markdown("""
    <style>
    .header-style {
        color: #004b8d;
        border-bottom: 2px solid #004b8d;
        padding-bottom: 10px;
    }
    .metric-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    /* Style untuk tabel penjelasan */
    .legend-table {
        font-size: 0.9rem;
        margin-top: 20px;
    }
    .info-box {
        background-color: #f8f9fa;
        border-left: 4px solid #004b8d;
        padding: 15px;
        margin: 20px 0;
        border-radius: 0 5px 5px 0;
    }
    .comparison-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# Format angka
def format_number(value):
    try:
        value = float(value)
        abs_value = abs(value)
        if abs_value >= 1_000_000_000_000_000_000_000_000_000_000:  # 10³³
            return f"{value / 1_000_000_000_000_000_000_000_000_000_000:.2f}D"
        elif abs_value >= 1_000_000_000_000_000_000_000_000_000:  # 10³⁰
            return f"{value / 1_000_000_000_000_000_000_000_000_000:.2f}N"
        elif abs_value >= 1_000_000_000_000_000_000_000_000:  # 10²⁷
            return f"{value / 1_000_000_000_000_000_000_000_000:.2f}O"
        elif abs_value >= 1_000_000_000_000_000_000_000_000:  # 10²⁴
            return f"{value / 1_000_000_000_000_000_000_000_000:.2f}Sp"
        elif abs_value >= 1_000_000_000_000_000_000_000:  # 10²¹
            return f"{value / 1_000_000_000_000_000_000_000:.2f}Sx"
        elif abs_value >= 1_000_000_000_000_000_000:  # 10¹⁸
            return f"{value / 1_000_000_000_000_000_000:.2f}Qt"
        elif abs_value >= 1_000_000_000_000_000:  # 10¹⁵
            return f"{value / 1_000_000_000_000_000:.2f}Qd"
        elif abs_value >= 1_000_000_000_000:  # 10¹² (Triliun)
            return f"{value / 1_000_000_000_000:.2f}T"
        elif abs_value >= 1_000_000_000:  # 10⁹ (Miliar)
            return f"{value / 1_000_000_000:.2f}M"
        elif abs_value >= 1_000_000:  # 10⁶ (Juta)
            return f"{value / 1_000_000:.2f}Jt"
        elif abs_value >= 1_000:  # 10³ (Ribu)
            return f"{value / 1_000:.1f}K"
        else:
            return f"{value:,.0f}"
    except (ValueError, TypeError):
        return "-"

# Load data
@st.cache_data
def load_data(uploaded_file):
    try:
        df = pd.read_excel(uploaded_file)

        def clean_number(x):
            if pd.isna(x) or x in ["", "-"]:
                return 0.0
            if isinstance(x, str):
                x = x.replace('.', '').replace(',', '.')
            try:
                return float(x)
            except:
                return 0.0

        if 'investasi_rp_juta' in df.columns:
            df['investasi_rp_juta'] = df['investasi_rp_juta'].apply(clean_number)
        if 'investasi_us_ribu' in df.columns:
            df['investasi_us_ribu'] = df['investasi_us_ribu'].apply(clean_number)
        if 'tki' in df.columns:
            df['tki'] = pd.to_numeric(df['tki'], errors='coerce').fillna(0)

        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

# Halaman input
def input_page():
    # Membuat 5 kolom dengan kolom tengah lebih lebar untuk logo
    col1, col2, col3, col4, col5, col6, col7, col8, col9 = st.columns([1,1,1,1,1.2,1,1,1,1])
    with col5:
        st.image(logo_path, width=200, use_container_width=True)
    
    st.markdown("<h1 style='text-align: center; color: #004b8d;'>Selamat Datang</h1>", unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Unggah file Excel data investasi", type=["xlsx", "xls"])

    if st.button("Proses Data") and uploaded_file:
        st.session_state['uploaded_file'] = uploaded_file
        st.session_state['page'] = 'analysis'
        st.rerun()

# Fungsi untuk membuat card perbandingan
def create_comparison_card(title, value1, value2, prov1, prov2, unit=""):
    st.markdown(f"""
    <div class='comparison-card'>
        <h3>{title}</h3>
        <div style="display: flex; justify-content: space-between; margin-top: 10px;">
            <div style="text-align: center; width: 48%;">
                <h4>{prov1}</h4>
                <h2 style="color: #004b8d;">{format_number(value1)}{unit}</h2>
            </div>
            <div style="text-align: center; width: 48%;">
                <h4>{prov2}</h4>
                <h2 style="color: #004b8d;">{format_number(value2)}{unit}</h2>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Halaman analisis
def analysis_page():
    if st.button("⬅️ Kembali ke Halaman Input"):
        st.session_state['page'] = 'input'
        st.rerun()

    if 'uploaded_file' not in st.session_state:
        st.warning("Silakan unggah file terlebih dahulu")
        return

    df = load_data(st.session_state['uploaded_file'])

    # Sidebar filter
    st.sidebar.image(logo_path, use_container_width=True)
    st.sidebar.title("🔍 Filter Data")

    # Filter Provinsi dengan opsi Pilih Semua di atas
    st.sidebar.markdown("**Provinsi**")
    provinsi_list = sorted(df['provinsi'].dropna().unique())
    all_provinces = st.sidebar.checkbox("Pilih Semua Provinsi", value=True, key="all_provinces")
    
    if all_provinces:
        selected_provinces = provinsi_list
        st.sidebar.info("Semua provinsi terpilih")
    else:
        selected_provinces = st.sidebar.multiselect(
            "Pilih provinsi:",
            provinsi_list,
            default=provinsi_list,
            label_visibility="collapsed"
        )

    # Filter untuk tab perbandingan
    st.sidebar.markdown("**🔎 Filter Perbandingan**")
    compare_prov1 = st.sidebar.selectbox("Provinsi Pertama", provinsi_list, index=0)
    compare_prov2 = st.sidebar.selectbox("Provinsi Kedua", provinsi_list, index=1 if len(provinsi_list) > 1 else 0)

    # Filter Kabupaten/Kota dengan opsi Pilih Semua di atas
    st.sidebar.markdown("**Kabupaten/Kota**")
    if selected_provinces:
        kab_options = sorted(df[df['provinsi'].isin(selected_provinces)]['kabupaten_kota'].dropna().unique())
    else:
        kab_options = sorted(df['kabupaten_kota'].dropna().unique())
    
    all_kab = st.sidebar.checkbox("Pilih Semua Kabupaten/Kota", value=True, key="all_kab")
    
    if all_kab:
        selected_kab = kab_options
        st.sidebar.info("Semua kabupaten/kota terpilih")
    else:
        selected_kab = st.sidebar.multiselect(
            "Pilih kabupaten/kota:",
            kab_options,
            default=kab_options,
            label_visibility="collapsed"
        )

    # Filter Status Investasi
    st.sidebar.markdown("**Status Penanaman Modal**")
    status_options = {
        'PMA': st.sidebar.checkbox("PMA (Penanaman Modal Asing)", value=True),
        'PMDN': st.sidebar.checkbox("PMDN (Penanaman Modal Dalam Negeri)", value=True)
    }
    selected_status = [k for k, v in status_options.items() if v]

    # Filter Sektor dengan opsi Pilih Semua di atas
    st.sidebar.markdown("**Sektor Usaha**")
    sektor_list = sorted(df['nama_sektor'].dropna().unique())
    all_sectors = st.sidebar.checkbox("Pilih Semua Sektor", value=True, key="all_sectors")
    
    if all_sectors:
        selected_sectors = sektor_list
        st.sidebar.info("Semua sektor terpilih")
    else:
        selected_sectors = st.sidebar.multiselect(
            "Pilih sektor usaha:",
            sektor_list,
            default=sektor_list,
            label_visibility="collapsed"
        )

    # Filter Negara dengan opsi Pilih Semua di atas (jika ada kolom)
    if 'negara' in df.columns:
        st.sidebar.markdown("**Negara Asal Investasi**")
        negara_list = sorted(df['negara'].dropna().unique())
        all_countries = st.sidebar.checkbox("Pilih Semua Negara", value=True, key="all_countries")
        
        if all_countries:
            selected_countries = negara_list
            st.sidebar.info("Semua negara terpilih")
        else:
            selected_countries = st.sidebar.multiselect(
                "Pilih negara:",
                negara_list,
                default=negara_list,
                label_visibility="collapsed"
            )
    else:
        selected_countries = None

    # Filter data dengan kondisi gabungan
    filter_conditions = [
        df['provinsi'].isin(selected_provinces),
        df['kabupaten_kota'].isin(selected_kab),
        df['status_penanaman_modal'].isin(selected_status),
        df['nama_sektor'].isin(selected_sectors)
    ]

    if selected_countries is not None:
        filter_conditions.append(df['negara'].isin(selected_countries))

    filtered_df = df[pd.concat(filter_conditions, axis=1).all(axis=1)]

    # Header
    st.markdown("<h1 class='header-style'>Dashboard Investasi Indonesia</h1>", unsafe_allow_html=True)
    st.markdown("""
        <div style='margin-bottom: 30px;'>
            Dashboard ini menampilkan data realisasi investasi di Indonesia.
            Gunakan filter di sidebar untuk menyesuaikan tampilan data.
        </div>
    """, unsafe_allow_html=True)

    # Metrics
    total_rp = filtered_df['investasi_rp_juta'].sum() * 1_000_000 if 'investasi_rp_juta' in filtered_df.columns else 0
    total_usd = filtered_df['investasi_us_ribu'].sum() * 1_000 if 'investasi_us_ribu' in filtered_df.columns else 0
    total_tki = filtered_df['tki'].sum() if 'tki' in filtered_df.columns else 0
    count_projects = len(filtered_df)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
            <div class='metric-card'>
                <h3>Total Investasi (USD)</h3>
                <h2>US$ {format_number(total_usd)}</h2>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
            <div class='metric-card'>
                <h3>Total Tenaga Kerja</h3>
                <h2>{format_number(total_tki)} orang</h2>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
            <div class='metric-card'>
                <h3>Jumlah Proyek</h3>
                <h2>{format_number(count_projects)} proyek</h2>
            </div>
        """, unsafe_allow_html=True)

    # Penjelasan singkatan angka (dalam expander)
    with st.expander("ℹ️ Penjelasan Singkatan Angka", expanded=False):
        st.markdown("""
        <div class='info-box'>
            Dashboard ini menggunakan singkatan untuk menampilkan angka yang sangat besar. 
            Berikut penjelasan singkatan yang digunakan:
        </div>
        """, unsafe_allow_html=True)
        
        legend_data = [
            {"Simbol": "K", "Nilai": "10³ (Ribu)", "Contoh": "1.500K = 1.500 ribu (1,500,000)", "Nama": "Ribu"},
            {"Simbol": "Jt", "Nilai": "10⁶ (Juta)", "Contoh": "2.75Jt = 2.75 juta (2,750,000)", "Nama": "Juta"},
            {"Simbol": "M", "Nilai": "10⁹ (Miliar)", "Contoh": "3.50M = 3.5 miliar (3,500,000,000)", "Nama": "Miliar"},
            {"Simbol": "T", "Nilai": "10¹² (Triliun)", "Contoh": "4.20T = 4.2 triliun (4,200,000,000,000)", "Nama": "Triliun"},
            {"Simbol": "Qd", "Nilai": "10¹⁵ (Kuadriliun)", "Contoh": "1.50Qd = 1.5 kuadriliun", "Nama": "Kuadriliun"},
            {"Simbol": "Qt", "Nilai": "10¹⁸ (Kuantiliun)", "Contoh": "2.00Qt = 2 kuantiliun", "Nama": "Kuantiliun"},
            {"Simbol": "Sx", "Nilai": "10²¹ (Sekstiliun)", "Contoh": "3.50Sx = 3.5 sekstiliun", "Nama": "Sekstiliun"},
            {"Simbol": "Sp", "Nilai": "10²⁴ (Septiliun)", "Contoh": "1.20Sp = 1.2 septiliun", "Nama": "Septiliun"},
            {"Simbol": "O", "Nilai": "10²⁷ (Oktiliun)", "Contoh": "0.75O = 0.75 oktiliun", "Nama": "Oktiliun"},
            {"Simbol": "N", "Nilai": "10³⁰ (Noniliun)", "Contoh": "1.10N = 1.1 noniliun", "Nama": "Noniliun"},
            {"Simbol": "D", "Nilai": "10³³ (Desiliun)", "Contoh": "0.50D = 0.5 desiliun", "Nama": "Desiliun"}
        ]
        
        st.table(pd.DataFrame(legend_data))
        
        st.markdown("""
        <div style='margin-top: 10px; color: #666; font-size: 0.9em;'> 
        </div>
        """, unsafe_allow_html=True)

    # Visualisasi
    st.markdown("---")
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📌 Distribusi Proyek", 
        "💰 Nilai Investasi", 
        "🌍 Investasi per Negara",
        "🧭 Komposisi", 
        "📋 Detail Data",
        "🆚 Perbandingan Provinsi"
    ])

    with tab1:
        st.markdown("### 📍 Distribusi Proyek Investasi per Provinsi")
        project_dist = filtered_df.groupby('provinsi', as_index=False).size()
        project_dist = project_dist.sort_values('size', ascending=False)
        
        fig1 = px.bar(
            project_dist,
            x='provinsi',
            y='size',
            text='size',
            labels={'size': 'Jumlah Proyek', 'provinsi': 'Provinsi'},
            color='size',
            color_continuous_scale='YlGnBu'
        )
        fig1.update_layout(
            xaxis_title="Provinsi",
            yaxis_title="Jumlah Proyek",
            hovermode="x unified",
            xaxis={'categoryorder':'total descending'}
        )
        fig1.update_traces(
            texttemplate='%{text}',
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>Jumlah Proyek: %{y}'
        )
        st.plotly_chart(fig1, use_container_width=True)

    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 💰 Investasi dalam Rupiah (IDR)")
            if 'investasi_rp_juta' in filtered_df.columns:
                rp_investment = filtered_df.groupby('provinsi', as_index=False)['investasi_rp_juta'].sum()
                rp_investment['total_investasi_rp'] = rp_investment['investasi_rp_juta'] * 1_000_000
                rp_investment = rp_investment.sort_values('total_investasi_rp', ascending=False)
                
                fig2a = px.bar(
                    rp_investment,
                    x='provinsi',
                    y='total_investasi_rp',
                    text='total_investasi_rp',
                    labels={'total_investasi_rp': 'Total Investasi (IDR)', 'provinsi': 'Provinsi'},
                    color='total_investasi_rp',
                    color_continuous_scale='Blues'
                )
                fig2a.update_traces(
                    texttemplate='Rp %{text:.2s}',
                    textposition='outside',
                    hovertemplate='<b>%{x}</b><br>Investasi: Rp %{y:,.0f}'
                )
                fig2a.update_layout(
                    yaxis_tickprefix='Rp ',
                    yaxis_tickformat=',.0f',
                    xaxis={'categoryorder':'total descending'}
                )
                st.plotly_chart(fig2a, use_container_width=True)
            else:
                st.warning("Data investasi dalam Rupiah tidak tersedia")
        
        with col2:
            st.markdown("### 💵 Investasi dalam Dolar (USD)")
            if 'investasi_us_ribu' in filtered_df.columns:
                usd_investment = filtered_df.groupby('provinsi', as_index=False)['investasi_us_ribu'].sum()
                usd_investment['total_investasi_usd'] = usd_investment['investasi_us_ribu'] * 1_000
                usd_investment = usd_investment.sort_values('total_investasi_usd', ascending=False)
                
                fig2b = px.bar(
                    usd_investment,
                    x='provinsi',
                    y='total_investasi_usd',
                    text='total_investasi_usd',
                    labels={'total_investasi_usd': 'Total Investasi (USD)', 'provinsi': 'Provinsi'},
                    color='total_investasi_usd',
                    color_continuous_scale='Greens'
                )
                fig2b.update_traces(
                    texttemplate='US$ %{text:.2s}',
                    textposition='outside',
                    hovertemplate='<b>%{x}</b><br>Investasi: US$ %{y:,.0f}'
                )
                fig2b.update_layout(
                    yaxis_tickprefix='US$ ',
                    yaxis_tickformat=',.0f',
                    xaxis={'categoryorder':'total descending'}
                )
                st.plotly_chart(fig2b, use_container_width=True)
            else:
                st.warning("Data investasi dalam USD tidak tersedia")

    with tab3:
        if 'negara' in filtered_df.columns and 'investasi_us_ribu' in filtered_df.columns:
            st.markdown("### 🌍 Investasi per Negara Asal")
            
            country_investment = filtered_df.groupby(['provinsi', 'negara'], as_index=False)['investasi_us_ribu'].sum()
            country_investment['total_investasi_usd'] = country_investment['investasi_us_ribu'] * 1_000
            country_investment = country_investment.sort_values('total_investasi_usd', ascending=False)
            
            fig3 = px.bar(
                country_investment,
                x='negara',
                y='total_investasi_usd',
                color='provinsi',
                text='total_investasi_usd',
                labels={'total_investasi_usd': 'Total Investasi (USD)', 'negara': 'Negara Asal'},
                barmode='group'
            )
            fig3.update_traces(
                texttemplate='US$ %{text:.2s}',
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>Investasi: US$ %{y:,.0f}<br>Provinsi: %{customdata[0]}'
            )
            fig3.update_layout(
                yaxis_tickprefix='US$ ',
                yaxis_tickformat=',.0f',
                xaxis={'categoryorder':'total descending'},
                height=600
            )
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.warning("Data negara asal investasi tidak tersedia dalam dataset")

    with tab4:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🧭 Komposisi Status Investasi")
            if 'status_penanaman_modal' in filtered_df.columns:
                status_dist = filtered_df['status_penanaman_modal'].value_counts().reset_index()
                status_dist.columns = ['status', 'count']
                status_dist = status_dist.sort_values('count', ascending=False)
                
                fig3a = px.pie(
                    status_dist,
                    names='status',
                    values='count',
                    color='status',
                    color_discrete_sequence=px.colors.qualitative.Pastel,
                    hole=0.4
                )
                fig3a.update_traces(
                    textinfo='percent+label',
                    hovertemplate='<b>%{label}</b><br>Jumlah: %{value} proyek<br>Persentase: %{percent}'
                )
                st.plotly_chart(fig3a, use_container_width=True)
            else:
                st.warning("Data status penanaman modal tidak tersedia")
        
        with col2:
            st.markdown("### 🏭 Top 10 Sektor Investasi")
            if 'nama_sektor' in filtered_df.columns:
                sector_dist = filtered_df['nama_sektor'].value_counts().nlargest(10).reset_index()
                sector_dist.columns = ['sektor', 'count']
                sector_dist = sector_dist.sort_values('count', ascending=False)
                
                fig3b = px.bar(
                    sector_dist,
                    x='count',
                    y='sektor',
                    orientation='h',
                    text='count',
                    labels={'count': 'Jumlah Proyek', 'sektor': 'Sektor Usaha'},
                    color='count',
                    color_continuous_scale='Purples'
                )
                fig3b.update_traces(
                    texttemplate='%{text} proyek',
                    textposition='outside',
                    hovertemplate='<b>%{y}</b><br>Jumlah Proyek: %{x}'
                )
                fig3b.update_layout(
                    yaxis={'categoryorder':'total ascending'}
                )
                st.plotly_chart(fig3b, use_container_width=True)
            else:
                st.warning("Data sektor usaha tidak tersedia")

    with tab5:
        st.markdown("### 📋 Tabel Data Investasi")
        
        available_columns = [col for col in filtered_df.columns if col in filtered_df]
        show_cols = st.multiselect(
            "Pilih kolom untuk ditampilkan:",
            options=available_columns,
            default=['provinsi', 'kabupaten_kota', 'nama_sektor', 'status_penanaman_modal', 
                    'investasi_rp_juta', 'investasi_us_ribu', 'tki'] if all(col in filtered_df.columns for col in ['provinsi', 'kabupaten_kota', 'nama_sektor', 'status_penanaman_modal', 'investasi_rp_juta', 'investasi_us_ribu', 'tki']) else available_columns[:5]
        )
        
        display_df = filtered_df[show_cols].copy()
        if 'investasi_rp_juta' in show_cols and 'investasi_rp_juta' in display_df.columns:
            display_df['investasi_rp_juta'] = display_df['investasi_rp_juta'].apply(lambda x: f"Rp {format_number(x)} Juta")
        if 'investasi_us_ribu' in show_cols and 'investasi_us_ribu' in display_df.columns:
            display_df['investasi_us_ribu'] = display_df['investasi_us_ribu'].apply(lambda x: f"US$ {format_number(x)} Ribu")
        if 'tki' in show_cols and 'tki' in display_df.columns:
            display_df['tki'] = display_df['tki'].apply(lambda x: f"{format_number(x)} orang")
        
        st.dataframe(
            display_df,
            height=500,
            use_container_width=True,
            hide_index=True
        )
        
        csv = filtered_df[show_cols].to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Unduh Data sebagai CSV",
            data=csv,
            file_name="data_investasi_filtered.csv",
            mime="text/csv"
        )

    with tab6:
    st.markdown("## 🆚 Perbandingan Provinsi")
    
    # Gunakan provinsi yang sudah difilter di sidebar
    available_provinces = filtered_df['provinsi'].unique()
    
    if len(available_provinces) < 1:
        st.warning("Tidak ada data provinsi yang tersedia berdasarkan filter saat ini")
    else:
        # Pilih provinsi untuk dibandingkan
        cols = st.columns(2)
        with cols[0]:
            prov1 = st.selectbox("Pilih Provinsi Pertama", available_provinces, index=0)
        with cols[1]:
            default_idx = 1 if len(available_provinces) > 1 else 0
            prov2 = st.selectbox("Pilih Provinsi Kedua", available_provinces, index=default_idx)
        
        # Filter data untuk masing-masing provinsi
        df_prov1 = filtered_df[filtered_df['provinsi'] == prov1]
        df_prov2 = filtered_df[filtered_df['provinsi'] == prov2]
        
        st.markdown(f"### 🔍 Hasil Perbandingan {prov1} vs {prov2}")
        
        # 1. Perbandingan jumlah proyek
        create_comparison_card(
            "Jumlah Proyek", 
            len(df_prov1), 
            len(df_prov2), 
            prov1, 
            prov2, 
            " proyek"
        )
        
        # 2. Perbandingan total investasi USD
        if 'investasi_us_ribu' in filtered_df.columns:
            invest_prov1 = df_prov1['investasi_us_ribu'].sum() * 1000
            invest_prov2 = df_prov2['investasi_us_ribu'].sum() * 1000
            create_comparison_card(
                "Total Investasi (USD)", 
                invest_prov1, 
                invest_prov2, 
                prov1, 
                prov2, 
                " US$"
            )
        
        # 3. Perbandingan per sektor
        st.markdown("### 📊 Perbandingan per Sektor Usaha")
        if 'nama_sektor' in filtered_df.columns:
            # Jumlah proyek per sektor
            sector_count_prov1 = df_prov1['nama_sektor'].value_counts().reset_index()
            sector_count_prov1.columns = ['Sektor', 'Jumlah Proyek']
            sector_count_prov2 = df_prov2['nama_sektor'].value_counts().reset_index()
            sector_count_prov2.columns = ['Sektor', 'Jumlah Proyek']
            
            fig_sector = px.bar(
                pd.concat([
                    sector_count_prov1.assign(Provinsi=prov1),
                    sector_count_prov2.assign(Provinsi=prov2)
                ]),
                x='Sektor',
                y='Jumlah Proyek',
                color='Provinsi',
                barmode='group',
                title=f"Jumlah Proyek per Sektor",
                color_discrete_sequence=['#1f77b4', '#2ca02c']
            )
            st.plotly_chart(fig_sector, use_container_width=True)
            
            # Investasi per sektor (jika data tersedia)
            if 'investasi_us_ribu' in filtered_df.columns:
                sector_invest_prov1 = df_prov1.groupby('nama_sektor')['investasi_us_ribu'].sum().reset_index()
                sector_invest_prov1['Investasi (USD)'] = sector_invest_prov1['investasi_us_ribu'] * 1000
                sector_invest_prov2 = df_prov2.groupby('nama_sektor')['investasi_us_ribu'].sum().reset_index()
                sector_invest_prov2['Investasi (USD)'] = sector_invest_prov2['investasi_us_ribu'] * 1000
                
                fig_invest = px.bar(
                    pd.concat([
                        sector_invest_prov1.assign(Provinsi=prov1),
                        sector_invest_prov2.assign(Provinsi=prov2)
                    ]),
                    x='nama_sektor',
                    y='Investasi (USD)',
                    color='Provinsi',
                    barmode='group',
                    title=f"Investasi per Sektor (USD)",
                    color_discrete_sequence=['#1f77b4', '#2ca02c']
                )
                fig_invest.update_layout(yaxis_tickprefix='US$ ', yaxis_tickformat=',.0f')
                st.plotly_chart(fig_invest, use_container_width=True)
        
        # 4. Perbandingan TKI
        if 'tki' in filtered_df.columns:
            st.markdown("### 👷 Perbandingan Tenaga Kerja")
            # Total TKI
            total_tki_prov1 = df_prov1['tki'].sum()
            total_tki_prov2 = df_prov2['tki'].sum()
            create_comparison_card(
                "Total Tenaga Kerja", 
                total_tki_prov1, 
                total_tki_prov2, 
                prov1, 
                prov2, 
                " orang"
            )
            
            # TKI per sektor
            if 'nama_sektor' in filtered_df.columns:
                tki_sector_prov1 = df_prov1.groupby('nama_sektor')['tki'].sum().reset_index()
                tki_sector_prov2 = df_prov2.groupby('nama_sektor')['tki'].sum().reset_index()
                
                fig_tki = px.bar(
                    pd.concat([
                        tki_sector_prov1.assign(Provinsi=prov1),
                        tki_sector_prov2.assign(Provinsi=prov2)
                    ]),
                    x='nama_sektor',
                    y='tki',
                    color='Provinsi',
                    barmode='group',
                    title="Tenaga Kerja per Sektor",
                    labels={'tki': 'Jumlah Tenaga Kerja', 'nama_sektor': 'Sektor Usaha'},
                    color_discrete_sequence=['#1f77b4', '#2ca02c']
                )
                st.plotly_chart(fig_tki, use_container_width=True)
        
        # 5. Perbandingan PMA vs PMDN
        if 'status_penanaman_modal' in filtered_df.columns:
            st.markdown("### 💼 Perbandingan Jenis Investasi")
            status_counts_prov1 = df_prov1['status_penanaman_modal'].value_counts().reset_index()
            status_counts_prov1.columns = ['Jenis', 'Jumlah Proyek']
            status_counts_prov2 = df_prov2['status_penanaman_modal'].value_counts().reset_index()
            status_counts_prov2.columns = ['Jenis', 'Jumlah Proyek']
            
            fig_status = px.bar(
                pd.concat([
                    status_counts_prov1.assign(Provinsi=prov1),
                    status_counts_prov2.assign(Provinsi=prov2)
                ]),
                x='Jenis',
                y='Jumlah Proyek',
                color='Provinsi',
                barmode='group',
                title="Jumlah Proyek per Jenis Investasi",
                color_discrete_sequence=['#1f77b4', '#2ca02c']
            )
            st.plotly_chart(fig_status, use_container_width=True)
            
            # Jika data investasi tersedia
            if 'investasi_us_ribu' in filtered_df.columns:
                status_invest_prov1 = df_prov1.groupby('status_penanaman_modal')['investasi_us_ribu'].sum().reset_index()
                status_invest_prov1['Investasi (USD)'] = status_invest_prov1['investasi_us_ribu'] * 1000
                status_invest_prov2 = df_prov2.groupby('status_penanaman_modal')['investasi_us_ribu'].sum().reset_index()
                status_invest_prov2['Investasi (USD)'] = status_invest_prov2['investasi_us_ribu'] * 1000
                
                fig_status_invest = px.bar(
                    pd.concat([
                        status_invest_prov1.assign(Provinsi=prov1),
                        status_invest_prov2.assign(Provinsi=prov2)
                    ]),
                    x='status_penanaman_modal',
                    y='Investasi (USD)',
                    color='Provinsi',
                    barmode='group',
                    title="Investasi per Jenis Investasi (USD)",
                    color_discrete_sequence=['#1f77b4', '#2ca02c']
                )
                fig_status_invest.update_layout(yaxis_tickprefix='US$ ', yaxis_tickformat=',.0f')
                st.plotly_chart(fig_status_invest, use_container_width=True)

# Main
if 'page' not in st.session_state:
    st.session_state['page'] = 'input'

if st.session_state['page'] == 'input':
    input_page()
elif st.session_state['page'] == 'analysis':
    analysis_page()

# Footer
st.markdown("---")
st.markdown(f"""
    <div style='text-align: center; color: #666; font-size: 0.9em;'>
        © 2025 - Dashboard Investasi Indonesia | Kementerian Keuangan Aceh
        <br>Data diperbarui: {pd.Timestamp.now().strftime("%d %B %Y")}
    </div>
""", unsafe_allow_html=True)
