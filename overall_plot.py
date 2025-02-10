# -*- coding: utf-8 -*-
"""
Created on Mon Feb 10 02:41:14 2025

@author: lenovo
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

def overall_plott():
    df=pd.read_excel("overallll.xlsx")
    plt.figure(figsize=(16, 6))  # Grafiği geniş yap, yükseklik düşük olsun
    plt.plot(df["Linear"], df["dB(A)"], linewidth=7)  # Çizgi grafiği

    plt.title("Overall Level vs. Time ")
    plt.ylabel("Ses Basınç Seviyesi [dB(A)]", fontsize=10)
    plt.xlabel("Zaman (s)", fontsize=10)


    # X ekseni etiketlerini seyrekleştir
    plt.xticks(np.arange(0, 45, step=0.75), rotation=90, fontsize=8)  # Her 5 birimde bir göster
    plt.yticks(np.arange(0, 100, step=25), rotation=90, fontsize=10)
    # Y eksenine grid ekle
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    
    st.pyplot()

