/* DD-01 - Digital delay JUCE based audio plugin
   Copyright (C) 2026 Erwan Gateau-Magdeleine

   This program is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.

   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this program. If not, see <https://www.gnu.org/licenses/>.
*/

#define DR_WAV_IMPLEMENTATION
#include "wavIo.h"
#include "dr_wav.h"
#include <stdexcept>

/** @brief Loads a wav file. 
 * 
 * 
*/
Audio loadWav(const std::string& path)
{
    Audio a;

    unsigned numChannels = 0;
    unsigned sampleRate = 0;
    drwav_uint64 numFrames = 0;

    float* data = drwav_open_file_and_read_pcm_frames_f32(path.c_str(), &numChannels, &sampleRate, &numFrames, nullptr);

    if (!data)
    {
        throw std::runtime_error("Cannot open WAV: " + path);
    }

    a.numChannels = numChannels;
    a.sampleRate = sampleRate;
    a.samples.assign(data, data + numFrames * numChannels);

    drwav_free((void *)data, nullptr);

    return a;
}
