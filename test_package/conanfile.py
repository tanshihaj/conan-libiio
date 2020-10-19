from conans import ConanFile, CMake
import os

class LibiioTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake_find_package"
    requires = "libiio/[>=0.1]"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        self.run(".%sexample" % os.path.sep, run_environment=True)