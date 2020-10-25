from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import shutil
import os

class LibiioConan(ConanFile):
    name = "libiio"
    version = "0.16"
    license = "https://github.com/analogdevicesinc/libiio/blob/master/COPYING.txt"
    url = "http://analogdevicesinc.github.io/libiio"
    description = "A cross platform library for interfacing with local and remote Linux IIO devices"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "framework": [True, False],
        "local_backend": [True, False],
        "local_config": [True, False],
        "network_backend": [True, False],
        "usb_backend": [True, False],
        "serial_backend": [True, False],
        "xml_backend": [True, False],
        "iio_daemon": [True, False],
        "use_aio": [True, False],
        "iio_daemon_usb": [True, False],
        "ipv6": [True, False],
        "documentation": [True, False],
        "python_bindings": [True, False],
    }
    default_options = {
        "shared": True,
        "framework": True,
        "local_backend": False,         # optional librt, required linux
        "local_config": False,          # required local_backend, required libini
        "network_backend": False,       # optional AVAHI_CLIENT_LIBRARIES AVAHI_COMMON_LIBRARIES, required libxml2, required xml_backend, optional pthreads
        "usb_backend": False,           # required libusb-1.0, required libxml2, required xml_backend, optional pthreads
        "serial_backend": False,        # required serialport >= 0.1.1, optional pthreads, required xml_backend, required libxml2
        "xml_backend": False,           # required libxml2
        "iio_daemon": False,            # required local_backend, required pthreads, required linux
        "use_aio": False,               # required iio_daemon, required libaio
        "iio_daemon_usb": False,        # required use_aio
        "ipv6": True,
        "documentation": False,         # required doxygen
        "python_bindings": False,
    }
    build_requires = "cmake/[>3.0]"
    generators = "cmake_find_package"
    no_copy_source = True

    def configure(self):
        if self.options.local_backend:
            if self.settings.os != "Linux":
                raise ConanInvalidConfiguration("'local_backend' option works only on Linux")

        if self.options.local_config:
            if not self.options.local_backend:
                raise ConanInvalidConfiguration("'local_config' option requires 'local_backend' option")

        if self.options.network_backend:
            if not self.options.xml_backend:
                raise ConanInvalidConfiguration("'network_backend' option requires 'xml_backend' option")

        if self.options.usb_backend:
            if not self.options.xml_backend:
                raise ConanInvalidConfiguration("'usb_backend' option requires 'xml_backend' option")

        if self.options.serial_backend:
            if not self.options.xml_backend:
                raise ConanInvalidConfiguration("'serial_backend' option requires 'xml_backend' option")
            if self.settings.os != "Linux":
                # todo: maybe it is possible to run it in macOS/Windows, I don't know, need to try install libserial to this platforms
                raise ConanInvalidConfiguration("'serial_backend' option works only on Linux")

        if self.options.iio_daemon:
            if not self.options.local_backend:
                raise ConanInvalidConfiguration("'iio_daemon' option requires 'local_backend' option")
            if self.settings.os != "Linux":
                # todo: maybe it is possible to run it in macOS/Windows, I don't know, need to try install libaio to this platforms
                raise ConanInvalidConfiguration("'iio_daemon' option works only on Linux")

        if self.options.use_aio:
            if not self.options.iio_daemon:
                raise ConanInvalidConfiguration("'use_aio' option requires 'iio_daemon' option")

        if self.options.iio_daemon_usb:
            if not self.options.use_aio:
                raise ConanInvalidConfiguration("'iio_daemon_usb' option requires 'use_aio' option")

    def system_requirements(self):
        pack_name = []
        if self.options.use_aio:
            if tools.os_info.is_linux:
                # todo: it will be better to package libaio to the conan and use recepie
                pack_name += ["libaio-dev"]
        if self.options.serial_backend:
            if tools.os_info.is_linux:
                # todo: it will be better to package libserialport to the conan and use recepie
                pack_name += ["libserialport-dev"]
                # todo: other distros
        
        if pack_name:
            installer = tools.SystemPackageTool()
            installer.install(pack_name)

    def requirements(self):
        if self.options.local_config:
            self.requires("libini/[>=0.1]@tanshihaj/stable")
        if self.options.network_backend:
            self.requires("libxml2/[>=2.0]")  # not sure about version?
        if self.options.usb_backend:
            self.requires("libusb/[>=1.0]")   # not sure about version?
            self.requires("libxml2/[>=2.0]")  # not sure about version?
        if self.options.serial_backend:
            self.requires("libxml2/[>=2.0]")  # not sure about version?
        if self.options.xml_backend:
            self.requires("libxml2/[>=2.0]")  # not sure about version?
        if self.options.documentation:
            self.requires("doxygen_installer/[>1.0]@bincrafters/stable")  # not sure about version?

    def source(self):
        tools.get("https://github.com/analogdevicesinc/libiio/archive/v%s.tar.gz" % (self.version))
        for filename in os.listdir("libiio-%s/" % self.version):
            shutil.move(os.path.join("libiio-%s/" % self.version, filename), ".")
        os.rmdir("libiio-%s/" % self.version)

        if self.options.framework:
            tools.replace_in_file(
                "CMakeLists.txt",
                "FRAMEWORK DESTINATION /Library/Frameworks",
                "FRAMEWORK DESTINATION ${CMAKE_INSTALL_PREFIX}/Frameworks"
            )
        else:
            tools.replace_in_file(
                "CMakeLists.txt",
                "FRAMEWORK TRUE",
                ""
            )
            tools.replace_in_file(
                "CMakeLists.txt",
                "FRAMEWORK DESTINATION /Library/Frameworks",
                ""
            )

        if not self.options.shared and self.settings.compiler == "Visual Studio":
            tools.replace_in_file(
                "iio.h",
                "#   ifdef LIBIIO_EXPORTS",
                "#   ifdef LIBIIO_STATIC\n#   define __api\n#   elif LIBIIO_EXPORTS"
            )

        if any('libxml2' in r for r in self.requires):
            tools.replace_in_file(
                "CMakeLists.txt",
                "LIBXML2_VERSION_STRING",
                "LIBXML2_VERSION"
            )
            tools.replace_in_file(
                "CMakeLists.txt",
                "LIBXML2_",
                "LibXml2_"
            )

        if any('libini' in r for r in self.requires):
            tools.replace_in_file(
                "CMakeLists.txt",
                "find_library(LIBINI_LIBRARIES ini)\n		find_path(LIBINI_INCLUDE_DIR ini.h)",
                "find_package(libini)",
            )
            tools.replace_in_file(
                "CMakeLists.txt",
                "LIBINI_",
                "libini_"
            )
            

        if any('libusb' in r for r in self.requires):
            tools.replace_in_file(
                "CMakeLists.txt",
                "find_library(LIBUSB_LIBRARIES usb-1.0)",
                "find_package(libusb)"
            )
            tools.replace_in_file(
                "CMakeLists.txt",
                "find_path(LIBUSB_INCLUDE_DIR libusb-1.0/libusb.h)",
                ""
            )
            # tools.replace_in_file(
            #     "CMakeLists.txt",
            #     "set(CMAKE_REQUIRED_LIBRARIES ${CMAKE_REQUIRED_LIBRARIES}\n			 ${LIBUSB_LIBRARIES})",
            #     "set(CMAKE_REQUIRED_INCLUDES ${CMAKE_REQUIRED_INCLUDES}\n			 ${LIBUSB_INCLUDE_DIR})",
            # )
            tools.replace_in_file(
                "CMakeLists.txt",
                "LIBUSB_LIBRARIES",
                "libusb_LIBRARIES"
            )
            tools.replace_in_file(
                "CMakeLists.txt",
                "LIBUSB_INCLUDE_DIR",
                "libusb_INCLUDE_DIR"
            )
        
        if self.options.python_bindings:
            tools.replace_in_file(
                "bindings/python/CMakeLists.txt",
                "include(FindPythonInterp)",
                "find_package(Python3)"
            )
            tools.replace_in_file(
                "bindings/python/CMakeLists.txt",
                "PYTHONINTERP_FOUND",
                "Python3_Interpreter_FOUND"
            )
            tools.replace_in_file(
                "bindings/python/CMakeLists.txt",
                "PYTHON_EXECUTABLE",
                "Python3_EXECUTABLE"
            )

    def configure_cmake(self):
        cmake = CMake(self, cmake_program=os.path.join(self.deps_cpp_info["cmake"].bin_paths[0], "cmake"))

        cmake.definitions["OSX_PACKAGE"] = "OFF"
        cmake.definitions["ENABLE_PACKAGING"] = "OFF"
        cmake.definitions["WITH_TESTS"] = "OFF"     # opt pthread
        cmake.definitions["WITH_SYSTEMD"] = "OFF"   # requires iio_daemon
        cmake.definitions["WITH_SYSVINIT"] = "OFF"  # requires iio_daemon
        cmake.definitions["WITH_UPSTART"] = "OFF"   # requires iio_daemon
        cmake.definitions["INSTALL_UDEV_RULE"] = "OFF" # requires usb_backend, requires linux
        cmake.definitions["WITH_LOCAL_BACKEND"] = "ON" if self.options.local_backend else "OFF"
        cmake.definitions["WITH_LOCAL_CONFIG"] = "ON" if self.options.local_config else "OFF"
        cmake.definitions["WITH_NETWORK_BACKEND"] = "ON" if self.options.network_backend else "OFF"
        cmake.definitions["WITH_USB_BACKEND"] = "ON" if self.options.usb_backend else "OFF"
        cmake.definitions["WITH_SERIAL_BACKEND"] = "ON" if self.options.serial_backend else "OFF"
        cmake.definitions["WITH_XML_BACKEND"] = "ON" if self.options.xml_backend else "OFF"
        cmake.definitions["WITH_IIOD"] = "ON" if self.options.iio_daemon else "OFF"
        cmake.definitions["ENABLE_IPV6"] = "ON" if self.options.ipv6 else "OFF"
        cmake.definitions["WITH_DOC"] = "ON" if self.options.documentation else "OFF"

        # iiod
        cmake.definitions["ENABLE_AIO"] = "ON" if self.options["use_aio"] else "OFF" # requires libaio
        cmake.definitions["WITH_IIOD_USBD"] = "ON" if self.options["iio_daemon_usb"] else "OFF" # depend on "struct usb_functionfs_descs_head_v2" how to check?

        # bindings
        cmake.definitions["PYTHON_BINDINGS"] = "ON" if self.options.python_bindings else "OFF" # requires python interp
        cmake.definitions["MATLAB_BINDINGS"] = "OFF" # requires matlab exe
        cmake.definitions["CSHARP_BINDINGS"] = "OFF" # requires mcs compiler

        cmake.configure()
        return cmake

    def build(self):
        cmake = self.configure_cmake()
        cmake.build()

    def package(self):
        cmake = self.configure_cmake()
        cmake.install()

    def package_info(self):
        if self.settings.os == "Macos":
            if self.options.framework:
                self.cpp_info.frameworks = ["iio"]
                self.cpp_info.includedirs = ["Frameworks/iio.framework/Headers"]
            else:
                self.cpp_info.libs = ["iio"]
        elif self.settings.os == "Linux":
            self.cpp_info.libs = ["iio"]
        elif self.settings.os == "Windows":
            if self.settings.compiler == "Visual Studio":
                if not self.options.shared:
                    self.cpp_info.defines = ["LIBIIO_STATIC=1"]
                self.cpp_info.libs = ["libiio"]
            else:
                self.cpp_info.libs = ["iio"]
