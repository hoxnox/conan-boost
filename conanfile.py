from conans import tools
import os
from nxtools import NxConanFile
from conans.paths import RUN_LOG_NAME


class BoostConan(NxConanFile):
    name = "boost"
    description = "Boost libraries."
    version = "1.64.0"
    settings = "os", "arch", "compiler", "build_type"
    url = "https://github.com/hoxnox/conan-boost"
    license = "Boost Software License - Version 1.0. http://www.boost.org/LICENSE_1_0.txt"
    # The current python option requires the package to be built locally, to find default Python implementation
    exports = "boost-1.64.0.libressl_patch.tar.gz", "nxtools/__init__.py", "nxtools/nx_conan_file.py"
    options = {
        "shared": [True, False],
        "header_only": [True, False],
        "fPIC": [True, False],
        "libressl_patch":[True, False],
        "without_python": [True, False],
        "without_atomic": [True, False],
        "without_chrono": [True, False],
        "without_container": [True, False],
        "without_context": [True, False],
        "without_coroutine": [True, False],
        "without_coroutine2": [True, False],
        "without_date_time": [True, False],
        "without_exception": [True, False],
        "without_fiber": [True, False],
        "without_filesystem": [True, False],
        "without_graph": [True, False],
        "without_graph_parallel": [True, False],
        "without_iostreams": [True, False],
        "without_locale": [True, False],
        "without_log": [True, False],
        "without_math": [True, False],
        "without_metaparse": [True, False],
        "without_mpi": [True, False],
        "without_program_options": [True, False],
        "without_random": [True, False],
        "without_regex": [True, False],
        "without_serialization": [True, False],
        "without_signals": [True, False],
        "without_system": [True, False],
        "without_test": [True, False],
        "without_thread": [True, False],
        "without_timer": [True, False],
        "without_type_erasure": [True, False],
        "without_wave": [True, False]
    }

    default_options = "shared=False", \
        "header_only=False", \
        "fPIC=False", \
        "libressl_patch=True", \
        "without_python=True", \
        "without_atomic=False", \
        "without_chrono=False", \
        "without_container=False", \
        "without_context=False", \
        "without_coroutine=False", \
        "without_coroutine2=False", \
        "without_date_time=False", \
        "without_exception=False", \
        "without_filesystem=False", \
        "without_fiber=False", \
        "without_graph=False", \
        "without_graph_parallel=False", \
        "without_iostreams=False", \
        "without_locale=False", \
        "without_log=False", \
        "without_math=False", \
        "without_metaparse=False", \
        "without_mpi=False", \
        "without_program_options=False", \
        "without_random=False", \
        "without_regex=False", \
        "without_serialization=False", \
        "without_signals=False", \
        "without_system=False", \
        "without_test=False", \
        "without_thread=False", \
        "without_timer=False", \
        "without_type_erasure=False", \
        "without_wave=False"

    def config_options(self):
        """ First configuration step. Only settings are defined. Options can be removed
        according to these settings
        """
        if self.settings.compiler == "Visual Studio":
            self.options.remove("fPIC")


    def configure(self):
        """ Second configuration step. Both settings and options have values, in this case
        we can force static library if MT was specified as runtime
        """
        if self.settings.compiler == "Visual Studio" and \
           self.options.shared and "MT" in str(self.settings.compiler.runtime):
            self.options.shared = False

        if not self.options.without_iostreams:
            self.requires("zlib/1.2.11@hoxnox/stable")
            if not self.options.header_only:
                self.options["zlib"].shared = self.options.shared


    def do_source(self):
        self.retrieve("0445c22a5ef3bd69f5dfb48354978421a85ab395254a26b1ffb0aa1bfd63a108",
                [
                    "vendor://boost.org/boost/boost_{v_}.tar.gz".format(v_=self.version.replace('.', '_')),
                    "https://sourceforge.net/projects/boost/files/boost/{v}/boost_{v_}.tar.gz/download".format(
                        v=self.version, v_=self.version.replace('.','_'))
                ], "boost-{v}.tar.gz".format(v=self.version))


    def do_build(self):
        if self.options.header_only:
            self.output.warn("Header only package, skipping build")
            return

        build_dir = "{staging_dir}/src".format(staging_dir=self.staging_dir)
        tools.untargz("boost-{v}.tar.gz".format(v=self.version), build_dir)
        if self.options.libressl_patch:
            tools.untargz("boost-{v}.libressl_patch.tar.gz".format(v=self.version), build_dir)

        command = "bootstrap" if self.settings.os == "Windows" else "./bootstrap.sh"
        if self.settings.os == "Windows" and self.settings.compiler == "gcc":
            command += " mingw"
        self.run("cd {staging_dir}/src/boost_{v_} && {bootstrap}".format(
            v_=self.version.replace('.', '_'), bootstrap=command, staging_dir=self.staging_dir))

        flags = []
        if self.settings.compiler == "Visual Studio":
            if self.settings.compiler.version=="15":
                # toolset=msvc-15.0 doesn't work in 1.64
                flags.append("toolset=msvc-14.1")
            else:
                flags.append("toolset=msvc-%s.0" % self.settings.compiler.version)
        elif str(self.settings.compiler) in ["clang", "gcc"]:
            flags.append("toolset=%s"% self.settings.compiler)

        flags.append("link=%s" % ("static" if not self.options.shared else "shared"))
        if self.settings.compiler == "Visual Studio" and self.settings.compiler.runtime:
            flags.append("runtime-link=%s" % ("static" if "MT" in str(self.settings.compiler.runtime) else "shared"))
        flags.append("variant=%s" % str(self.settings.build_type).lower())
        flags.append("address-model=%s" % ("32" if self.settings.arch == "x86" else "64"))
        flags.append("threading=multi")
        flags.append("--prefix={staging_dir}".format(staging_dir=self.staging_dir))
        flags.append("--layout=system")
        flags.append("--ignore-site-config")

        option_names = {
            "--without-python": self.options.without_python,
            "--without-atomic": self.options.without_atomic,
            "--without-chrono": self.options.without_chrono,
            "--without-container": self.options.without_container,
            "--without-coroutine": self.options.without_coroutine,
            "--without-coroutine2": self.options.without_coroutine2,
            "--without-date_time": self.options.without_date_time,
            "--without-exception": self.options.without_exception,
            "--without-filesystem": self.options.without_filesystem,
            "--without-fiber": self.options.without_fiber,
            "--without-graph": self.options.without_graph,
            "--without-graph_parallel": self.options.without_graph_parallel,
            "--without-iostreams": self.options.without_iostreams,
            "--without-locale": self.options.without_locale,
            "--without-log": self.options.without_log,
            "--without-math": self.options.without_math,
            "--without-metaparse": self.options.without_metaparse,
            "--without-mpi": self.options.without_mpi,
            "--without-program_options": self.options.without_program_options,
            "--without-random": self.options.without_random,
            "--without-regex": self.options.without_regex,
            "--without-serialization": self.options.without_serialization,
            "--without-signals": self.options.without_signals,
            "--without-system": self.options.without_system,
            "--without-test": self.options.without_test,
            "--without-thread": self.options.without_thread,
            "--without-timer": self.options.without_timer,
            "--without-type_erasure": self.options.without_type_erasure,
            "--without-wave": self.options.without_wave
        }

        for option_name, activated in option_names.items():
            if activated:
                flags.append(option_name)

        cxx_flags = []
        # fPIC DEFINITION
        if self.settings.compiler != "Visual Studio":
            if self.options.fPIC:
                cxx_flags.append("-fPIC")


        # LIBCXX DEFINITION FOR BOOST B2
        try:
            if str(self.settings.compiler.libcxx) == "libstdc++":
                flags.append("define=_GLIBCXX_USE_CXX11_ABI=0")
            elif str(self.settings.compiler.libcxx) == "libstdc++11":
                flags.append("define=_GLIBCXX_USE_CXX11_ABI=1")
            if "clang" in str(self.settings.compiler):
                if str(self.settings.compiler.libcxx) == "libc++":
                    cxx_flags.append("-stdlib=libc++")
                    cxx_flags.append("-std=c++11")
                    flags.append('linkflags="-stdlib=libc++"')
                else:
                    cxx_flags.append("-stdlib=libstdc++")
                    cxx_flags.append("-std=c++11")
        except:
            pass

        cxx_flags = 'cxxflags="%s"' % " ".join(cxx_flags) if cxx_flags else ""
        flags.append(cxx_flags)

        full_command = "cd {staging_dir}/src/boost_{v_} && {b2} {b2_flags} -j{cpu_cnt} install".format(
            staging_dir = self.staging_dir,
            v_ = self.version.replace('.', '_'),
            b2 = "b2" if self.settings.os == "Windows" else "./b2",
            b2_flags = " ".join(flags),
            cpu_cnt = tools.cpu_count())
        self.output.warn(full_command)
        self._runner(full_command, self.output, os.path.abspath(RUN_LOG_NAME),  None)


    def do_package_info(self):

        if not self.options.header_only and self.options.shared:
            self.cpp_info.defines.append("BOOST_ALL_DYN_LINK")
        else:
            self.cpp_info.defines.append("BOOST_USE_STATIC_LIBS")
        self.cpp_info.defines.extend(["BOOST_ALL_NO_LIB"])

        if self.options.header_only:
            return

        libs = ("python wave unit_test_framework test_exec_monitor container exception "
                "graph iostreams locale log log_setup math_c99 math_c99f math_c99l"
                "program_options random regex wserialization serialization "
                "signals coroutine context timer thread chrono date_time atomic filesystem system").split()

        if not self.options.without_python and not self.options.shared:
            self.cpp_info.defines.append("BOOST_PYTHON_STATIC_LIB")

        for option in self.options.fields:
            if option.startswith('without_') and getattr(self.options, option):
                lib_name = option[8:]
                libs = [l for l in libs if not lib_name in l]

        if self.settings.compiler != "Visual Studio":
            self.cpp_info.libs.extend(["boost_%s" % lib for lib in libs])
        else:
            self.cpp_info.libs.extend(["libboost_%s.lib" % lib for lib in libs])
