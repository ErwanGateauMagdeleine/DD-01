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
#include "circularBuffer.h"
#include "testsCommonVars.h"

TEST_CASE("Buffer Length is a power of two")
{
    auto [maxDelayTime, expected] = GENERATE(table<float, size_t>({
        {1.0f,   65536},
        {0.5f,   32768},
        {0.005f, 256},
        {0.06f,  4096},
    }));

    CircularBuffer<float> cBuf;

    int delayTimeInSamples = static_cast<int>(maxDelayTime * test::kSampleRate);

    cBuf.prepare(test::kSampleRate, delayTimeInSamples);

    CAPTURE(maxDelayTime);
    REQUIRE(cBuf.getBufferLength() == expected);
}

TEST_CASE("Buffer Writing works properly")
{
    CircularBuffer<float> cBuf;
    cBuf.prepare(test::kSampleRate, 1);

    for (unsigned i = 0; i < test::kSampleRate; i++)
    {
       cBuf.writeSample(static_cast<float>(i));
       float out = cBuf.readSample(0);
       REQUIRE(out == static_cast<float>(i));
    }
}

TEST_CASE("Integer delays reads are working properly")
{
    CircularBuffer<float> cBuf;
    cBuf.prepare(test::kSampleRate, test::kSampleRate);
    const int d = GENERATE(0, 1, 2, 10, 100, 500, 998);
    for (unsigned i = 0; i < test::kSampleRate; i++)
    {
       cBuf.writeSample(static_cast<float>(i));
    }

    const float out = cBuf.readSampleInterp(static_cast<float>(d) / test::kSampleRate);

    REQUIRE(out == Catch::Approx(static_cast<float>(test::kSampleRate - 1 - d)).margin(1e-3));
}

TEST_CASE("Fractional delays reads are working properly")
{
    CircularBuffer<float> cBuf;
    cBuf.prepare(test::kSampleRate, test::kSampleRate);
    const float d = GENERATE(0.25f, 0.5f, 0.75f, 1.5f, 10.3f, 100.5f, 500.9f, 997.5f);
    for (unsigned i = 0; i < test::kSampleRate; i++)
    {
       cBuf.writeSample(static_cast<float>(i));
    }

    const float out = cBuf.readSampleInterp(d / test::kSampleRate);

    REQUIRE(out == Catch::Approx(static_cast<float>(test::kSampleRate - 1) - d).margin(1e-3));
}

TEST_CASE("Circular buffer can be reset")
{
    CircularBuffer<float> cBuf;
    cBuf.prepare(test::kSampleRate, test::kSampleRate);

    /* Fill half the buffer */
    for (unsigned i = 0; i < test::kSampleRate / 2; i++)
    {
       cBuf.writeSample(1.0);
    }

    auto writePtr = cBuf.getWritePointer();

    REQUIRE_FALSE(writePtr == 0);

    for (unsigned i = 0; i < test::kSampleRate / 2; i++)
    {
        auto sample = cBuf.readSample(i);
        REQUIRE(sample == 1.0);
    }

    cBuf.reset();

    writePtr = cBuf.getWritePointer();
    REQUIRE(writePtr == 0);

    for (unsigned i = 0; i < test::kSampleRate; i++)
    {
        auto sample = cBuf.readSample(i);
        REQUIRE(sample == 0.0);
    }
}
