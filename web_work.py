# -*- coding: utf-8 -*-
"""
Created on Thu Jan 30 17:29:37 2025

@author: lenovo
"""

import streamlit as st
st.set_page_config(page_title="Akustik Analiz Uygulamaları", page_icon=":bar_chart:", layout="wide")
import matplotlib.pyplot as plt
import plotly.express as px
import pandas as pd
from datetime import datetime
from streamlit_app_döngülü import mainn
from utils import df_t60, df_t60_dolu, yutum_katsayisi
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from overall_plot import deneme_plot


col1, col2 = st.columns([1, 0.5])
with col1:
    st.markdown("<h1 style='font-weight: bold; font-size: 46px;'>Akustik Analiz Uygulamalari</h1>", 
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
    c.drawString(100, 750, "Akustik Analiz Raporu")
    c.drawString(100, 700, f"Test Talep Eden/ Firma: {st.session_state.firma}")
    c.drawString(100, 680, f"Malzeme Ismi: {st.session_state.malzeme}")
    c.drawString(100, 660, f"Silinen Deney Tarihi: {st.session_state.test_date}")
    #c.drawString(100, 640, f"Dolu Kabin Ä°Ã§in T60 DeÄerleri: {st.table(df_t60_dolu)}")

    c.showPage()
    c.save()    


def main():
    st.sidebar.title("Akustik Analiz Menüsü")
    menu = ["Ana Sayfa", "Test","Test_Overall","Rapor"]
    choice = st.sidebar.selectbox("Menü", menu)
    
    if choice == "Ana Sayfa":
        st.markdown("<h1 style='font-size: 28px;'>Ana Sayfa <span style='font-size: 28px;'>🏠 </span></h1>", unsafe_allow_html=True)
        st.write("""Bu web uygulaması akustik veri analizi yapılması ve bir malzemenin ses absorpsiyon katsayısının belirlenmesi amacıyla
                 geliştirilmiştir. Akustik Analiz Uygulamaları, ses ve titreşimlerin analizi ve değerlendirilmesi üzerine odaklanan bir bilim dalıdır. Bu analizler, genellikle akustik ölçümler, 
                 veri toplama ve değerlendirme süreçlerini içeren, özel yazılım ve donanım sistemleri kullanılarak gerçekleştirilir. Akustik analizler, birçok alanda kritik öneme sahiptir; örneğin, bina akustiği, çevresel gürültü kontrolü, otomotiv endüstrisi, elektroakustik cihazlar ve tıbbi uygulamalar.
Bu alandaki bir uygulama, ses yutma katsayısının belirlenmesi, yankı sürelerinin ölçülmesi ve ses yalıtım performanslarının değerlendirilmesi gibi işlemleri içerebilir. Akustik analizler, kaliteli ses ortamları yaratmak, gürültü kirliliğini azaltmak ve konforlu yaşam alanları sağlamak amacıyla kullanılır. 
Ayrıca, bu analizler ile yapıların akustik özelliklerini optimize ederek, müzik ve konuşma performanslarını iyileştirmek mümkündür.
                 """)
        st.image('https://static.wixstatic.com/media/11062b_a9e50b12c27349e192c096a0bf39b18d~mv2.jpeg/v1/fill/w_1886,h_609,al_c,q_85,usm_0.66_1.00_0.01,enc_avif,quality_auto/11062b_a9e50b12c27349e192c096a0bf39b18d~mv2.jpeg')
        
        
    elif choice == "Test":
        st.markdown("<h1 style='font-size: 28px;'>Test Sayfası <span style='font-size: 28px;'>📊</span></h1>", unsafe_allow_html=True)
        uploaded_file = st.file_uploader(":file_folder: Veri dosyanızı buraya yükleyiniz. ",type=(["csv","txt","xlsx","xls"]))
        data = None
        if uploaded_file is not None:
            data = pd.read_csv(uploaded_file)   
            st.dataframe(data)
        else:
            st.warning("Lütfen bir veri dosyası yükleyin.")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            firma = st.text_input("Test Talep Eden/ Firma:")
        with col2:
            malzeme = st.text_input("Malzeme İsmi:")
        with col3:
            test_date = st.date_input("Test Tarihi", datetime.today())
        
        if st.button("Boş Kabin İçin T60 Değerleri"):
            st.table(df_t60)
        if st.button("Dolu Kabin İçin T60 Değerleri"):
            st.table(df_t60_dolu)   
            #yutum_katsayisi()

        if st.button("Sonuçları Göster"): # bu butona basÄ±ldÄ±ÄÄ±nda kod Ã§alÄ±Åcak
            if firma.strip() == "" or malzeme.strip() == "" or test_date is None or data is None:
                st.error(":exclamation: Lütfen tüm alanlarÄ± doldurun.")
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
        st.markdown("<h1 style='font-size: 28px;'>Test Sayfası <span style='font-size: 28px;'>📊</span></h1>", unsafe_allow_html=True)
        
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
        
       
        
        
        test_option = st.radio("Test Seçeneğini Seçiniz:", ["Overall vs Time", "Overall vs RPM"])  
        if test_option == "Overall vs Time":
            st.write("Bu, Overall vs Time içeriğidir.")
            # Buraya Test Seçeneği 1 ile ilgili kodlarınızı ekleyin
        elif test_option == "Overall vs RPM":
            st.write("Bu, Overall vs RPM içeriğidir.")
            # Buraya Test Seçeneği 2 ile ilgili kodlarınızı ekleyin

        if st.button("Grafiği Göster"):
            overall_plott()

        uploaded_file = st.file_uploader(":file_folder: Veri dosyanızı buraya yükleyiniz. ",type=(["csv","txt","xlsx","xls"]))
        data = None
        if uploaded_file is not None:
            data = pd.read_csv(uploaded_file)   
            st.dataframe(data)
        else:
            st.warning("Lütfen bir veri dosyası yükleyin.")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            firma = st.text_input("Test Talep Eden/ Firma:")
        with col2:
            malzeme = st.text_input("Malzeme İsmi:")
        with col3:
            test_date = st.date_input("Test Tarihi", datetime.today())

        st.session_state.firma = firma
        st.session_state.malzeme = malzeme
        st.session_state.test_date = test_date
    

    elif choice == "Rapor":
        st.slider("What is your level",0,2000,step=50)
        st.markdown("<h1 style='font-size: 28px;'>Rapor Sayfası <span style='font-size: 28px;'>📈</span></h1>", unsafe_allow_html=True)
        st.write("Bu sayfa raporların garantilendiği bölümdür.")
        st.write("Test Talep Eden/ Firma:", st.session_state.firma)
        st.write("Malzeme İsmi:", st.session_state.malzeme)
        st.write("Seçilen Deney Tarihi:", st.session_state.test_date)
        #st.table(df_t60_dolu)
        
        if st.session_state.show_graph:  # Bu koÅul eklenerek T60 dolu tablosu kontrolÃ¼ yapÄ±lÄ±r
            st.table(df_t60_dolu)
            yutum_katsayisi()

        if not st.session_state.show_graph: # sonuÃ§larÄ± gÃ¶ster butonuna basÄ±lmadan rapor sekmesine geÃ§ilirse
            st.error(":exclamation: Test sayfasındaki işlemleri gerçekleştirmeden Rapor oluşturamazsınız.")
        else:
            generate_pdf(st.session_state.show_graph)

            with open("rapor.pdf", "rb") as f:
                st.download_button("Raporu PDF Olarak İndir", f.read(), file_name="rapor.pdf", key="pdf-download")

if __name__ == "__main__":
    main()  

    


    
