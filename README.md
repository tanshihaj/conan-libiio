[![Build Status Travis](https://travis-ci.com/tanshihaj/conan-libiio.svg?branch=main)](https://travis-ci.com/tanshihaj/conan-libiio)

## Conan package recipe for [libiio](http://analogdevicesinc.github.io/libiio)

## How use recipe

1. Add bintray remote to the [conan](https://docs.conan.io) remotes:
    ```
    conan remote add libiio_remote https://api.bintray.com/conan/tanshihaj/main
    ```
2. Use it in conan recipes or install it from command line:

   - inside `conanfile.py`:
        ```
        class MyFancyProgram(ConanFile):
            ...
            requires = ["libiio/0.16@tanshihaj/stable"]
        ```    

   - using command line:

        ```
        conan install libiio/0.16@tanshihaj/stable --build=libiio
        ```
