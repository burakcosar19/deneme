# -*- coding: utf-8 -*-
"""
Created on Thu Jan 30 17:29:37 2025

@author: lenovo
"""

import streamli as st
st.set_page_config(page_title="Noise and Vibration Post Processing", page_icon=":bar_chart:", layout="wide")
import matplotlib.pyplot as plt
import plotly.express as px
import pandas as pd
from datetime import datetime
from streamlit_app_döngülü import mainn
from utils import df_t60, df_t60_dolu, yutum_katsayisi
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from overall_plot import deneme_plot
from overall_plot import deneme_plot1


col1, col2 = st.columns([1, 0.5])
with col1:
    st.markdown("<h1 style='font-weight: bold; font-size: 46px;'>Noise and Vibration Post Processing</h1>", 
                unsafe_allow_html=True)
with col2:
    st.image("https://static.wixstatic.com/media/349070_f1acaa38d241433d82ef28801913235c~mv2.png/v1/fill/w_251,h_68,al_c,q_85,usm_0.66_1.00_0.01,enc_avif,quality_auto/349070_f1acaa38d241433d82ef28801913235c~mv2.png")    
    
def generate_pdf(graph_shown): # pdf oluÅturmak iÃ§in fonksiyon
    c = canvas.Canvas("rapor.pdf", pagesize=letter)
    #if graph_shown:
    #    graph = mainn() #mainn fonk Ã§aÄÄ±rarak grafiÄi Ã§ektik
    #    plt.savefig("graph.png") #grafiÄi png olarak kaydediyo
    #    c.drawInlineImage("graph.png", 100, 380, width=400, height=300)

    plt.savefig("yutum_katsayisi.png")  # yutum katsayÄ±sÄ± grafiÄini png olarak kaydediyoruz
    c.drawInlineImage("yutum_katsayisi.png", 100, 350, width=400, height=300)  # PDF'e grafiÄi ekliyoruz
    c.drawString(100, 750, "Noise and Vibration Post Processing Report")
    c.drawString(100, 700, f"Test Talep Eden/ Firma: {st.session_state.firma}")
    c.drawString(100, 680, f"Malzeme Ismi: {st.session_state.malzeme}")
    c.drawString(100, 660, f"Silinen Deney Tarihi: {st.session_state.test_date}")
    #c.drawString(100, 640, f"Dolu Kabin Ä°Ã§in T60 DeÄerleri: {st.table(df_t60_dolu)}")

    c.showPage()
    c.save()    


def main():
    st.sidebar.title("Noise and Vibration Post Processing Menu")
    menu = ["Home Page", "Test","Test_Overall","Report"]
    choice = st.sidebar.selectbox("Home Page", menu)
    
    if choice == "Home Page":
        st.markdown("<h1 style='font-size: 28px;'>Home Page<span style='font-size: 28px;'>🏠 </span></h1>", unsafe_allow_html=True)
        st.write("""This web application is intended for analyzing acoustic data and determining the sound absorption coefficient of a material.
                 has been developed. Acoustic Analysis Applications is a branch of science that focuses on the analysis and evaluation of sound and vibrations. These analyzes are usually acoustic measurements, 
                 is performed using specialized software and hardware systems, including data collection and evaluation processes.
                 Acoustic analysis is critical in many fields, for example, building acoustics, environmental noise control, the automotive industry, electroacoustic devices and medical applications.
An application in this field can include processes such as determining the sound absorption coefficient, measuring reverberation times and evaluating sound insulation performances. 
Acoustic analysis is used to create quality sound environments, reduce noise pollution and provide comfortable living spaces. 
It is also possible to optimize the acoustic properties of structures to improve music and speech performances.
                 """)
        st.image('https://static.wixstatic.com/media/11062b_a9e50b12c27349e192c096a0bf39b18d~mv2.jpeg/v1/fill/w_1886,h_609,al_c,q_85,usm_0.66_1.00_0.01,enc_avif,quality_auto/11062b_a9e50b12c27349e192c096a0bf39b18d~mv2.jpeg')
        
        
    elif choice == "Test":
        st.markdown("<h1 style='font-size: 28px;'>Test Page <span style='font-size: 28px;'>📊</span></h1>", unsafe_allow_html=True)
        uploaded_file = st.file_uploader(":file_folder: Upload your data file here. ",type=(["csv","txt","xlsx","xls"]))
        data = None
        if uploaded_file is not None:
            data = pd.read_csv(uploaded_file)   
            st.dataframe(data)
        else:
            st.warning("Upload your data file here.")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            firma = st.text_input("Test Requestor / Company:")
        with col2:
            malzeme = st.text_input("Material Name:")
        with col3:
            test_date = st.date_input("Test Date", datetime.today())
        
        if st.button("T60 Values for Empty Cabin"):
            st.table(df_t60)
        if st.button("T60 Values for Full Cabin"):
            st.table(df_t60_dolu)   
            #yutum_katsayisi()

        if st.button("Show Results"): # bu butona basÄ±ldÄ±ÄÄ±nda kod Ã§alÄ±Åcak
            if firma.strip() == "" or malzeme.strip() == "" or test_date is None or data is None:
                st.error(":exclamation: Please fill in all fields.")
            else:
                #mainn()
                yutum_katsayisi()
                #generate_pdf(st.session_state.show_graph)
                st.session_state.show_graph = True #sonuÃ§larÄ± gÃ¶ster butonuna basÄ±ldÄ±ÄÄ±nda true olarak dÃ¶ndÃ¼recek bu deÄiÅkeni
        else:
            st.session_state.show_graph = False #sonuÃ§larÄ± gÃ¶ster butonuna basÄ±lmamÄ±Åsa bu deÄiÅken false olcak
        # grafikleri gÃ¶sterip gÃ¶stermemek iÃ§in yaptÄ±m bu deÄiÅkenleri

        st.session_state.firma = firma
        st.session_state.malzeme = malzeme
        st.session_state.test_date = test_date


    elif choice == "Test_Overall":
        st.markdown("<h1 style='font-size: 28px;'>Test Page <span style='font-size: 28px;'>📊</span></h1>", unsafe_allow_html=True)
        
        # Sayfa başlığını ayarla
         #st.set_page_config(page_title="FFT Settings", layout="wide")

        # Başlık
        st.title("FFT Settings Panel")

        # İki sütun oluştur
        col1, col2 = st.columns(2)

        # Common properties
        with col1:
            st.header("Common properties")
            harmonic_list = st.text_input("Harmonic list", "-12;-4;4;12")
            fft_window = st.selectbox("FFT window", ["Hanning", "Hamming", "Blackman", "Flat-top"], index=0)
            amplitude = st.selectbox("Amplitude", ["RMS", "Peak"], index=0)
            data_collection = st.selectbox("Data collection", ["Right Edge of Bin","Center of Bin","Left Edge of Bin"], index=0)
            bin_update = st.selectbox("Bin update", ["Always","Conditional", "Never"], index=0)
            spectral_weighting = st.selectbox("Spectral weighting", ["None", "A-weighting", "C-weighting", "Z-weighting"], index=0)
            skip_missing_bins = st.checkbox("Skip missing bins")

        # Time FFT setup
        with col2:
            st.header("Time FFT setup")
            time_domain_harmonics = st.checkbox("Time domain harmonics")
            update_on_reference_change = st.checkbox("Update on reference change (Delta)", disabled=True)
            update_on = st.number_input("Update on (sec)", value=0.5, step=0.1, min_value=0.0)
            
            st.subheader("FFT Waterfall vs. Reference")
            fft_waterfall = st.checkbox("FFT waterfall vs. reference", value=True)
            fft_lines = st.selectbox("FFT Lines", [4096, 8192, 12288, 16384, 20480], index=0)
            frequency_axis_unit = st.selectbox("Frequency axis unit", ["Hz", "kHz"], index=0)
            
            overall_rms = st.checkbox("Overall RMS vs. reference", value=True)

        # Alt bilgi
        st.markdown("---")
        st.markdown("⚙️ This interface allows users to configure FFT settings interactively.")
        
       
        
        
        test_option = st.radio("Select Test Option:", ["Overall vs Time", "Overall vs RPM"])  
        if test_option == "Overall vs Time":
            st.write("This is the content of Overall vs Time.")
            # Buraya Test Seçeneği 1 ile ilgili kodlarınızı ekleyin
        elif test_option == "Overall vs RPM":
            st.write("This is the Overall vs RPM content.")
            # Buraya Test Seçeneği 2 ile ilgili kodlarınızı ekleyin

        if st.button("Show Graphic"):
            if test_option == "Overall vs Time":
                deneme_plot()
            elif test_option == "Overall vs RPM":
                deneme_plot1()
                
                
            

            

        uploaded_file = st.file_uploader(":file_folder: Upload your data file here. ",type=(["csv","txt","xlsx","xls"]))
        data = None
        if uploaded_file is not None:
            data = pd.read_csv(uploaded_file)   
            st.dataframe(data)
        else:
            st.warning("Upload your data file here.")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            firma = st.text_input("Test Requestor / Company:")
        with col2:
            malzeme = st.text_input("Material Name:")
        with col3:
            test_date = st.date_input("Test Date", datetime.today())

        st.session_state.firma = firma
        st.session_state.malzeme = malzeme
        st.session_state.test_date = test_date
    

    elif choice == "Report":
        st.slider("What is your level",0,2000,step=50)
        st.markdown("<h1 style='font-size: 28px;'>Report Page <span style='font-size: 28px;'>📈</span></h1>", unsafe_allow_html=True)
        st.write("This page is where reports are guaranteed.")
        st.write("Test Requestor / Company:", st.session_state.firma)
        st.write("Material Name:", st.session_state.malzeme)
        st.write("Selected Experiment Date:", st.session_state.test_date)
        #st.table(df_t60_dolu)
        
        if st.session_state.show_graph:  # Bu koÅul eklenerek T60 dolu tablosu kontrolÃ¼ yapÄ±lÄ±r
            st.table(df_t60_dolu)
            yutum_katsayisi()

        if not st.session_state.show_graph: # sonuÃ§larÄ± gÃ¶ster butonuna basÄ±lmadan rapor sekmesine geÃ§ilirse
            st.error(":exclamation: You cannot create a Report without performing the actions on the Test page.")
        else:
            generate_pdf(st.session_state.show_graph)

            with open("rapor.pdf", "rb") as f:
                st.download_button("Download Report as PDF", f.read(), file_name="rapor.pdf", key="pdf-download")

if __name__ == "__main__":
    main()  

    


    
