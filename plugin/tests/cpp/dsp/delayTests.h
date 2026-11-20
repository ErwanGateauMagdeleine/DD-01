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
#include "delay.h"
#include "testsCommonVars.h"
#include <catch2/matchers/catch_matchers_floating_point.hpp>
#include "wavIo.h"
#include <string.h>

TEST_CASE("Straigth delay feedback works properly")
{
    auto dut = delay<float>();
    std::vector<float> outBuf;

    int testDurationSamples = static_cast<int>(test::kSampleRate * test::kTestTimeSeconds);
    outBuf.assign(testDurationSamples, 0);

    float delayTime = GENERATE(1.0, 0.5, 1.5, 0.25, 0.75);

    int delayTimeSample = static_cast<int>(delayTime * test::kSampleRate);

    dut.prepare(test::kSampleRate, test::kMaxDelayTime);
    dut.setDelayType(delay<float>::delayType::STRAIGHT);
    dut.setFeedback(1.0f);
    dut.setDelayTime(delayTime);

    outBuf[0] = dut.process(1.0f);
    for (int i = 1; i < testDurationSamples; i++)
    {
        outBuf[i] = dut.process(0.0f);
    }

    REQUIRE(outBuf[0] == 0.0f);
    for (int i = 1; i < testDurationSamples; i++)
    {
        if ((i % (delayTimeSample + 1))== 0)
        {
            REQUIRE(outBuf[i] != 0.0f);
        }
        else
        {
            REQUIRE(outBuf[i] == 0.0f);
        }
    }
}

TEST_CASE("Straigth delay feedback decays properly")
{
    auto dut = delay<float>();
    std::vector<float> outBuf;
    float amplitude = 1.0f;
    float feedback = 0.5f;

    int testDurationSamples = static_cast<int>(test::kSampleRate * test::kTestTimeSeconds);
    outBuf.assign(testDurationSamples, 0);

    float delayTime = GENERATE(1.0, 0.5, 1.5, 0.25, 0.75);

    int delayTimeSample = static_cast<int>(delayTime * test::kSampleRate);

    dut.prepare(test::kSampleRate, test::kMaxDelayTime);
    dut.setDelayType(delay<float>::delayType::STRAIGHT);
    dut.setFeedback(feedback);
    dut.setDelayTime(delayTime);

    outBuf[0] = dut.process(amplitude);
    for (int i = 1; i < testDurationSamples; i++)
    {
        outBuf[i] = dut.process(0.0f);
    }

    REQUIRE(outBuf[0] == 0.0f);
    for (int i = 1; i < testDurationSamples; i++)
    {
        if ((i % (delayTimeSample + 1))== 0)
        {
            REQUIRE_THAT(outBuf[i], Catch::Matchers::WithinRel(amplitude));
            amplitude *= feedback;
        }
        else
        {
            REQUIRE(outBuf[i] == 0.0f);
        }
    }
}

TEST_CASE("Reversed delay phase increment is the inverse of the delay time")
{
    auto dut = delay<float>();

    float d = GENERATE(1.0, 0.5, 1.5, 0.25, 0.75, 0.35, 0.786);

    dut.prepare(test::kSampleRate, test::kMaxDelayTime);
    dut.setDelayTime(d);

    float expected = 1.0f / (d * test::kSampleRate);

    float phaseInc = dut.getRevDelayPhaseIncrement();
    REQUIRE_THAT(phaseInc, Catch::Matchers::WithinRel(expected));
}

TEST_CASE("Reversed delay is working properly")
{
    auto dut = delay<float>();
    float feedback = 0.25f; /* Regenerate expected file if changed */
    float delayTime = 0.3f; /* Regenerate expected file if changed */

    const std::string dir = AUDIO_DIR;

    Audio expectedOut = loadWav(dir + "/one-time-piano-processed-rev.wav");
    Audio inSignal = loadWav(dir + "/one-time-piano.wav");

    REQUIRE(expectedOut.numChannels == inSignal.numChannels);
    REQUIRE(expectedOut.sampleRate == inSignal.sampleRate);
    REQUIRE(expectedOut.getNumFrames() >= inSignal.getNumFrames());

    dut.prepare(test::kSampleRate, test::kMaxDelayTime);
    dut.setDelayType(delay<float>::delayType::REVERSED);
    dut.setFeedback(feedback);
    dut.setDelayTime(delayTime);

    for(int i = 0; i < expectedOut.getNumFrames(); i++)
    {
        float inData;
        if (i < inSignal.getNumFrames())
        {
            inData = inSignal.samples[i];
        }
        else
        {
            inData = 0.0f;
        }

        INFO("index under process: i = " << i);
        REQUIRE_THAT(dut.process(inData), Catch::Matchers::WithinRel(expectedOut.samples[i]));
    }
}
