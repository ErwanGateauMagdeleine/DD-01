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

#define MAX_DELAY_TIME_S (2)
#define TESTS_TIME_S (4 * MAX_DELAY_TIME_S)

TEST_CASE("Straigth delay feedback works properly")
{
    auto dut = delay<float>();
    std::vector<float> outBuf;

    int testDurationSamples = static_cast<int>(SAMPLE_RATE * TESTS_TIME_S);
    outBuf.assign(testDurationSamples, 0);

    float delayTime = GENERATE(1.0, 0.5, 1.5, 0.25, 0.75);

    int delayTimeSample = static_cast<int>(delayTime * SAMPLE_RATE);

    dut.prepare(SAMPLE_RATE, MAX_DELAY_TIME_S);
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

    int testDurationSamples = static_cast<int>(SAMPLE_RATE * TESTS_TIME_S);
    outBuf.assign(testDurationSamples, 0);

    float delayTime = GENERATE(1.0, 0.5, 1.5, 0.25, 0.75);

    int delayTimeSample = static_cast<int>(delayTime * SAMPLE_RATE);

    dut.prepare(SAMPLE_RATE, MAX_DELAY_TIME_S);
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
