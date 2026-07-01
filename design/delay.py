import numpy as np
import matplotlib.pyplot as plt


class CircularBuffer:
    """
    This class implements a circular buffer.

    Attributes
    ----------
    sample_rate (int): the operating sample rate of the buffer
    buf_size (int): The size of the circular buffer
    read_pointer (int): circular buffer reading head
    write_pointer (int): cicular buffer writting head
    buffer (np.ndarray): circular buffer
    """
    def __init__(self, buf_size):
        self.buf_size = buf_size
        self.buffer = np.zeros(self.buf_size)
        self.read_pointer = 0
        self.write_pointer = 0

    def reset(self):
        """
        Resets the circular buffer pointers and re-initialize the
        buffer to 0s.
        """
        self.read_pointer = 0
        self.write_pointer = 0
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
        self.write_pointer += 1 
        self.write_pointer %= self.buf_size

    def read_sample(self):
        """
        Reads a sample from the delay line. and updates the
        read pointer.

        return
        ------
        y (float): The output sample.
        """
        y = self.buffer[self.read_pointer]
        self.read_pointer += 1 
        self.read_pointer %= self.buf_size
        return y

    def set_read_pointer(self, read_pointer):
        """
        Sets the read pointer to a chosen value.
        """
        if (read_pointer > self.buf_size) or (read_pointer < 0):
            raise ValueError("Value of the chosen read pointer is out of the buffer.")
        self.read_pointer = read_pointer
    
    def get_buffer_size(self):
        """
        Returns the size of the circular buffer
        """
        return self.buf_size

    def get_write_pointer(self):
        """
        Getter for the write pointer value
        
        returns
        -------
        write_pointer (int): value of the write pointer.
        """
        return self.write_pointer


class Delay:
    """
    This class implements an audio delay.

    Attributes
    ---------
    sample_rate (int): Sampling rate in Hz.

    circular_buffer (circularBuffer): Circular buffer used for the delay.
    """

    MAX_DELAY_TIME_S = 3

    def __init__(self, sample_rate, delay_time_s):
        """
        class constructor.

        Arguments
        ---------
        sample_rate (int): Sample rate of the delay.

        delay_time_s (float): delay time in seconds.
        """
        self.sample_rate = sample_rate
        self.circular_buffer = CircularBuffer(int(self.MAX_DELAY_TIME_S * sample_rate))
        self.set_delay(delay_time_s)

    def set_delay(self, delay):
        """
        Sets the delay value by moving the read pointer
        to the proper location

        Params
        -------
        delay (float) the delay lenght in seconds
        """
        delay_in_samples = int(delay * self.sample_rate)

        read_pointer = self.circular_buffer.get_write_pointer() - delay_in_samples
        if read_pointer < 0:
            read_pointer += self.circular_buffer.get_buffer_size()

        self.circular_buffer.set_read_pointer(read_pointer)

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
        y = self.circular_buffer.read_sample()
        self.circular_buffer.write_sample(x)

        return y


if __name__== "__main__":
    sample_rate = 44100
    delay_time_s = 0.5
    num_samples = int(sample_rate * 3 * delay_time_s)

    in_signal = np.zeros(num_samples)
    in_signal[0] = 1

    out_signal = np.zeros(num_samples)

    dut = Delay(sample_rate, delay_time_s)

    for i, sample in enumerate(in_signal):
        out_signal[i] = dut.process(sample)

    time = np.arange(num_samples) / sample_rate

    plt.figure(figsize=(10, 6))
    plt.plot(time, in_signal)
    plt.plot(time, out_signal)
    plt.show()
