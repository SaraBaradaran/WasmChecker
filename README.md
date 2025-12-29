# WasmChecker
A differential testing framework for checking the semantic equivalence of a C/C++ code in a native binary (e.g., x86-64) and WebAssembly using a test-driven approach.
For more information, see the paper ["Reusing Legacy Code in WebAssembly: Key Challenges of Cross-Compilation and Code Semantics Preservation"](https://arxiv.org/abs/2412.20258).

## Requirements
- Python3
- [Emscripten compiler toolchain](https://emscripten.org)
- [CodeqL analysis engine](https://codeql.github.com)

## Download and Install Emscripten
```
git clone https://github.com/emscripten-core/emsdk.git
cd emsdk
git pull
./emsdk install 3.1.54
./emsdk activate 3.1.54
source ./emsdk_env.sh; cd ..
```
Note: We did the evaluation part using Emscripten version 3.1.54. However, WasmChecker can work with any arbitrary version. 

## Download and Install CodeQL
```
wget https://github.com/github/codeql-action/releases/download/codeql-bundle-v2.17.0/codeql-bundle-linux64.tar.gz
tar -xzf codeql-bundle-linux64.tar.gz 
export PATH=$PATH:/path/to/codeql
codeql resolve qlpacks
```
Note: You can also use WasmChecker without using CodeQL as the static analyzer. In this case, the WasmChecker simply enables the most important flags. This may cause options conflicts and compile-time overhead. Also, the result of differential testing might be less accurate. 

## How to Use WasmChecker
You can use WasmChecker in two ways. If you are going to test a codebase that is already in your system, simply use the following command:
```
python3 WasmChecker.py -p path_to_codebase -t test_flag
```
For example:
```
git clone https://github.com/fmtlib/fmt --recursive
python3 WasmChecker.py -p fmt -t FMT_TEST
```
You can also simply provide WasmChecker with the git url using the following command:
```
python3 WasmChecker.py -u repo_url -t test_flag
```
For example:
```
python3 WasmChecker.py -u https://github.com/taocpp/PEGTL -t PEGTL_BUILD_TESTS
```

## Build and Test Codebases with the Default Settings of Emscripten

```
python3 build-codebases.py compiler(i.e., clang/gcc/emcc)
python3 test-runner.py -p ./emcc-build/fmt
```

## Reproducing The Paper Results
Using the dataset.csv and the script results.py, you can simply reproduce our results.
```
python3 results.py
```

## :lady_beetle: Reported Bugs
This is the list of new bugs we found in Emscripten compiler toolchain by using WasmChecker:
- https://github.com/emscripten-core/emscripten/issues/21382
- https://github.com/emscripten-core/emscripten/issues/21603
- https://github.com/emscripten-core/emscripten/issues/22014
- https://github.com/emscripten-core/emscripten/issues/22259
- https://github.com/emscripten-core/emscripten/issues/21604
- https://github.com/emscripten-core/emscripten/issues/22050
- https://github.com/emscripten-core/emscripten/issues/22040
- https://github.com/emscripten-core/emscripten/issues/22033
- https://github.com/emscripten-core/emscripten/issues/22030
- https://github.com/emscripten-core/emscripten/issues/22202
- !https://github.com/emscripten-core/emscripten/pull/21193

## :mailbox_with_mail: Feedback

If you have any suggestions or found a bug, please contact us at sbaradar@usc.edu.
