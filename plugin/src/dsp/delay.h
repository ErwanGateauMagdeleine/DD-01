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
        revDelayPhase = static_cast<SampleType>(0.0);
        revDelayPhaseInc = static_cast<SampleType>(0.0);
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
        revDelayPhaseInc = static_cast<SampleType>(1.0 / (delayTime * sampleRate));
    }

    void prepare(double newSampleRate, double maxDelayTimeInSec)
    {
        sampleRate = newSampleRate;

        int delayBufSz = static_cast<int>(newSampleRate * maxDelayTimeInSec);
        int revDelayBufSz =  static_cast<int>((2 * newSampleRate * maxDelayTimeInSec) + 2);

        straightDelayBuf.prepare(newSampleRate, delayBufSz);

        revBuf.prepare(newSampleRate, revDelayBufSz);
        revDelayBuf.prepare(newSampleRate, delayBufSz);

        halfDelayBuf.prepare(newSampleRate, revDelayBufSz);
    }

    void reset()
    {
        straightDelayBuf.reset();
    }

    SampleType process(SampleType x)
    {
        auto y_straight = straightDelayBuf.readSampleInterp(delayTime);
        straightDelayBuf.writeSample(x + feedback * y_straight);

        auto rev_delay = 2 * delayTime * revDelayPhase;
        auto rev_gain = 4 * revDelayPhase * (1 - revDelayPhase);

        revDelayPhase += revDelayPhaseInc;
        if (revDelayPhase >= 1)
        {
            revDelayPhase -= static_cast<SampleType>(1.0);
        }

        auto pureRev = rev_gain * revBuf.readSampleInterp(rev_delay);
        auto pureRevDelayed = revDelayBuf.readSampleInterp(delayTime);
        auto pureRevSum = pureRev + pureRevDelayed;
        revBuf.writeSample(x);
        revDelayBuf.writeSample(feedback * pureRevSum);

        auto halfRev = rev_gain * halfDelayBuf.readSampleInterp(rev_delay);
        halfDelayBuf.writeSample(x + feedback * halfRev);

        switch (type)
        {
            case delayType::HALF_REVERSED:
                return halfRev;
            case delayType::REVERSED:
                return pureRevSum;
            default:
                return y_straight;
        }
    }

    SampleType getRevDelayPhaseIncrement()
    {
        return revDelayPhaseInc;
    }
private:
    double sampleRate;

    CircularBuffer<SampleType> straightDelayBuf;

    CircularBuffer<SampleType> revBuf;
    CircularBuffer<SampleType> revDelayBuf;

    CircularBuffer<SampleType> halfDelayBuf;

    delayType type;
    SampleType feedback;
    SampleType delayTime;

    SampleType revDelayPhase;
    SampleType revDelayPhaseInc;
};
