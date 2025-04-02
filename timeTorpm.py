import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import glob
import streamlit as st

import numpy as np
from numpy import log10, pi
from scipy.signal import bilinear_zpk, freqs, sosfilt, zpk2sos, zpk2tf

__all__ = ['ABC_weighting', 'A_weighting', 'A_weight']


def ABC_weighting(curve='A'):
    """
    Design of an analog weighting filter with A, B, or C curve.

    Returns zeros, poles, gain of the filter.

    Examples
    --------
    Plot all 3 curves:

    >>> from scipy import signal
    >>> import matplotlib.pyplot as plt
    >>> for curve in ['A', 'B', 'C']:
    ...     z, p, k = ABC_weighting(curve)
    ...     w = 2*pi*np.geomspace(10, 100000, 1000)
    ...     w, h = signal.freqs_zpk(z, p, k, w)
    ...     plt.semilogx(w/(2*pi), 20*np.log10(h), label=curve)
    >>> plt.title('Frequency response')
    >>> plt.xlabel('Frequency [Hz]')
    >>> plt.ylabel('Amplitude [dB]')
    >>> plt.ylim(-50, 20)
    >>> plt.grid(True, color='0.7', linestyle='-', which='major', axis='both')
    >>> plt.grid(True, color='0.9', linestyle='-', which='minor', axis='both')
    >>> plt.legend()
    >>> plt.show()

    """
    if curve not in 'ABC':
        raise ValueError('Curve type not understood')

    # ANSI S1.4-1983 C weighting
    #    2 poles on the real axis at "20.6 Hz" HPF
    #    2 poles on the real axis at "12.2 kHz" LPF
    #    -3 dB down points at "10^1.5 (or 31.62) Hz"
    #                         "10^3.9 (or 7943) Hz"
    #
    # IEC 61672 specifies "10^1.5 Hz" and "10^3.9 Hz" points and formulas for
    # derivation.  See _derive_coefficients()

    z = [0, 0]
    p = [-2*pi*20.598997057568145,
         -2*pi*20.598997057568145,
         -2*pi*12194.21714799801,
         -2*pi*12194.21714799801]
    k = 1

    if curve == 'A':
        # ANSI S1.4-1983 A weighting =
        #    Same as C weighting +
        #    2 poles on real axis at "107.7 and 737.9 Hz"
        #
        # IEC 61672 specifies cutoff of "10^2.45 Hz" and formulas for
        # derivation.  See _derive_coefficients()

        p.append(-2*pi*107.65264864304628)
        p.append(-2*pi*737.8622307362899)
        z.append(0)
        z.append(0)

    elif curve == 'B':
        # ANSI S1.4-1983 B weighting
        #    Same as C weighting +
        #    1 pole on real axis at "10^2.2 (or 158.5) Hz"

        p.append(-2*pi*10**2.2)  # exact
        z.append(0)

    # TODO: Calculate actual constants for this
    # Normalize to 0 dB at 1 kHz for all curves
    b, a = zpk2tf(z, p, k)
    k /= abs(freqs(b, a, [2*pi*1000])[1][0])

    return np.array(z), np.array(p), k


def A_weighting(fs, output='ba'):
    """
    Design of a digital A-weighting filter.

    Designs a digital A-weighting filter for
    sampling frequency `fs`.
    Warning: fs should normally be higher than 20 kHz. For example,
    fs = 48000 yields a class 1-compliant filter.

    Parameters
    ----------
    fs : float
        Sampling frequency
    output : {'ba', 'zpk', 'sos'}, optional
        Type of output:  numerator/denominator ('ba'), pole-zero ('zpk'), or
        second-order sections ('sos'). Default is 'ba'.

    Examples
    --------
    Plot frequency response

    >>> from scipy.signal import freqz
    >>> import matplotlib.pyplot as plt
    >>> fs = 200000
    >>> b, a = A_weighting(fs)
    >>> f = np.geomspace(10, fs/2, 1000)
    >>> w = 2*pi * f / fs
    >>> w, h = freqz(b, a, w)
    >>> plt.semilogx(w*fs/(2*pi), 20*np.log10(abs(h)))
    >>> plt.grid(True, color='0.7', linestyle='-', which='both', axis='both')
    >>> plt.axis([10, 100e3, -50, 20])

    Since this uses the bilinear transform, frequency response around fs/2 will
    be inaccurate at lower sampling rates.
    """
    z, p, k = ABC_weighting('A')

    # Use the bilinear transformation to get the digital filter.
    z_d, p_d, k_d = bilinear_zpk(z, p, k, fs)

    if output == 'zpk':
        return z_d, p_d, k_d
    elif output in {'ba', 'tf'}:
        return zpk2tf(z_d, p_d, k_d)
    elif output == 'sos':
        return zpk2sos(z_d, p_d, k_d)
    else:
        raise ValueError(f"'{output}' is not a valid output form.")


def A_weight(signal, fs):
    """
    Return the given signal after passing through a digital A-weighting filter

    signal : array_like
        Input signal, with time as dimension
    fs : float
        Sampling frequency
    """
    # TODO: Upsample signal high enough that filter response meets Type 0
    # limits.  A passes if fs >= 260 kHz, but not at typical audio sample
    # rates. So upsample 48 kHz by 6 times to get an accurate measurement?
    # TODO: Also this could just be a measurement function that doesn't
    # save the whole filtered waveform.
    sos = A_weighting(fs, output='sos')
    return sosfilt(sos, signal)


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
        a_weighted_data = A_weight(pressure_data, fs)
        
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

