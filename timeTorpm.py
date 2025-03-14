import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import waveform_analysis  


def analyze_time_series(time_rpm, rpm, time_pa, pa, n_blocks):
    # Veri tiplerini numpy array'e çevirme
    time_rpm = np.array(time_rpm)
    rpm = np.array(rpm)
    time_pa = np.array(time_pa)
    pa = np.array(pa)
    
    # PA verilerine göre 56 eşit zaman bloğu oluşturma
    t_start = time_pa.min()
    t_end = time_pa.max()
    time_blocks = np.linspace(t_start, t_end, n_blocks + 1)
    
    # Sonuçları saklamak için listeler
    mean_rpms = []
    rms_pas = []
    block_starts = []
    block_ends = []
    
    # Her blok için analiz
    for i in range(len(time_blocks)-1):
        t0 = time_blocks[i]
        t1 = time_blocks[i+1]
        
        # RPM değerlerini filtreleme ve ortalama alma
        rpm_mask = (time_rpm >= t0) & (time_rpm <= t1)
        block_rpm = rpm[rpm_mask]
        mean_rpm = np.mean(block_rpm) if len(block_rpm) > 0 else np.nan
        
        # PA değerlerini filtreleme ve RMS hesaplama
        pa_mask = (time_pa >= t0) & (time_pa <= t1)
        pa_values = pa[pa_mask]
        
        # PA RMS hesaplama
        if len(pa_values) > 0:
            #window = np.hanning(len(pa_values))
            #window_correction_factor = np.sqrt(len(pa_values) / np.sum(window**2))
            block = pa_values #* window
            overall_pa = np.sqrt(np.mean(block**2)) # * np.sqrt(window_correction_factor)
            overall = 20 * np.log10(overall_pa/(2*10**-5))  # dB(A) dönüşümü
        else:
            overall = np.nan
        
        # Sonuçları listelere ekleme
        mean_rpms.append(mean_rpm)
        rms_pas.append(overall)
        block_starts.append(t0)
        block_ends.append(t1)
    
    
   
    return mean_rpms, rms_pas

# Veri dosyalarını okuma
#dataRpm = pd.read_excel("C:\\Users\\GkhnKznn\\Desktop\\AracNVH\\TPA_Ornek_Data_Analiz_RPMvsTime.xlsx", skiprows=60, header=0)
data = pd.read_csv("https://github.com/burakcosar19/deneme/blob/main/ornek_data_03.csv")
#dataOr = pd.read_excel("C:\\Users\\GkhnKznn\\Desktop\\AracNVH\\TPA_Ornek_Data_Analiz_OALevel_vs_RPM.xlsx")

# Veriler
s_data = data['s'].values  # RPM zaman verisi
rpm_data = data['rpm'].values  # RPM verisi

t_data = data['s'].values  # PA zaman verisi
t_data = t_data - t_data[0]
pa_data = data['Pa'].values  # Pa verisi

def calculate_a_weighted_pressure(time_data, pressure_data):

    # Örnekleme frekansını hesaplama
    delta_t = time_data[1] - time_data[0]  # İki örnek arasındaki zaman farkı
    fs = 1 / delta_t  # Örnekleme frekansı (Hz)
    
    # A-ağırlıklı basınç verisini hesaplama
    a_weighted_data = waveform_analysis.A_weight(pressure_data, fs)
    
    return a_weighted_data, fs

#örneklem frekansı hesaplma
#deltaT = t_data[1] - t_data[0]
#fs = 1/deltaT

#pa_data = waveform_analysis.A_weight(pa_data, fs)  # A-ağırlıklı PA verisi

#Orpm = dataOr['Linear'].values
#Ooverall = dataOr['dB(A)'].values

def calculate_n_blocks(rpm_data, rpm_step=25):

    max_rpm = max(rpm_data)
    min_rpm = min(rpm_data)
    return int((max_rpm - min_rpm) / rpm_step) + 1




# Analiz
#mean_rpms, rms_pas = analyze_time_series(s_data, rpm_data, t_data, pa_data, n_blocks)



# Görselleştirme
fig, ( ax2) = plt.subplots(1, 1, figsize=(12, 8))       
# PA RMS plot
ax2.plot(mean_rpms, rms_pas,color = 'black', label='yazilim') # type: ignore
#ax2.plot(Orpm, Ooverall, label='okan abi')
ax2.set_xlabel('rpm')
ax2.set_ylabel('dB(A)')
#ax2.set_xlim(750, 1800)
ax2.set_title('')
ax2.grid(True)
ax2.legend()
plt.tight_layout()
plt.show()


