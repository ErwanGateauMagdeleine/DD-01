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

import argparse
from delay import Delay
from utils import get_audio, write_audio_file
import numpy as np


def parse_param():
    """
    Parses command line arguments.

    Returns:
        argparse.Namespace: Parsed command line arguments.
    """
    parser = argparse.ArgumentParser(description="delay test script")

    parser.add_argument('--feedback', type=float, required=True, help="Delay feedback")
    parser.add_argument('--time', type=float, required=True, help="delay time in seconds.")
    parser.add_argument('--type', choices=["straight", "half-rev", "rev"], required=True, help="Selects the delay type.")
    parser.add_argument('--in-file', type=str, default="design/audio_files/one-time-piano.wav",
                        help="Audio file to use to test the delay")
    parser.add_argument('--out-file', type=str, default="design/audio_files/one-time-piano-processed.wav",
                            help="Audio file to use to test the delay")

    return parser.parse_args()


if __name__== "__main__":
    args = parse_param()

    sample_rate, num_channels, signal = get_audio(args.in_file)
    if num_channels > 1:
            signal = signal[:, 0]
    signal = np.pad(signal, (0, int(len(signal) + 3 * sample_rate)))

    out_signal = np.zeros(len(signal))

    dut = Delay(sample_rate, args.time, args.feedback, 1, args.type)

    for i, sample in enumerate(signal):
            out_signal[i] = dut.process(sample)

    write_audio_file(sample_rate, out_signal, args.out_file)
