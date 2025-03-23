import numpy as np
import pandas as pd
import waveform_analysis

def calculate_sample_rate(t_data, pa_data):
    """
    Örneklem frekansını hesaplar ve A-ağırlık filtresi uygular
    """
    deltaT = t_data[1] - t_data[0]
    fs = 1 / deltaT
    weighted_pa = waveform_analysis.A_weight(pa_data, fs)
    return fs, weighted_pa

def process_rpm_data(rpm_data, t_data, pa_data, 
                    start_rpm_step=25, window_type='hann'):
    """
    RPM aralıklarını işleyip dB(A) değerlerini hesaplar
    
    Parametreler:
    - rpm_data: RPM değerleri array'i
    - s_data: Zaman damgaları array'i
    - t_data: Hizalı zaman array'i
    - pa_data: Ağırlıklandırılmış basınç verisi
    - start_rpm_step: RPM artış adımı (default 25)
    - window_type: Pencereleme fonksiyonu (default hann)
    
    Çıktı:
    - (rpm_list, dB_values): RPM ve karşılık gelen dB(A) listeleri
    """
    # Pencere fonksiyonu seçimi
    window_functions = {
        'hann': np.hanning,
        'hamming': np.hamming,
        'blackman': np.blackman
    }
    window = window_functions.get(window_type, np.hanning)

    # Değişkenleri başlat
    current_rpm = int(np.min(rpm_data))
    last_end_time = np.min(t_data)
    rpm_list = []
    dB_values = []

    while current_rpm < np.max(rpm_data):
        next_rpm = current_rpm + start_rpm_step
        
        # RPM aralığı için maske oluştur
        mask = (rpm_data >= current_rpm) & (rpm_data < next_rpm)
        rpm_section = rpm_data[mask]
        time_section = t_data[mask]

        if len(rpm_section) > 0:
            valid_times = time_section[time_section >= last_end_time]
            
            if len(valid_times) > 0:
                start_time = np.min(valid_times)
                end_time = np.max(valid_times)
                
                # PA verilerini zaman aralığına göre al
                pa_mask = (t_data >= start_time) & (t_data < end_time)
                pa_values = pa_data[pa_mask]
                
                if len(pa_values) > 0:
                    # Pencereleme ve düzeltme faktörü
                    N = len(pa_values)
                    win = window(N)
                    correction = np.sqrt(N / np.sum(win**2))
                    
                    # RMS hesapla
                    rms = np.sqrt(np.mean((pa_values * win)**2)) * correction
                    dB = 20 * np.log10(rms/(2e-5))
                    
                    # Sonuçları kaydet
                    rpm_list.append(np.mean(rpm_section))
                    dB_values.append(dB)
                    last_end_time = end_time

        current_rpm = next_rpm

    return rpm_list, dB_values

# Ana işlem akışı örneği
if __name__ == "__main__":
    # Veri yükleme
    data = pd.read_csv("C:\\Users\\GkhnKznn\\Downloads\\Ornek_Datalar_Karsilastirildi\\ornek_data_03.csv")
    rpm_data = data['rpm'].values
    t_data = data['s'].values - data['s'].values[0]
    pa_data = data['Pa'].values

    # Örneklem frekansı ve A-weighting
    fs, weighted_pa = calculate_sample_rate(t_data, pa_data)

    # RPM işleme
    rpm, dB = process_rpm_data(
        rpm_data=rpm_data,
        t_data=t_data,
        pa_data=weighted_pa,
        start_rpm_step=25,
        window_type='hann'
    )

    # Görselleştirme
    import matplotlib.pyplot as plt
    plt.figure(figsize=(10,6))
    plt.plot(rpm, dB, 'k--', label='Hesaplanan Veri')
    plt.xlabel('RPM'), plt.ylabel('dB(A)')
    plt.title('RPM vs Ses Seviyesi')
    plt.grid(True), plt.legend()
    plt.show()