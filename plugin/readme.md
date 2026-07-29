# Plugin

This folder gathers the sources to build a plugin. It is a vst3 plugin that is based on the JUCE framework.

## Generating the IDE project

To generate a project for your IDE, one can run the following command in the root of the repository:
```
cmake -B build -S plugin -G <your_IDE_generator>
```
You can find the list of available IDE generators [here](https://cmake.org/cmake/help/latest/manual/cmake-generators.7.html).

## Build the plugin
Once you have generated your IDE project, you can from the command line build the plugin running the following command in the root of the repository:

```
cmake --build build --target AW-01_VST3 --config Release
```

Once the build is finished, the built plugin `.vst3` is automatically moved to the OUT folder.

## References

In order to build the vst project, the following references were used:
* [pamplejuce](https://github.com/sudara/pamplejuce)
* [JUCE CMake API](https://github.com/juce-framework/JUCE/blob/master/docs/CMake%20API.md)
* [JUCECmakeRepoPrototype](https://github.com/eyalamirmusic/JUCECmakeRepoPrototype)
