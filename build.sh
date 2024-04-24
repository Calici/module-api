#!/bin/bash
for VERSION in {7..11}; do
  docker build \
  --platform=linux/amd64 \
  -o dist \
  -f dockerfile.export \
  --build-arg "PYTHON_VERSION=3.$VERSION" \
  . &&
  docker build \
  --platform=linux/arm64 \
  -o dist \
  -f dockerfile.export \
  --build-arg "PYTHON_VERSION=3.$VERSION" \
  .
done

# INITIAL_DIR=$(pwd);
# cd ./lib/file-lock/build
# ninja multiprocessing_file_lock_python
# cd $INITIAL_DIR
# mv ./lib/file-lock/build/file_lock.so ./module_api/API/file_lock.so
# python3 setup.py bdist_wheel --plat-name=macos_14_4_arm64

