import streamlit as st
import pandas as pd
import plotly.express as px
import openpyxl
logo_path = os.path.join(os.path.dirname(__file__), "assets", "LOgo.PNG")
# Konfigurasi halaman
st.set_page_config(
    layout="wide",
    page_title="Dashboard Investasi Indonesia",
    page_icon="📊",
    initial_sidebar_state="expanded"
)

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
# Halaman input
def input_page():
    # Membuat 5 kolom dengan kolom tengah lebih lebar untuk logo
    col1, col2, col3, col4, col5, col6, col7,col8,col9 = st.columns([1,1,1,1,1.2,1,1,1,1])
    with col5:
        st.image(logo_path, width=200)
    
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

    # Filter Provinsi
    all_provinces = st.sidebar.checkbox("Semua Provinsi", value=True, key='all_provinces')
    if all_provinces:
        selected_provinces = st.sidebar.multiselect(
            "Provinsi", 
            df['provinsi'].unique(), 
            default=df['provinsi'].unique(),
            disabled=True
        )
    else:
        selected_provinces = st.sidebar.multiselect("Provinsi", df['provinsi'].unique())

    # Filter Kabupaten/Kota
    if selected_provinces:
        kab_options = df[df['provinsi'].isin(selected_provinces)]['kabupaten_kota'].unique()
    else:
        kab_options = df['kabupaten_kota'].unique()

    all_kab = st.sidebar.checkbox("Semua Kabupaten/Kota", value=True, key='all_kab')
    if all_kab:
        selected_kab = st.sidebar.multiselect(
            "Kabupaten/Kota", 
            kab_options, 
            default=kab_options,
            disabled=True
        )
    else:
        selected_kab = st.sidebar.multiselect("Kabupaten/Kota", kab_options)

    # Filter Status Investasi
    st.sidebar.markdown("**Status Penanaman Modal**")
    status_options = {
        'PMA': st.sidebar.checkbox("PMA (Penanaman Modal Asing)", value=True),
        'PMDN': st.sidebar.checkbox("PMDN (Penanaman Modal Dalam Negeri)", value=True)
    }
    selected_status = [k for k, v in status_options.items() if v]

    # Filter Sektor
    all_sectors = st.sidebar.checkbox("Semua Sektor", value=True, key='all_sectors')
    if all_sectors:
        selected_sectors = st.sidebar.multiselect(
            "Sektor Usaha", 
            df['nama_sektor'].unique(), 
            default=df['nama_sektor'].unique(),
            disabled=True
        )
    else:
        selected_sectors = st.sidebar.multiselect("Sektor Usaha", df['nama_sektor'].unique())

    # Filter Negara (jika kolom ada)
    if 'negara' in df.columns:
        all_countries = st.sidebar.checkbox("Semua Negara", value=True, key='all_countries')
        if all_countries:
            selected_countries = st.sidebar.multiselect(
                "Negara Asal Investasi",
                df['negara'].unique(),
                default=df['negara'].unique(),
                disabled=True
            )
        else:
            selected_countries = st.sidebar.multiselect("Negara Asal Investasi", df['negara'].unique())
    else:
        selected_countries = None

    # Filter data
    filter_conditions = [
        (df['provinsi'].isin(selected_provinces)),
        (df['kabupaten_kota'].isin(selected_kab)),
        (df['status_penanaman_modal'].isin(selected_status)),
        (df['nama_sektor'].isin(selected_sectors))
    ]
    
    if selected_countries is not None:
        filter_conditions.append(df['negara'].isin(selected_countries))
    
    filtered_df = df[pd.concat(filter_conditions, axis=1).all(axis=1)]

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
        </style>
    """, unsafe_allow_html=True)

    # Header
    st.markdown("<h1 class='header-style'>📊 Dashboard Investasi Indonesia</h1>", unsafe_allow_html=True)
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
        project_dist = project_dist.sort_values('size', ascending=False)  # Urutkan dari terbesar
        
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
            xaxis={'categoryorder':'total descending'}  # Urutkan dari terbesar
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
            rp_investment = rp_investment.sort_values('investasi_rp_juta', ascending=False)  # Urutkan dari terbesar
            
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
                xaxis={'categoryorder':'total descending'}  # Urutkan dari terbesar
            )
            st.plotly_chart(fig2a, use_container_width=True)
        
        with col2:
            st.markdown("### 💵 Investasi dalam Dolar (USD)")
            usd_investment = filtered_df.groupby('provinsi', as_index=False)['total_investasi_usd'].sum()
            usd_investment = usd_investment.sort_values('total_investasi_usd', ascending=False)  # Urutkan dari terbesar
            
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
                xaxis={'categoryorder':'total descending'}  # Urutkan dari terbesar
            )
            st.plotly_chart(fig2b, use_container_width=True)

    with tab3:
        if 'negara' in filtered_df.columns:
            st.markdown("### 🌍 Investasi per Negara Asal")
            
            # Investasi per negara untuk provinsi terpilih
            country_investment = filtered_df.groupby(['provinsi', 'negara'], as_index=False)['total_investasi_usd'].sum()
            country_investment = country_investment.sort_values('total_investasi_usd', ascending=False)  # Urutkan dari terbesar
            
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
                xaxis={'categoryorder':'total descending'},  # Urutkan dari terbesar
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
            status_dist = status_dist.sort_values('count', ascending=False)  # Urutkan dari terbesar
            
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
            sector_dist = sector_dist.sort_values('count', ascending=False)  # Urutkan dari terbesar
            
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
                yaxis={'categoryorder':'total ascending'}  # Urutkan dari terbesar
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
else:
    analysis_page()

# Footer
st.markdown("---")
st.markdown(f"""
    <div style='text-align: center; color: #666; font-size: 0.9em;'>
        © 2025 - Dashboard Investasi Indonesia | Kementerian Keuangan Aceh
        <br>Data diperbarui: {pd.Timestamp.now().strftime("%d %B %Y")}
    </div>
""", unsafe_allow_html=True)
