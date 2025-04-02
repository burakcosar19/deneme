import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from waveform_analysis import A_weight, A_weighting, ABC_weighting
import glob
import streamlit as st

class TimeSeriesAnalyzer:
    def __init__(self, file_pattern="*ornek_data_04.csv", rpm_step=25):
        # Veri dosyasını okuma
        self.file_path = glob.glob(file_pattern)[0]
        self.data = pd.read_csv(self.file_path)
        
        # Verileri çıkarma
        self.s_data = self.data['s'].values  # RPM zaman verisi
        self.rpm_data = self.data['rpm'].values  # RPM verisi
        self.t_data = self.data['s'].values  # PA zaman verisi
        self.t_data = self.t_data - self.t_data[0]
        self.pa_data = self.data['Pa'].values  # Pa verisi
        


    def calculate_n_blocks( rpm_data, rpm_step=25):
        """RPM verisine göre blok sayısını hesaplar."""
        max_rpm = 2175 #int(max(rpm_data))
        min_rpm = 599.99#int(min(rpm_data))
        return int((max_rpm - min_rpm) / rpm_step) + 1
    
    def calculate_a_weighted_pressure( time_data, pressure_data):
        """A-ağırlıklı basınç hesaplamasını yapar."""
        delta_t = time_data[1] - time_data[0]  # İki örnek arasındaki zaman farkı
        fs = 1 / delta_t  # Örnekleme frekansı (Hz)
        
        # A-ağırlıklı basınç verisini hesaplama
        a_weighted_data = waveform_analysis.A_weight(pressure_data, fs)
        
        return a_weighted_data

    def analyze_time_series( t_data, rpm_data,s_data,pa_data, n_block):
        """Zaman serisi verilerini analiz eder."""
        # PA verilerine göre 56 eşit zaman bloğu oluşturma
        t_start = t_data.min()
        t_end = t_data.max()
        time_blocks = np.linspace(t_start, t_end, n_block + 1)
        
        # Sonuçları saklamak için listeler
        mean_rpms = []
        rms_pas = []
        block_starts = []
        block_ends = []
        
        # Her blok için analiz
        for i in range(len(time_blocks) - 1):
            t0 = time_blocks[i]
            t1 = time_blocks[i + 1]
            
            # RPM değerlerini filtreleme ve ortalama alma
            rpm_mask = (s_data >= t0) & (s_data <= t1)
            block_rpm = rpm_data[rpm_mask]
            mean_rpm = np.mean(block_rpm) if len(block_rpm) > 0 else np.nan
            
            # PA değerlerini filtreleme ve RMS hesaplama
            pa_mask = (t_data >= t0) & (t_data <= t1)
            pa_values = pa_data[pa_mask]
            
            # PA RMS hesaplama
            if len(pa_values) > 0:
                block = pa_values
                overall_pa = np.sqrt(np.mean(block**2))
                overall = 20 * np.log10(overall_pa / (2 * 10**-5))  # dB(A) dönüşümü
            else:
                overall = np.nan
            
            # Sonuçları listelere ekleme
            mean_rpms.append(mean_rpm)
            rms_pas.append(overall)
            block_starts.append(t0)
            block_ends.append(t1)
        
        return mean_rpms, rms_pas

    def plot_results(mean_rpms, rms_pas):
        """Analiz sonuçlarını görselleştirir."""
        fig, (ax2) = plt.subplots(1, 1, figsize=(12, 8))       
        # PA RMS plot
        ax2.plot(mean_rpms, rms_pas, color='black', label='Yazılım')
        ax2.set_xlabel('RPM')
        ax2.set_ylabel('dB(A)')
        ax2.set_title('PA RMS vs RPM')
        ax2.grid(True)
        ax2.legend()
        plt.tight_layout()
        plt.show()
        st.pyplot(fig)
'''
# Kullanım örneği
analyzer = TimeSeriesAnalyzer(file_pattern="*ornek_data_04.csv",  rpm_step=25)

# Zaman serisini analiz et
mean_rpms, rms_pas = analyzer.analyze_time_series()

# Sonuçları görselleştir
analyzer.plot_results(mean_rpms, rms_pas)
'''

