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

#include "circularBuffer.h"

template <typename SampleType>
class delay
{
public:
    /** Enumeration for the delay type. */
    enum delayType
    {
        STRAIGHT,
        HALF_REVERSED,
        REVERSED
    };

    delay()
    {
        type = delayType::STRAIGHT;
    }

    void setDelayType(delayType newDelayType)
    {
        type = newDelayType;
    }

    void setFeedback(SampleType newFeedback)
    {
        feedback = newFeedback;
    }

    void setDelayTime(SampleType newDelayTime)
    {
        delayTime = newDelayTime;
    }

    void prepare(double newSampleRate, double maxDelayTimeInSec)
    {
        sampleRate = newSampleRate;

        int delayBufSz = static_cast<int>(newSampleRate * maxDelayTimeInSec);

        straightDelayBuf.prepare(newSampleRate, delayBufSz);
    }

    void reset()
    {
        straightDelayBuf.reset();
    }

    SampleType process(SampleType x)
    {
        auto y = straightDelayBuf.readSampleInterp(delayTime);
        straightDelayBuf.writeSample(x + feedback * y);

        return y;
    }

private:
    double sampleRate;

    CircularBuffer<SampleType> straightDelayBuf;

    delayType type;
    SampleType feedback;
    SampleType delayTime;
};
