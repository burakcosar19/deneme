from acoustics.signal import *
from acoustics.bands import *
from acoustics.standards.iso_tr_25417_2007 import REFERENCE_PRESSURE
from acoustics.standards.iec_61672_1_2013 import (NOMINAL_OCTAVE_CENTER_FREQUENCIES,NOMINAL_THIRD_OCTAVE_CENTER_FREQUENCIES)

import streamlit as st                                                    
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from scipy.optimize import curve_fit
from sklearn.linear_model import LinearRegression 
import os
from time import localtime, strftime
#from scipy.interpolate import interp1d

data=pd.read_csv('Alpha_2.txt')
fs= 50000
####window_size= fs/20

# bu fonksiyonda ses sinyalini frekans domaininde analiz edilir ve farklı frekans bantlarında sesin güç değerleri hesaplanır.
def third_octaves2(p, window_size, density=False,frequencies=NOMINAL_THIRD_OCTAVE_CENTER_FREQUENCIES,ref=REFERENCE_PRESSURE):
    #fob, level = third_octaves2(np.array(channelData[i:i+int(frameSize)]), sampleRate1, False, THIRD_OCTAVE_CENTER_FREQUENCIES)
    
    """Calculate level per 1/3-octave in frequency domain using the FFT.
    :param x: Instantaneous signal :math:`x(t)`.
    :param fs: Sample frequency.
    :param density: Power density instead of power.
    :returns: Tuple. First element is an instance of :class:`OctaveBand`. The second element an array.
    .. note:: Based on power spectrum (FFT)
    .. seealso:: :attr:`acoustics.bands.THIRD_OCTAVE_CENTER_FREQUENCIES`
    .. note:: Exact center frequencies are always calculated.
    """

    #fs=window_size
    fob = OctaveBand(center=frequencies, fraction=3)
    f, p = power_spectrum(p, fs)
    fnb = EqualBand(f)
    power = integrate_bands(p, fnb, fob ) 
    if density:
        power /= (fob.bandwidth/fnb.bandwidth)
    level = 10.0*np.log10(power / ref**2.0) #hesaplanan güçler kullanılarak seviyeler hesaplanıyo ve dB cinsine dönüştürülüyo.
    return fob, level

#fob,level= third_octaves2(data['basinc'], window_size, density=False,frequencies=NOMINAL_THIRD_OCTAVE_CENTER_FREQUENCIES,ref=REFERENCE_PRESSURE)
#print(fob,level)


time_max = int(data['zaman'].max())   # data olarak oluşturulan data frameden veri seçiliyo burda mesela zaman sütunu şeçildi 
# bu sütunun en büyük değeri alındı ses sinyalinin uygulama süresi belirlendi

TDP= int(fs*time_max)
print("total data point=",TDP)

data['basinc_yeni']= data['basinc'][0:TDP] # analizin daha hızlı olması için belirli bir bölümü kullanıldı datanın

bands = {}
center_freq=[400,500,630,800,1000,1250,1600,2000,2500,3150,4000,5000,6300,8000,10000]
#center_freq=[1000]
t60_degerleri= []
for center_freq in center_freq: # center_freqi frequencies içine yazıyoruz
    bands[str(center_freq)] = []

    for keys, values in bands.items():
        #window_size =int(keys)*2 
        window_size = 3000  
        step = int(window_size / 2)
        delta_t = time_max / (TDP / (window_size) * 2)
        times = np.linspace(0, time_max, num=int(time_max / delta_t))

        for i in range(0, TDP + step, step):
            fob, level = third_octaves2(data['basinc_yeni'][i:int(window_size) + i], fs, density=False,frequencies=center_freq, ref=REFERENCE_PRESSURE)
            bands[keys].append(level)

    # neden bu saniyeleri aldık?
    saniye_3 = (len(bands[keys]) / time_max) * 3  # upper lower degerlerini görmek istiyosak saniyeleri dışarı aldım for keysin altına
    saniye_6 = (len(bands[keys]) / time_max) * 6
    selected_value = bands[keys][int(saniye_3):int(saniye_6)]
    average_level = np.mean(selected_value)
    upper_point = average_level - 5  # üst limit hesabı
    #print(f"bant degeri: {keys}, upper point degeri: {upper_point}")
    #plt.plot(times, bands['10000'][:len(times)])

    saniye_12 = (len(bands[keys]) / time_max) * 12
    saniye_14 = (len(bands[keys]) / time_max) * 14
    selected_value2 = bands[keys][int(saniye_12):int(saniye_14)]
    lower_point = np.nanmean(selected_value2)
    #print(f"bant degeri: {keys}, lower point: {lower_point}")

    band_data = bands[keys][:len(times)]
    df = pd.DataFrame({'times': times, f'band_{keys}_level': band_data})
    #print(df)

    #st.title("Akustik Analiz ! ")

    #for center_freq in center_freq_list:  # center_freq_list, tüm merkez frekanslarının bir listesi
        #keys = str(center_freq)

    if upper_point - 30 > lower_point:
        filtered_values = df[(df['times'] >= 6) & (df['times'] <= 12) & (df[f'band_{keys}_level'] < upper_point) & (df[f'band_{keys}_level'] > upper_point - 30)]

        x_verileri = np.array(filtered_values['times']).reshape(-1, 1)
        y_verileri = np.array(filtered_values[f'band_{keys}_level']).reshape(-1, 1)

        reg_model = LinearRegression()
        reg_model.fit(x_verileri, y_verileri)
        predict_y = reg_model.predict(x_verileri)

        a = reg_model.coef_[0][0]
        b = reg_model.intercept_[0]

        t_ilk = (upper_point - b) / a
        t_son = (upper_point - 60 - b) / a
        T30 = (t_son - t_ilk) * 1000
        T60= T30*2
        print("T60 degeri:", T60, "mili saniye")
        t60_degerleri.append({'merkez frekansları': center_freq, 'boş kabin T60 değerleri': T60})
        
        #st.subheader(f"Curve Fit Grafigi - Bant: {keys}")
        #fig, ax = plt.subplots()
        #ax.plot(df['times'], df[f'band_{keys}_level'])
        #ax.scatter(filtered_values['times'], filtered_values[f'band_{keys}_level'], color='red')
        #ax.plot(x_verileri, predict_y, color='yellow')
        #ax.set_xlabel('Zaman')
        #ax.set_ylabel('Seviye')
        #ax.axhline(upper_point, color='red', linestyle='--')
        #ax.axhline(lower_point, color='blue', linestyle='--')
        #st.pyplot(fig)
        #st.plotly_chart(fig)

        #st.subheader(f"Sonuçlar - Bant: {keys}, T60 Degeri: {T60:.2f} milisaniye")
        #st.write(f"T60 Degeri: {T60:.2f} milisaniye")  
    #else:
    #    print(f'The Test Is Not Okay For {keys}')
    #    st.write(f'Test Is Not Okay For {keys}')  
    df_t60 = pd.DataFrame(t60_degerleri)       
st.table(df_t60)

center_freqs = [800, 1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000, 6300, 8000, 10000]
T60_dolu= [2290.084167, 800.466085, 660.826036, 420.742212, 335.691303, 366.299362, 380.783909, 283.117575, 277.484426, 223.934179, 162.006617, 76.416757]
df_t60_dolu = pd.DataFrame({'merkez frekansları': center_freqs, 'dolu kabin T60 değerleri': T60_dolu})
#st.dataframe(df_t60_dolu)
st.table(df_t60_dolu)

def yutum_katsayisi():
    V = 6.44 #m^3
    A = 1.2 #m^2
    alfa_degerleri=[]

    for t60_dolu, t60_bos in zip(df_t60_dolu['dolu kabin T60 değerleri'], df_t60['boş kabin T60 değerleri']):
        alfa = 1.61 * (V / A) * (1 / t60_dolu - 1 / t60_bos)
        #print(f"alfa değerleri: {alfa}")
        alfa_degerleri.append(alfa)
    plt.figure(figsize=(10, 7))
    plt.plot(center_freqs, alfa_degerleri, marker='o')
    plt.xlabel('merkez frekansları')
    plt.ylabel('alfa değerleri')
    plt.title('ses yutum katsayısı grafiği')    
    plt.xticks(center_freqs, rotation=45,fontsize=8)
    plt.yticks(alfa_degerleri, rotation=0,fontsize=7)  
    #st.pyplot(plt.gcf()) #grafik figürünü alma????
    st.pyplot(plt)
st.subheader("Ses Yutum Katsayısı Grafiği")
yutum_katsayisi()