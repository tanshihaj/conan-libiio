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
        bin_path = os.path.join("bin", "example")
        self.run(bin_path, run_environment=True)