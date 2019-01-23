import numpy as np


class OFDM:
    """Class that creates OFDM signals.

    This class will set up an OFDM modulator to create random OFDM signals.

    Attributes:
        n_subcarriers:  Number of subcarriers per OFDM symbol
        subcarrier_spacing: Spacing between subcarriers in Hz
        cp_length : Number of samples in the cyclic prefix
        fft_size: Size of the IFFT/FFT used.
        sampling_rate: The native sampling rate based on the FFT size and subcarrier spacing
        symbol_alphabet: The constellation points
    """

    def __init__(self, n_subcarriers, subcarrier_spacing, cp_length, constellation):
        """OFDM Modulator Constructor.

        Construct an OFDM Modulator with custom number of subcarriers, subcarrier spacing, cyclic prefix length,
        and constellation on each subcarrier.

        Args:
            n_subcarriers: Number of subcarriers per OFDM symbol
            subcarrier_spacing: Description of `param3`.
            cp_length: Description of `param3`.
            constellation: Type of constellation used on each subcarrier. QPSK, 16QAM or 64QAM
        """
        self.n_subcarriers = n_subcarriers
        self.subcarrier_spacing = subcarrier_spacing
        self.cp_length = cp_length

        self.fft_size = np.power(2, np.int(np.ceil(np.log2(n_subcarriers))))
        np.int(np.ceil(np.log2(n_subcarriers)))
        self.sampling_rate = self.subcarrier_spacing * self.fft_size
        self.symbol_alphabet = self.QAM_Alphabet(constellation)

    def use(self, n_symbols):
        """Use the OFDM modulator to generate a random signal.

        Args:
            n_symbols: Number of OFDM symbols to generate

        Returns:
            A time-domain OFDM signal

        TODO:
            - Allow to pass in an arbitrary bit pattern for modulation.
        """

        fd_symbols = self.symbol_alphabet[
            np.random.randint(self.symbol_alphabet.size, size=(self.n_subcarriers, n_symbols))]
        out = np.zeros((self.fft_size + self.cp_length, n_symbols), dtype='complex64')
        for index, symbol in enumerate(fd_symbols.T):
            td_waveform = self.frequency_to_time_domain(symbol)
            out[:, index] = self.add_cyclic_prefic(td_waveform)

        return out.flatten(1)

    def frequency_to_time_domain(self, fd_symbol):
        """Convert the frequency domain symbol to time domain via IFFT

        Args:
            fd_symbol: One frequency domain symbol

        Returns:
            time domain signal
        """
        # TODO: Verify that the RB are mapping to the IFFT input correctly
        ifft_input = np.zeros((self.fft_size), dtype='complex64')
        # Index 0 is DC. Leave blank. The 1st half needs to be in negative frequency so they go in the last IFFT inputs.
        ifft_input[1: np.int(self.n_subcarriers / 2)] = fd_symbol[np.int(self.n_subcarriers / 2) + 1:]
        ifft_input[-np.int(self.n_subcarriers / 2):] = fd_symbol[:np.int(self.n_subcarriers / 2)]
        return np.fft.ifft(ifft_input)

    def add_cyclic_prefix(self, td_waveform):
        """Adds cyclic prefix by taking the last few samples and appends it to the beginning of the signal

        Args:
            td_waveform: IFFT output signal.

        Returns:
            time domain signal with a cyclic prefix
        """

        # TODO: verify my indexing
        out = np.zeros(td_waveform.size + self.cp_length, dtype='complex64')
        out[self.cp_length:] = td_waveform
        out[:self.cp_length] = td_waveform[-self.cp_length:]
        return out

    @staticmethod
    def qam_alphabet(self, constellation):
        """Returns constellation points for QPSK, 16QAM, or 64 QAM

        Args:
            constellation: String saying the desired constellation

        Returns:
            symbol alphabet on the complex plane
        """
        constellation_dict = {
            "QPSK": 4,
            "16QAM": 16,
            "64QAM": 64
        }
        n_points = constellation_dict[constellation]
        x = np.int(np.sqrt(n_points)) - 1

        alpha_n_points = np.arange(-x, x + 1, 2, dtype=int)
        A = np.kron(np.ones((x + 1, 1)), alpha_n_points)
        B = np.flipud(A.transpose())
        const_qam = A + 1j * B
        alphabet = const_qam.flatten(1)
        return alphabet