from conans import ConanFile, CMake
import os

class LibiioTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake_find_package"
    build_requires = "cmake/[>3.0]"
    requires = "libiio/[>=0.1]"

    def build(self):
        cmake = CMake(self, cmake_program=os.path.join(self.deps_cpp_info["cmake"].bin_paths[0], "cmake"))
        cmake.configure()
        cmake.build()

    def test(self):
        bin_path = os.path.join("bin", "example")
        self.run(bin_path, run_environment=True)