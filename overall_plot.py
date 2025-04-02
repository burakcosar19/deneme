# -*- coding: utf-8 -*-
"""
Created on Mon Feb 10 02:41:14 2025

@author: lenovo
"""
import glob 
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
from timeTorpm import TimeSeriesAnalyzer
#from rpmTotime import RpmSeriesAnalyzer

def deneme_plot():
    # Excel dosyasını oku
    #df = pd.read_excel("overallll.xlsx")
    
    file_path = glob.glob("*ornek_data_04.csv")[0]
    df = pd.read_csv(file_path)

    rpm_data = df['rpm'].values
    t_data = df['s'].values - df['s'].values[0]
    pa_data = df['Pa'].values
 
     # Örneklem frekansı ve A-weighting
    fs, weighted_pa =RpmSeriesAnalyzer.calculate_sample_rate(t_data, pa_data)
   
    # RPM işleme
    rpm, dB =RpmSeriesAnalyzer.process_rpm_data(
        rpm_data=rpm_data,
        t_data=t_data,
        pa_data=weighted_pa,
        start_rpm_step=25,
        window_type='hann'
    )
    
    # Görselleştirme
    plt.figure(figsize=(10,6))
    plt.plot(rpm, dB, 'k--', label='Hesaplanan Veri')
    plt.xlabel('RPM'), plt.ylabel('dB(A)')
    plt.title('RPM vs Ses Seviyesi')
    plt.grid(True), plt.legend()
    plt.show()
        

    # Grafiği göster
    st.pyplot()


def deneme_plot1():
    #df = pd.read_excel("TPA_Ornek_Data_Analiz_OALevel_vs_RPM.xlsx")
    file_path = glob.glob("*ornek_data_04.csv")[0]
    df = pd.read_csv(file_path)

        # Veriler
    t_data = df['s'].values  # RPM zaman verisi
    t_data = t_data - t_data[0]
    rpm_data = df['rpm'].values  # RPM verisi
    pa_data = df['Pa'].values  # Pa verisi


    pressure = TimeSeriesAnalyzer.calculate_a_weighted_pressure(t_data, pa_data)  

    n_block = TimeSeriesAnalyzer.calculate_n_blocks(rpm_data, rpm_step=25)  

    rpm, overall = TimeSeriesAnalyzer.analyze_time_series(t_data, rpm_data, t_data,pressure, n_block ) 

    TimeSeriesAnalyzer.plot_results(rpm,overall)

    st.pyplot()

if __name__ == "__deneme_plot__":
    deneme_plot()
