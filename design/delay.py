import numpy as np
import matplotlib.pyplot as plt
import math

class CircularBuffer:
    """
    This class implements a circular buffer. The size of the buffer will be the nearest
    power of two to the requested size.

    Attributes
    ----------
    buf_size (int): The size of the circular buffer
    write_pointer (int): cicular buffer writting head
    buffer (np.ndarray): circular buffer
    wraping_mask (int): Mask used to wrap the read pointer efficiently.
    """
    def __init__(self, buf_size):
        self.buf_size = int(math.pow(2, math.ceil(math.log(buf_size) / math.log(2))))
        self.buffer = np.zeros(self.buf_size)
        self.wraping_mask = self.buf_size - 1
        self.write_pointer = 0

    def reset(self):
        """
        Resets the circular buffer pointers and re-initialize the
        buffer to 0s.
        """
        self.read_pointer = 0
        self.buffer[:,:] = 0

    def write_sample(self, x):
        """
        Writes an input sample into the circular buffer and advances the
        write pointer.

        Params
        ------
        x (float): input sample
        """
        self.buffer[self.write_pointer] = x
        self.write_pointer = (self.write_pointer + 1) & self.wraping_mask

    def _read_sample(self, delay):
        """
        Reads a sample from the delay line. and updates the
        read pointer.

        Params
        ------
        delay (int) the delay to be applied in samples

        return
        ------
        y (float): The output sample.
        """
        # - 1 as we read before we write.
        read_pointer = (self.write_pointer - 1) - int(delay)
        read_pointer &= self.wraping_mask

        return self.buffer[read_pointer]

    def read_sample(self, delay):
        """
        """
        y1 = self._read_sample(int(delay))
        y2 = self._read_sample(int(delay) + 1)

        fraction = delay - int(delay)

        return (fraction * y2) + (1.0 - fraction) * y1

class Delay:
    """
    This class implements an audio delay.

    Attributes
    ---------
    sample_rate (int): Sampling rate in Hz.

    circular_buffer (circularBuffer): Circular buffer used for the delay.

    feedback (float): feedback amount (in the range [0, 1])
    """

    MAX_DELAY_TIME_S = 3

    def __init__(self, sample_rate, delay_time_s, feedback, dry_wet):
        """
        class constructor.

        Arguments
        ---------
        sample_rate (int): Sample rate of the delay.

        delay_time_s (float): delay time in seconds.

        feedback (float): feedback amount (in the range [0, 1])

        dry_wet (float): dry / wet amount (in the range [0, 1] 0 being fully
        dry, 1 being completely wet).
        """
        self.sample_rate = sample_rate
        self.circular_buffer = CircularBuffer(int(self.MAX_DELAY_TIME_S * sample_rate))
        self.feedback = feedback
        self.dry_wet = dry_wet

        self.delay_in_samples = delay_time_s * self.sample_rate

    def process(self, x):
        """
        Processes a signal through the delay.

        Arguments
        ---------
        x (float): delay input.

        returns
        -------
        y: delay output.
        """
        y = self.circular_buffer.read_sample(self.delay_in_samples)

        self.circular_buffer.write_sample(x + self.feedback * y)

        return self.dry_wet * y + (1 - self.dry_wet) * x


if __name__== "__main__":
    duration = 3
    sample_rate = 44100
    delay_time_s = 0.15
    num_samples = int(sample_rate * duration)
    feedback = 0.5
    dry_wet = 0.5

    in_signal = np.zeros(num_samples)
    in_signal[0] = 1

    out_signal = np.zeros(num_samples)

    dut = Delay(sample_rate, delay_time_s, feedback, dry_wet)

    for i, sample in enumerate(in_signal):
        out_signal[i] = dut.process(sample)

    time = np.arange(num_samples) / sample_rate

    plt.figure(figsize=(10, 6))
    plt.plot(time, in_signal)
    plt.plot(time, out_signal)
    plt.show()
