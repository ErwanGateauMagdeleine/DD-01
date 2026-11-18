# DD-01 - Digital delay JUCE based audio plugin
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

add_executable(dspTests 
    main.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/CircularBufferTests.h)

target_compile_features(dspTests PRIVATE cxx_std_20)

target_link_libraries(dspTests
    PRIVATE
        Catch2::Catch2WithMain
)

target_include_directories(dspTests
    PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}/../../../src/dsp/
)

set_property(TARGET dspTests PROPERTY COMPILE_WARNING_AS_ERROR ON)

add_test(NAME DSP_TESTS COMMAND dspTests)
