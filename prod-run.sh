#!/bin/bash
neu build
export WEBKIT_DISABLE_DMABUF_RENDERER=1
./dist/ext-python/ext-python-linux_x64 --debug