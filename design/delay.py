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
    parser.add_argument('--audio-file', type=str, default="design/audio_files/one-time-piano.wav",
                        help="Audio file to use to test the delay")
    parser.add_argument('--display', action='store_true', help="Display the signal instead of playing it.")

    return parser.parse_args()


class CircularBuffer:
    """
    This class implements a circular buffer. The size of the buffer will be the nearest
    power of two to the requested size.

    Parameters
    ----------
    buf_size (int): The size of the circular buffer

    sample_rate (np.float64): Operating sample rate

    dtype: The buffer content ndtype.
    """
    def __init__(self, buf_size, sample_rate, dtype=np.float32):
        self.buf_size = int(math.pow(2, math.ceil(math.log(buf_size) / math.log(2))))
        self.buffer = np.zeros(self.buf_size, dtype=dtype)
        self.wraping_mask = self.buf_size - 1
        self.write_pointer = 0
        self.sample_rate = np.float64(sample_rate)

    def write_sample(self, x):
        """
        Writes an input sample into the circular buffer and advances the
        write pointer.

        Params
        ------
        x (np.float32): input sample
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
        y (np.float32): The output sample.
        """
        # - 1 as we read before we write.
        read_pointer = (self.write_pointer - 1) - int(delay)
        read_pointer &= self.wraping_mask

        return self.buffer[read_pointer]

    def read_sample(self, delay):
        """
        Read a sample with an interpolation.

        Params
        ------
        delay (np.float32): The delay to be applied in seconds

        return
        ------
        y (np.float32) The output delayed with interpolation.
        """
        delay_in_samples = np.float32(self.sample_rate * delay)
        integer_delay = int(delay_in_samples)

        y1 = self._read_sample(integer_delay)
        y2 = self._read_sample(integer_delay + 1)

        fraction = delay_in_samples - np.float32(integer_delay)

        return (fraction * y2) + (1.0 - fraction) * y1


class Delay:
    """
    This class implements an audio delay.

    Attributes
    ---------
    sample_rate (np.float64): Sampling rate in Hz.

    circular_buffer (circularBuffer): Circular buffer used for the delay.

    reversed_circular_buffer (circularBuffer): Circular buffer for the reverse algo.

    feedback (np.float32): feedback amount (in the range [0, 1])
    """

    MAX_DELAY_TIME_S = np.float32(3.0)

    def __init__(self, sample_rate, delay_time_s, feedback, dry_wet, delay_type):
        """
        class constructor.

        Arguments
        ---------
        sample_rate (np.float64): Sample rate of the delay.

        delay_time_s (np.float32): delay time in seconds.

        feedback (np.float32): feedback amount (in the range [0, 1])

        dry_wet (np.float32): dry / wet amount (in the range [0, 1] 0 being fully
                              dry, 1 being completely wet).
        """
        self.sample_rate = np.float64(sample_rate)
        self.circular_buffer = CircularBuffer(int(self.MAX_DELAY_TIME_S * self.sample_rate), self.sample_rate)
        self.reversed_circular_buffer = CircularBuffer(int(2 * self.MAX_DELAY_TIME_S * self.sample_rate) + 2, self.sample_rate)
        self.feedback = np.float32(feedback)
        self.dry_wet = np.float32(dry_wet)
        self.delay_time_s = np.float32(delay_time_s)

        self.delay_type = delay_type
        self.phase = np.float32(0.0)

    def _process_straight(self, x):
        """
        Processes a signal through the straight delay.

        Arguments
        ---------
        x (np.float32): delay input.

        returns
        -------
        y: delay output.
        """
        y = self.circular_buffer.read_sample(self.delay_time_s)

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
        delay = np.float32(2 * self.delay_time_s * self.phase)
        gain = np.float32(4 * (self.phase) * (1 - self.phase))

        self.phase += np.float32(1 / (self.delay_time_s * self.sample_rate))
        self.phase %= 1

        y = gain * self.reversed_circular_buffer.read_sample(delay)

        self.reversed_circular_buffer.write_sample(x + self.feedback * y)

        return y

    def _process_reversed_gain_smoothing(self, x):
        """
        Processes a signal through the reversed delay.

        Arguments
        ---------
        x (np.float32): delay input.

        returns
        -------
        y: delay output.
        """
        delay = np.float32(2 * self.delay_time_s * self.phase)
        gain = np.float32(4 * (self.phase) * (1 - self.phase))

        self.phase += np.float32(1 / (self.delay_time_s * self.sample_rate))
        self.phase %= 1

        y_delay = gain * self.reversed_circular_buffer.read_sample(delay)
        y_rev_delay = self.circular_buffer.read_sample(self.delay_time_s)
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
    delay_type = args.type
    delay_time_s = args.time

    sample_rate, num_channels, channels_data = get_audio(args.audio_file)

    if num_channels > 1:
        # Extract the first channel if the signal is stereo
        signal = channels_data[:, 0]
    else:
        signal = channels_data

    if args.display:
        # Add 0 padding after the signal to see all repetitions when feedback is
        signal = np.pad(signal, (0, int(len(signal) + 3 * sample_rate)))
        num_samples  = len(signal)

    out_signal = np.zeros(num_samples, dtype=np.float32)

    dut = Delay(sample_rate, delay_time_s, feedback, dry_wet, delay_type)

    for i, sample in enumerate(signal):
        out_signal[i] = dut.process(sample)

    if args.display:
        time = np.arange(num_samples) / sample_rate
        plt.figure(figsize=(10, 6))
        plt.plot(time, signal)
        plt.plot(time, out_signal)
        plt.show()
    else:
        # Play the audio
        sd.play(out_signal, samplerate=sample_rate)
        sd.wait()
