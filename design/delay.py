# DD-01 - AutoWah JUCE based audio plugin
# Copyright (C) 2026 Erwan Gateau-Magdeleine
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program. If not, see <https://www.gnu.org/licenses/>.

import numpy as np
import matplotlib.pyplot as plt
import math
import argparse
from utils import get_audio
import sounddevice as sd


def parse_param():
    """
    Parses command line arguments.

    Returns:
        argparse.Namespace: Parsed command line arguments.
    """
    parser = argparse.ArgumentParser(description="delay test script")

    parser.add_argument('--feedback', type=float, required=True, help="Delay feedback")
    parser.add_argument('--dry-wet', type=float, required=True, help="Delay dry / wet")
    parser.add_argument('--time', type=float, required=True, help="delay time in seconds.")
    parser.add_argument('--type', choices=["straight", "half-rev", "rev"], required=True, help="Selects the delay type.")
    parser.add_argument('--audio-file', type=str, default="design/audio_files/piano_loop.wav",
                        help="Audio file to use to test the delay")

    return parser.parse_args()


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

    reversed_circular_buffer (circularBuffer): Circular buffer for the reverse algo.

    feedback (float): feedback amount (in the range [0, 1])
    """

    MAX_DELAY_TIME_S = 3

    def __init__(self, sample_rate, delay_time_s, feedback, dry_wet, delay_type):
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
        self.reversed_circular_buffer = CircularBuffer(int(2 * self.MAX_DELAY_TIME_S * sample_rate) + 2)
        self.feedback = feedback
        self.dry_wet = dry_wet

        self.delay_in_samples = delay_time_s * self.sample_rate

        self.delay_type = delay_type
        self.phase = 0.0

    def _process_straight(self, x):
        """
        Processes a signal through the straight delay.

        Arguments
        ---------
        x (float): delay input.

        returns
        -------
        y: delay output.
        """
        y = self.circular_buffer.read_sample(self.delay_in_samples)

        self.circular_buffer.write_sample(x + self.feedback * y)

        return y

    def _process_half_reversed_gain_smoothing(self, x):
        """
        Processes a signal through the half reversed delay.

        Arguments
        ---------
        x (float): delay input.

        returns
        -------
        y: delay output.
        """
        delay = 2 * self.delay_in_samples * self.phase
        delay_ratio = delay / (2 * self.delay_in_samples)
        gain = 4 * (delay_ratio) * (1 - delay_ratio)

        self.phase += 1 / self.delay_in_samples
        self.phase %= 1

        y = gain * self.reversed_circular_buffer.read_sample(delay)

        self.reversed_circular_buffer.write_sample(x + self.feedback * y)

        return y

    def _process_reversed_gain_smoothing(self, x):
        """
        Processes a signal through the reversed delay.

        Arguments
        ---------
        x (float): delay input.

        returns
        -------
        y: delay output.
        """
        delay = 2 * self.delay_in_samples * self.phase
        delay_ratio = delay / (2 * self.delay_in_samples)
        gain = 4 * (delay_ratio) * (1 - delay_ratio)

        self.phase += 1 / self.delay_in_samples
        self.phase %= 1

        y_delay = gain * self.reversed_circular_buffer.read_sample(delay)
        y_rev_delay = self.circular_buffer.read_sample(self.delay_in_samples)
        y_sum = y_delay + y_rev_delay

        self.reversed_circular_buffer.write_sample(x)
        self.circular_buffer.write_sample(self.feedback * y_sum)

        return y_sum

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
        if self.delay_type == "straight":
            y = self._process_straight(x)
        elif self.delay_type == "half-rev":
            y = self._process_half_reversed_gain_smoothing(x)
        else:
            y = self._process_reversed_gain_smoothing(x)

        return self.dry_wet * y + (1 - self.dry_wet) * x


if __name__== "__main__":

    args = parse_param()
    feedback = args.feedback
    dry_wet = args.dry_wet
    rev = args.reversed
    delay_time_s = args.time


    sample_rate, num_channels, channels_data = get_audio(args.audio_file)

    if num_channels > 1:
        # Extract the first channel if the signal is stereo
        signal = channels_data[:, 0]
        num_samples = len(signal)

    out_signal = np.zeros(num_samples)

    dut = Delay(sample_rate, delay_time_s, feedback, dry_wet, rev)

    for i, sample in enumerate(signal):
        out_signal[i] = dut.process(sample)

    # Play the audio
    sd.play(out_signal, samplerate=sample_rate)
    sd.wait()
