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

#pragma once
#include <vector>
#include <cmath>

template <typename SampleType>
class CircularBuffer
{
public:
    CircularBuffer()
    {
        writePointer = 0;
        wrapingMask = 0;
    }

    void prepare(double newSampleRate, int bufSz)
    {
        size_t bufSzPow2 = nextPowerOfTwo(bufSz);
        buffer.assign(bufSzPow2, 0);
        writePointer = 0;
        wrapingMask = static_cast<unsigned>(bufSzPow2) - 1;
        sampleRate = newSampleRate;
    }

    void writeSample(SampleType sample)
    {
        buffer[writePointer] = sample;
        writePointer = (writePointer + 1) & wrapingMask;
    }

    SampleType readSampleInterp(float delay)
    {
        float delaySamples = static_cast<float>(sampleRate) * delay;
        unsigned dInt = static_cast<unsigned>(delaySamples);
        float fract = delaySamples - static_cast<float>(dInt);

        SampleType y1 = readSample(static_cast<int>(dInt));
        SampleType y2 = readSample(static_cast<int>(dInt) + 1);

        return (fract * y2) + ((1- fract) * y1);
    }

    SampleType readSample(unsigned delay)
    {
        /* -1 as we read before we write. */
        unsigned readPointer = (writePointer - 1) - delay;
        readPointer &= wrapingMask;

        return buffer[readPointer];
    }

    size_t getBufferLength()
    {
        return static_cast<size_t>(buffer.size());
    }

private:

    size_t nextPowerOfTwo(size_t n)
    {
        return pow(2, ceil(log(n) / log(2)));
    }

    unsigned writePointer;
    unsigned wrapingMask;
    std::vector<SampleType> buffer;
    double sampleRate;
};
