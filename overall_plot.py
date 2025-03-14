# -*- coding: utf-8 -*-
"""
Created on Mon Feb 10 02:41:14 2025

@author: lenovo
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
from timeTorpm import calculate_a_weighted_pressure , calculate_n_blocks , analyze_time_series

def deneme_plot(data):
    # Excel dosyasını oku
    #df = pd.read_excel("overallll.xlsx")

    # Şekil ve eksenleri oluştur
    fig, ax = plt.subplots(figsize=(16, 6))

    # Çizgi grafiğini oluştur
    ax.plot(data["s"], data["Pa"], linewidth=6)

    # Başlık ve eksen etiketlerini ayarla
    ax.set_title("Overall Level vs. Time")
    ax.set_ylabel("Ses Basınç Seviyesi [dB(A)]", fontsize=8)
    ax.set_xlabel("Zaman (s)", fontsize=10)

    # X ekseni etiketlerini seyrekleştir
    ax.set_xticks(np.arange(0, data["Pa"].max(), step=10))  # X ekseni için 0.75 birimde bir göster
    ax.set_xticklabels(ax.get_xticks(), rotation=90, fontsize=8)
    ax.set_yticks(np.arange(0, 101, step=25))  # Y ekseni için 25 birimde bir göster

    # Y eksenine grid ekle
    ax.grid(axis='y', linestyle='--', alpha=0.5)

    # Grafiği göster
    st.pyplot(fig)


def deneme_plot1():
    df = pd.read_excel("TPA_Ornek_Data_Analiz_OALevel_vs_RPM.xlsx")

        # Veriler
    t_data = df['s'].values  # RPM zaman verisi
    t_data = t_data - t_data[0]
    rpm_data = df['rpm'].values  # RPM verisi
    pa_data = df['Pa'].values  # Pa verisi


    pressure, fs =timeTorpm.calculate_a_weighted_pressure(t_data, pa_data) # type: ignore

    n_block = timeTorpm.calculate_n_blocks(rpm_data, rpm_step=25) # type: ignore

    rpm, overall = timeTorpm.analyze_time_series(t_data, rpm_data, t_data,pressure, n_block ) # type: ignore

    # Şekil ve eksenleri oluştur
    fig, ax = plt.subplots(figsize=(16, 6))

    # Çizgi grafiğini oluştur
    ax.plot(rpm, overall, linewidth=6)



    # Başlık ve eksen etiketlerini ayarla
    ax.set_title("Overall Level vs. RPM")
    ax.set_ylabel("Ses Basınç Seviyesi [dB(A)]", fontsize=8)
    ax.set_xlabel("Zaman (s)", fontsize=10)

    # X ekseni etiketlerini seyrekleştir
    # X ekseni için 0.75 birimde bir göster
    ax.set_xticks(np.arange(0, df["Linear"].max(), step=50))
    ax.set_xticklabels(ax.get_xticks(), rotation=90, fontsize=8)
    # Y ekseni için 25 birimde bir göster
    ax.set_yticks(np.arange(0, 101, step=25))

    # Y eksenine grid ekle
    ax.grid(axis='y', linestyle='--', alpha=0.5)

    st.pyplot(fig)

if __name__ == "__deneme_plot__":
    deneme_plot()
