import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# ==========================================
# SETUP HALAMAN STREAMLIT
# ==========================================
st.set_page_config(page_title="Bike Sharing Dashboard", page_icon="🚲", layout="wide")

# Mengatur tema seaborn untuk semua visualisasi
sns.set_theme(style="whitegrid")

# ==========================================
# LOAD DAN CLEANING DATA
# ==========================================
@st.cache_data
def load_data():
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

# ==========================================
# SIDEBAR UNTUK INTERAKTIF
# ==========================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2972/2972185.png", width=150)
    st.title("🚲 Bike Sharing")
    st.markdown("Dashboard Analisis Data Sepeda")
    
    # Interaktif: Pilihan menampilkan dataset mentah
    show_data = st.checkbox("Tampilkan Dataset Mentah")

    st.markdown("---")
    st.markdown("**Pembuat:** Alma Wulan Saptaningrum")
    st.markdown("**ID Cohort:** CDCC297D6X1782")

# ==========================================
# MENAMPILKAN DATA MENTAH (Jika dicentang)
# ==========================================
if show_data:
    st.header("Raw Data Preview")
    
    # Membuat dua kolom agar tampilan data sejajar
    col_raw1, col_raw2 = st.columns(2)
    
    with col_raw1:
        st.subheader("Dataset Harian (day_df)")
        st.dataframe(day_df.head(), use_container_width=True)
        st.caption(f"Total baris: {day_df.shape[0]}")
        
    with col_raw2:
        st.subheader("Dataset Per Jam (hour_df)")
        st.dataframe(hour_df.head(), use_container_width=True)
        st.caption(f"Total baris: {hour_df.shape[0]}")
    
    st.markdown("---")

# ==========================================
# HEADER UTAMA
# ==========================================
st.title("🚲 Bike Sharing Data Dashboard")
st.markdown("Dashboard ini menyajikan hasil analisis data penyewaan sepeda berdasarkan cuaca, jam sibuk, dan kelompok waktu (*daypart*).")

# Membuat dua kolom untuk visualisasi agar rapi
col1, col2 = st.columns(2)

# ==========================================
# VISUALISASI 1: PENGARUH CUACA (Q1)
# ==========================================
with col1:
    st.subheader("1. Pengaruh Cuaca di Musim Dingin (2012)")
    
    # Filter data
    winter_2012_df = day_df[(day_df['season'] == 1) & (day_df['year'] == 1)]
    weather_impact = winter_2012_df.groupby('weather_condition', observed=True)['total_count'].mean().reset_index()
    
    # PERBAIKAN: Ubah nama kolom hasil rata-rata menjadi 'avg_rentals'
    weather_impact.rename(columns={'total_count': 'avg_rentals'}, inplace=True)
    
    # Mapping label
    weather_impact['weather_label'] = weather_impact['weather_condition'].map({
        1: 'Cerah / Berawan', 2: 'Kabut', 3: 'Salju / Hujan Ringan', 4: 'Badai Salju'
    })
    plot_data_q1 = weather_impact[weather_impact['weather_condition'].isin([1, 3, 4])]

    # Plot
    fig1, ax1 = plt.subplots(figsize=(8, 5))
    colors = ["#72BCD4", "#D3D3D3", "#A9A9A9"] 
    sns.barplot(
        x='weather_label', y='avg_rentals', data=plot_data_q1, 
        palette=colors, hue='weather_label', legend=False, ax=ax1
    )
    ax1.set_title("Rata-rata Penyewaan Sepeda Berdasarkan Cuaca", fontsize=12, fontweight='bold')
    ax1.set_xlabel("Kondisi Cuaca")
    ax1.set_ylabel("Rata-rata Penyewaan (Unit)")
    st.pyplot(fig1)
    
    with st.expander("Lihat Insight"):
        st.write("Terjadi penurunan drastis penyewaan sepeda (dari ~3500 unit ke bawah 1500 unit) ketika cuaca berubah dari cerah menjadi bersalju/hujan ringan di musim dingin.")

# ==========================================
# VISUALISASI 2: JAM SIBUK PENGGUNA KASUAL (Q2)
# ==========================================
with col2:
    st.subheader("2. Jam Sibuk Casual Users (Hari Libur 2012)")
    
    # Filter data
    holiday_2012_df = hour_df[(hour_df['workingday'] == 0) & (hour_df['year'] == 1)]
    peak_hours_casual = holiday_2012_df.groupby('hr', observed=True)['casual'].sum().reset_index()

    # Plot
    fig2, ax2 = plt.subplots(figsize=(8, 5))
    sns.lineplot(
        x='hr', y='casual', data=peak_hours_casual, 
        marker='o', linewidth=2.5, color='#FF7F50', ax=ax2
    )
    ax2.axvspan(12, 15, color='red', alpha=0.1, label='Peak Hours (12:00-15:00)')
    ax2.set_title("Tren Penyewaan Casual Users per Jam", fontsize=12, fontweight='bold')
    ax2.set_xlabel("Jam (0-23)")
    ax2.set_ylabel("Total Casual Users")
    ax2.legend()
    st.pyplot(fig2)
    
    with st.expander("Lihat Insight"):
        st.write("Pengguna kasual sangat aktif di siang hari pada akhir pekan, dengan puncak penyewaan terjadi pada rentang waktu 12:00 hingga 15:00.")

st.markdown("---")

# ==========================================
# VISUALISASI 3: CLUSTERING (DAYPARTING)
# ==========================================
st.subheader("3. Analisis Lanjutan: Distribusi Penyewaan Berdasarkan Waktu (Dayparting)")

# Menambahkan keterangan rentang waktu agar informatif
st.info("""
**Keterangan Rentang Waktu:**
- 🌅 **Morning:** 06:00 - 11:00
- ☀️ **Afternoon:** 12:00 - 16:00
- 🌆 **Evening:** 17:00 - 21:00
- 🌙 **Night:** 22:00 - 05:00
""")

# Fungsi Binning
def categorize_daypart(hour):
    if 6 <= hour <= 11:
        return 'Morning'
    elif 12 <= hour <= 16:
        return 'Afternoon'
    elif 17 <= hour <= 21:
        return 'Evening'
    else:
        return 'Night'

hour_df['daypart'] = hour_df['hr'].apply(categorize_daypart)
hour_df['daypart'] = pd.Categorical(hour_df['daypart'], categories=['Morning', 'Afternoon', 'Evening', 'Night'], ordered=True)

# Agregasi
daypart_rentals = hour_df.groupby('daypart', observed=True)['total_count'].sum().reset_index()

# Plot
fig3, ax3 = plt.subplots(figsize=(10, 5))
sns.barplot(
    x='daypart', y='total_count', data=daypart_rentals, 
    palette='viridis', hue='daypart', legend=False, ax=ax3
)
ax3.set_title("Total Penyewaan Sepeda Berdasarkan Kelompok Waktu", fontsize=14, fontweight='bold')
ax3.set_xlabel("Kelompok Waktu", fontsize=12)
ax3.set_ylabel("Total Penyewaan (Juta Unit)", fontsize=12)
st.pyplot(fig3)

with st.expander("Lihat Insight Lanjutan"):
    st.write("Secara akumulatif (menggabungkan semua tipe pengguna), periode **Evening (17:00 - 21:00)** adalah sesi paling sibuk secara keseluruhan, disusul oleh **Afternoon**.")

st.caption("Copyright © Alma Wulan Saptaningrum 2026")