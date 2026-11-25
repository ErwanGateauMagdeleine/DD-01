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
import soundfile as sf


def get_file_num_channels(signal):
    """
    Determines the number of channels in the audio signal.

    Parameters:
        signal (numpy.ndarray): The input audio signal.

    Returns:
            int: The number of channels in the audio signal.
    """
    # Determine the number of channels
    if signal.ndim == 1:
        # Mono
        num_channels = 1
    else:
        # Stereo or more
        num_channels = signal.shape[1]

    return num_channels


def get_audio(file_name):
    """
    Reads an audio file and returns the sample rate and signal.

    Parameters:
        file_name (str): Path to the audio file.

    Returns:
        tuple: Sample rate, nummber of channels and audio signal.
    """
    signal, sample_rate= sf.read(file_name, dtype="float32")
    num_channel = get_file_num_channels(signal)

    return np.float64(sample_rate), num_channel, signal


def write_audio_file(sample_rate, audio_data, file_name):
    """
    Writes an audio file with the given data sample rate etc.

    Parameters:
        sample_rate (float): Sample rate of the signal
        num_channels (int): number of channels of the file.
        audio_data (numpy.ndarray): audio data. It must be already interleaved if
                                    the number of channels is > 1.
        file_name (str): name of the file generated.
    """
    sf.write(file_name, audio_data.astype('float32'), int(sample_rate), subtype="FLOAT")
