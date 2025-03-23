import struct
import io

class ReadRPC:
    """
    Read RPC III (RSP) files from a file-like object (e.g., uploaded via Streamlit).
    """
    def __init__(self, f):
        self._i_opened_the_file = None
        # Eğer gelen nesne bir dosya yolu değilse, bu durumda bir BytesIO nesnesi olabilir
        if isinstance(f, io.BytesIO):
            self._i_opened_the_file = f
        else:
            raise ValueError("Geçersiz dosya formatı! BytesIO bekleniyor.")

        try:
            self.initfp(f)
        except Exception as e:
            if self._i_opened_the_file:
                f.close()
            raise e

    def initfp(self, file):
        self._fHeader = {}
        _head, _value = struct.unpack('<32s96s', file.read(128))
        _head = _head.rstrip(b'\0').decode()
        self._fHeader[_head] = _value.rstrip(b'\0').decode()

        _head, _value = struct.unpack('<32s96s', file.read(128))
        _head = _head.rstrip(b'\0').decode()
        self._fHeader[_head] = _value.rstrip(b'\0').decode()

        _head, _value = struct.unpack('<32s96s', file.read(128))
        _head = _head.rstrip(b'\0').decode()
        _value = _value.rstrip(b'\0').decode()
        self._fHeader[_head] = _value

        num_params = int(self._fHeader.get('NUM_PARAMS', '0'))
        if ((_head == 'NUM_PARAMS') and (num_params > 3)):
            for _ in range(num_params - 3):
                _head, _value = struct.unpack('<32s96s', file.read(128))
                self._fHeader[_head.rstrip(b'\0').decode()] = _value.rstrip(b'\0').decode()

    def header(self):
        return self._fHeader

    def close(self):
        if self._i_opened_the_file:
            self._i_opened_the_file.close()
            self._i_opened_the_file = None