#!/bin/bash
docker build --platform=linux/amd64 -o module_api/API -f dockerfile.export ./lib/file-lock && \
python3 setup.py bdist_wheel --plat-name=linux_x86_64
docker build --platform=linux/amd64 -o module_api/API -f dockerfile.export ./lib/file-lock && \
python3 setup.py bdist_wheel --plat-name=linux_aarch64

INITIAL_DIR=$(pwd);
cd ./lib/file-lock/build
ninja multiprocessing_file_lock_python
cd $INITIAL_DIR
mv ./lib/file-lock/build/file_lock.so ./module_api/API/file_lock.so
python3 setup.py bdist_wheel --plat-name=macos_14_4_arm64

