import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

 
# SETUP HALAMAN STREAMLIT
 
st.set_page_config(page_title="Bike Sharing Dashboard", page_icon="🚲", layout="wide")

# Mengatur tema seaborn untuk semua visualisasi
sns.set_theme(style="whitegrid", context="talk")

 
# LOAD DAN CLEANING DATA
 
@st.cache_data
def load_data():
    # MENGGUNAKAN NAMA FILE YANG TEPAT
    day_df = pd.read_csv("day.csv")
    hour_df = pd.read_csv("hour.csv")

    # Cleaning: Mengubah tipe data tanggal
    day_df['dteday'] = pd.to_datetime(day_df['dteday'])
    hour_df['dteday'] = pd.to_datetime(hour_df['dteday'])

    # Cleaning: Mengubah tipe data kategori
    categorical_cols = ['season', 'yr', 'mnth', 'holiday', 'weekday', 'workingday', 'weathersit']
    for col in categorical_cols:
        day_df[col] = day_df[col].astype('category')
        hour_df[col] = hour_df[col].astype('category')

    # Cleaning: Rename kolom
    rename_mapping = {
        'dteday': 'date', 'yr': 'year', 'mnth': 'month', 
        'weathersit': 'weather_condition', 'cnt': 'total_count'
    }
    day_df.rename(columns=rename_mapping, inplace=True)
    hour_df.rename(columns=rename_mapping, inplace=True)

    return day_df, hour_df

day_df, hour_df = load_data()

 
# SIDEBAR UNTUK INTERAKTIF
 
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2972/2972185.png", width=150)
    st.title("🚲 Bike Sharing")
    st.markdown("Dashboard Analisis Data Sepeda")
    
    # Interaktif: Pilihan menampilkan dataset mentah
    show_data = st.checkbox("Tampilkan Dataset Mentah")
    
    st.markdown("---")
    st.subheader("⚙️ Filter Data")
    
    # Interaktif: Filter Tahun
    selected_year = st.selectbox(
        "Pilih Tahun:",
        options=[0, 1],
        format_func=lambda x: "2011" if x == 0 else "2012",
        index=1
    )
    
    # Interaktif: Filter Musim
    # Menyesuaikan dengan index data (1: Springer/Winter_Notebook, dll)
    season_mapping = {1: 'Musim 1 (Spring/Winter)', 2: 'Musim 2 (Summer)', 3: 'Musim 3 (Fall)', 4: 'Musim 4 (Winter)'}
    selected_season = st.selectbox(
        "Pilih Musim:",
        options=list(season_mapping.keys()),
        format_func=lambda x: season_mapping[x],
        index=0 
    )

    st.markdown("---")
    st.markdown("**Pembuat:** Alma Wulan Saptaningrum")
    st.markdown("**ID Cohort:** cdcc297d6x1782")

 
# FILTERING DATA BERDASARKAN SIDEBAR
 
main_day_df = day_df[(day_df['year'] == selected_year) & (day_df['season'] == selected_season)].copy()
main_hour_df = hour_df[(hour_df['year'] == selected_year) & (hour_df['season'] == selected_season)].copy()

 
# MENAMPILKAN DATA MENTAH (Jika dicentang)
 
if show_data:
    st.header("Raw Data Preview")
    st.write(f"Menampilkan data untuk Tahun **{'2011' if selected_year == 0 else '2012'}** dan Musim **{season_mapping[selected_season]}**")
    
    col_raw1, col_raw2 = st.columns(2)
    
    with col_raw1:
        st.subheader("Dataset Harian")
        st.dataframe(main_day_df.head(), use_container_width=True)
        st.caption(f"Total baris: {main_day_df.shape[0]}")
        
    with col_raw2:
        st.subheader("Dataset Per Jam")
        st.dataframe(main_hour_df.head(), use_container_width=True)
        st.caption(f"Total baris: {main_hour_df.shape[0]}")
    
    st.markdown("---")

 
# HEADER UTAMA
 
st.title("🚲 Bike Sharing Data Dashboard")
st.markdown("Dashboard ini menyajikan hasil analisis data penyewaan sepeda. Warna visualisasi diatur secara otomatis untuk menyoroti nilai tertinggi (Biru) dan terendah (Merah).")

col1, col2 = st.columns(2)

 
# VISUALISASI 1: PENGARUH CUACA
 
with col1:
    st.subheader("1. Pengaruh Cuaca terhadap Penyewaan")
    
    weather_impact = main_day_df.groupby('weather_condition', observed=True)['total_count'].mean().reset_index()
    weather_impact = weather_impact.dropna(subset=['total_count']) 
    weather_impact.rename(columns={'total_count': 'avg_rentals'}, inplace=True)
    
    weather_impact['weather_label'] = weather_impact['weather_condition'].map({
        1: 'Cerah / Berawan', 2: 'Kabut', 3: 'Salju / Hujan Ringan', 4: 'Badai Salju / Hujan Lebat'
    })
    
    # Filter hanya cuaca yang ada di dataset untuk mencegah error bar kosong
    weather_impact = weather_impact[weather_impact['avg_rentals'] > 0]
    
    # Logika Warna Terarah
    max_val = weather_impact['avg_rentals'].max()
    min_val = weather_impact['avg_rentals'].min()
    
    colors1 = []
    for val in weather_impact['avg_rentals']:
        if val == max_val:
            colors1.append("#3498DB") # Biru (Tertinggi)
        elif val == min_val:
            colors1.append("#E74C3C") # Merah (Terendah)
        else:
            colors1.append("#D3D3D3") # Abu-abu

    # Plot
    fig1, ax1 = plt.subplots(figsize=(8, 6))
    sns.barplot(
        x='weather_label', y='avg_rentals', data=weather_impact, 
        palette=colors1, hue='weather_label', legend=False, ax=ax1,
        edgecolor="black"
    )
    
    ax1.set_title(f"Rata-rata Penyewaan Berdasarkan Cuaca\n({season_mapping[selected_season]} {'2011' if selected_year == 0 else '2012'})", fontsize=15, fontweight='bold', pad=15)
    ax1.set_xlabel("Kondisi Cuaca", fontsize=12, fontweight='bold')
    ax1.set_ylabel("Rata-rata Penyewaan (Unit)", fontsize=12, fontweight='bold')
    
    import textwrap
    labels = [textwrap.fill(label.get_text(), 12) for label in ax1.get_xticklabels()]
    ax1.set_xticklabels(labels)
    
    sns.despine()
    st.pyplot(fig1)
    
    with st.expander("💡 Lihat Insight Cuaca"):
        st.write("""
        **Kesimpulan Analisis:**
        Terlihat dengan jelas bahwa **kondisi cuaca sangat memengaruhi tingkat penyewaan sepeda**. Penyewaan mencapai angka tertinggi (rata-rata maksimal) ketika cuaca sedang cerah atau berawan. Sebaliknya, saat kondisi cuaca memburuk seperti turun salju atau hujan ringan, rata-rata penyewaan turun sangat drastis (ditandai dengan warna merah).
        """)

 
# VISUALISASI 2: JAM SIBUK PENGGUNA KASUAL
 
with col2:
    st.subheader("2. Jam Sibuk Casual Users (Akhir Pekan/Libur)")
    
    holiday_df = main_hour_df[main_hour_df['workingday'] == 0]
    peak_hours_casual = holiday_df.groupby('hr', observed=True)['casual'].sum().reset_index()

    # Plot
    fig2, ax2 = plt.subplots(figsize=(8, 6))
    
    sns.lineplot(
        x='hr', y='casual', data=peak_hours_casual, 
        marker='o', markersize=8, linewidth=3, color='#E67E22', ax=ax2
    )
    
    # Area rentang waktu puncak (Peak Hours)
    ax2.axvspan(12, 16, color='#E74C3C', alpha=0.15, label='Peak Hours (12:00-16:00)')
    
    ax2.set_title(f"Tren Penyewaan Casual per Jam\n({season_mapping[selected_season]} {'2011' if selected_year == 0 else '2012'})", fontsize=15, fontweight='bold', pad=15)
    ax2.set_xlabel("Jam (0-23)", fontsize=12, fontweight='bold')
    ax2.set_ylabel("Total Casual Users", fontsize=12, fontweight='bold')
    ax2.set_xticks(range(0, 24, 2))
    ax2.legend(loc='upper left')
    sns.despine()
    st.pyplot(fig2)
    
    # Menambahkan Insight dari Notebook
    with st.expander("💡 Lihat Insight Jam Sibuk"):
        st.write("""
        **Kesimpulan Analisis:**
        Pada hari libur atau akhir pekan, **pengguna kasual (casual users) menunjukkan lonjakan aktivitas penyewaan pada siang hingga sore hari**. Area yang disorot menunjukkan bahwa *peak hours* terjadi secara konsisten antara pukul **12:00 hingga 16:00**.
        """)

st.markdown("---")

 
# VISUALISASI 3: CLUSTERING (DAYPARTING)
 
st.subheader("3. Analisis Lanjutan: Distribusi Penyewaan Berdasarkan Waktu (Dayparting)")

st.info("""
**Keterangan Rentang Waktu:**
- 🌅 **Morning:** 06:00 - 11:00
- ☀️ **Afternoon:** 12:00 - 16:00
- 🌆 **Evening:** 17:00 - 21:00
- 🌙 **Night:** 22:00 - 05:00
""")

def categorize_daypart(hour):
    if 6 <= hour <= 11:
        return 'Morning'
    elif 12 <= hour <= 16:
        return 'Afternoon'
    elif 17 <= hour <= 21:
        return 'Evening'
    else:
        return 'Night'

main_hour_df['daypart'] = main_hour_df['hr'].apply(categorize_daypart)
main_hour_df['daypart'] = pd.Categorical(main_hour_df['daypart'], categories=['Morning', 'Afternoon', 'Evening', 'Night'], ordered=True)

daypart_rentals = main_hour_df.groupby('daypart', observed=True)['total_count'].sum().reset_index()

max_daypart_val = daypart_rentals['total_count'].max()
min_daypart_val = daypart_rentals['total_count'].min()

colors3 = []
for val in daypart_rentals['total_count']:
    if val == max_daypart_val:
        colors3.append("#3498DB") # Biru
    elif val == min_daypart_val:
        colors3.append("#D3D3D3") # Abu-abu
    else:
        colors3.append("#D3D3D3") # Abu-abu

# Plot
fig3, ax3 = plt.subplots(figsize=(10, 5))

sns.barplot(
    x='daypart', y='total_count', data=daypart_rentals, 
    palette=colors3, hue='daypart', legend=False, ax=ax3,
    edgecolor="black"
)

# Menambahkan pemisah ribuan pada sumbu Y
ylabels = ['{:,.0f}'.format(y) for y in ax3.get_yticks()]
ax3.set_yticklabels(ylabels)

ax3.set_title(f"Total Penyewaan Sepeda Berdasarkan Kelompok Waktu\n({season_mapping[selected_season]} {'2011' if selected_year == 0 else '2012'})", fontsize=15, fontweight='bold', pad=15)
ax3.set_xlabel("Kelompok Waktu", fontsize=12, fontweight='bold')
ax3.set_ylabel("Total Penyewaan (Unit)", fontsize=12, fontweight='bold')
sns.despine()
st.pyplot(fig3)

with st.expander("💡 Lihat Insight Pengelompokan Waktu"):
    st.write("""
    **Kesimpulan Analisis:**
    Melalui teknik *clustering* berbasis jam (*dayparting*), kita bisa melihat akumulasi penyewaan sepeda paling masif terjadi pada segmen **Afternoon (Sore) dan Evening (Malam)**. Sementara itu, pada fase **Night (Larut Malam - Dini Hari)**, aktivitas penyewaan berada di titik terendah.
    """)

st.caption("Copyright © Alma Wulan Saptaningrum 2026")
