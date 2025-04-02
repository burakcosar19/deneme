import numpy as np
import pandas as pd
import numpy as np
from numpy import log10, pi
from scipy.signal import bilinear_zpk, freqs, sosfilt, zpk2sos, zpk2tf
class RpmSeriesAnalyzer:
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
        z, p, k = RpmSeriesAnalyzer.ABC_weighting('A')
    
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
        sos = RpmSeriesAnalyzer.A_weighting(fs, output='sos')
        return sosfilt(sos, signal)
    def calculate_sample_rate(t_data, pa_data):
        """
        Örneklem frekansını hesaplar ve A-ağırlık filtresi uygular
        """
        deltaT = t_data[1] - t_data[0]
        fs = 1 / deltaT
        weighted_pa = RpmSeriesAnalyzer.A_weight(pa_data, fs)
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
