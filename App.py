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

        if 'investasi_rp_juta' in df.columns and 'investasi_us_ribu' in df.columns:
            df['total_investasi_usd'] = (df['investasi_rp_juta'] * 1_000_000 / 15_000) + (df['investasi_us_ribu'] * 1_000)

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

    # Filter Provinsi (urut A-Z)
    provinsi_list = sorted(df['provinsi'].dropna().unique())
    selected_provinces = st.sidebar.multiselect(
        "Provinsi",
        provinsi_list,
        default=provinsi_list
    )

    # Filter Kabupaten/Kota (urut A-Z, berdasarkan provinsi terpilih)
    if selected_provinces:
        kab_options = sorted(df[df['provinsi'].isin(selected_provinces)]['kabupaten_kota'].dropna().unique())
    else:
        kab_options = sorted(df['kabupaten_kota'].dropna().unique())

    selected_kab = st.sidebar.multiselect(
        "Kabupaten/Kota",
        kab_options,
        default=kab_options
    )

    # Filter Status Investasi (checkbox tetap)
    st.sidebar.markdown("**Status Penanaman Modal**")
    status_options = {
        'PMA': st.sidebar.checkbox("PMA (Penanaman Modal Asing)", value=True),
        'PMDN': st.sidebar.checkbox("PMDN (Penanaman Modal Dalam Negeri)", value=True)
    }
    selected_status = [k for k, v in status_options.items() if v]

    # Filter Sektor (urut A-Z)
    sektor_list = sorted(df['nama_sektor'].dropna().unique())
    selected_sectors = st.sidebar.multiselect(
        "Sektor Usaha",
        sektor_list,
        default=sektor_list
    )

    # Filter Negara (urut A-Z jika ada kolom)
    if 'negara' in df.columns:
        negara_list = sorted(df['negara'].dropna().unique())
        selected_countries = st.sidebar.multiselect(
            "Negara Asal Investasi",
            negara_list,
            default=negara_list
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
    total_rp = filtered_df['investasi_rp_juta'].sum() * 1_000_000
    total_usd = filtered_df['total_investasi_usd'].sum()
    total_tki = filtered_df['tki'].sum()
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
            <b>Catatan:</b> 
        </div>
        """, unsafe_allow_html=True)

    # Visualisasi
    st.markdown("---")
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📌 Distribusi Proyek", 
        "💰 Nilai Investasi", 
        "🌍 Investasi per Negara",
        "🧭 Komposisi", 
        "📋 Detail Data"
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
            rp_investment = filtered_df.groupby('provinsi', as_index=False)['investasi_rp_juta'].sum()
            rp_investment['investasi_rp_juta'] = rp_investment['investasi_rp_juta'] * 1_000_000
            rp_investment = rp_investment.sort_values('investasi_rp_juta', ascending=False)
            
            fig2a = px.bar(
                rp_investment,
                x='provinsi',
                y='investasi_rp_juta',
                text='investasi_rp_juta',
                labels={'investasi_rp_juta': 'Total Investasi (IDR)', 'provinsi': 'Provinsi'},
                color='investasi_rp_juta',
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
        
        with col2:
            st.markdown("### 💵 Investasi dalam Dolar (USD)")
            usd_investment = filtered_df.groupby('provinsi', as_index=False)['total_investasi_usd'].sum()
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

    with tab3:
        if 'negara' in filtered_df.columns:
            st.markdown("### 🌍 Investasi per Negara Asal")
            
            country_investment = filtered_df.groupby(['provinsi', 'negara'], as_index=False)['total_investasi_usd'].sum()
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
        
        with col2:
            st.markdown("### 🏭 Top 10 Sektor Investasi")
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

    with tab5:
        st.markdown("### 📋 Tabel Data Investasi")
        
        show_cols = st.multiselect(
            "Pilih kolom untuk ditampilkan:",
            options=filtered_df.columns,
            default=['provinsi', 'kabupaten_kota', 'nama_sektor', 'status_penanaman_modal', 
                    'investasi_rp_juta', 'investasi_us_ribu', 'tki']
        )
        
        display_df = filtered_df[show_cols].copy()
        if 'investasi_rp_juta' in show_cols:
            display_df['investasi_rp_juta'] = display_df['investasi_rp_juta'].apply(lambda x: f"Rp {format_number(x)} Juta")
        if 'investasi_us_ribu' in show_cols:
            display_df['investasi_us_ribu'] = display_df['investasi_us_ribu'].apply(lambda x: f"US$ {format_number(x)} Ribu")
        if 'tki' in show_cols:
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
