from conans import ConanFile, CMake, tools
import os, subprocess

class ModernCppProject(ConanFile):
    name = "moderncpp-project-template"
    version = "0.1.0"
    license = "MIT"
    url = "https://gitlab.com/madduci/moderncpp-project-template"
    description = "Modern C++ Project Template"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=False"
    generators = "cmake"
    requires = "doctest/1.2.6@bincrafters/stable"
    build_policy = "always" # update source code every time
    conanfile_dir = os.path.dirname(os.path.realpath(__file__))
    project_dir = os.path.join(conanfile_dir, "project")
    project_files_extensions = ['.h', '.cpp', '.hpp', '.c', '.cc', '.hh', '.cxx', '.hxx']
    project_cpp_files_extensions = ['.cpp', '.c', '.cc', '.cxx']
    build_dir = os.path.join(conanfile_dir, 'build')

    def source(self):
        '''Format files if clang-format is available'''
        if tools.which('clang-format') is not None:
            self.__clang_format()

    def configure(self):
        '''Force libstdc++11 on gcc'''
        if self.settings.compiler == "gcc" and self.settings.compiler.libcxx == "libstdc++":
            self.settings.compiler.libcxx = "libstdc++11"
        '''Force libc++ on clang'''
        if self.settings.compiler == "clang":
            self.settings.compiler.libcxx = "libc++"

    def build(self):
        '''Format files if clang-format is available
           Setup CMake project
           Runs clang-check and cppcheck if available
           Builds the source files and runs the tests'''

        if tools.which('clang-format') is not None:
            self.__clang_format()

        cmake = CMake(self, set_cmake_flags=True)
        cmake.configure(source_dir=self.project_dir)

        if tools.which('clang-check') is not None:
            self.__clang_check()

        if tools.which('cppcheck') is not None:
            self.__cppcheck()

        cmake.build()
        cmake.test()

        #TODO: Add Install target on CMake
        #cmake.install()

    def package(self):
        self.copy("*.h", dst="include", src="hello")
        self.copy("*hello.lib", dst="lib", keep_path=False)
        self.copy("*.dll", dst="bin", keep_path=False)
        self.copy("*.so", dst="lib", keep_path=False)
        self.copy("*.dylib", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = [self.name]

    def __list_files(self, extensions):
        '''Finds all the files by extension'''
        found_files = []
        for path, subdirs, files in os.walk(self.project_dir):
            for file in files:
                extension = os.path.splitext(file)[1]
                for ext in extensions:
                    if ext == extension:
                        found_files.append(os.path.join(path, file))

        return found_files

    def __clang_check(self):
        '''Performs clang-check on compiled files'''
        files = self.__list_files(self.project_cpp_files_extensions)
        for file in files:
            subprocess.Popen(['clang-check', '-analyze', "-p=%s" % self.build_dir, file], stdout=subprocess.PIPE)

    def __clang_format(self):
        '''Performs clang-format on all C++ files'''
        files = self.__list_files(self.project_files_extensions)
        for file in files:
            subprocess.Popen(['clang-format', '-style=file', '-i', file], stdout=subprocess.PIPE)

    def __cppcheck(self):
        '''Performs clang-format on all C++ files'''
        build_path = os.path.join(self.build_dir, 'compile_commands.json')
        xml_report = os.path.join(self.build_dir, 'cppcheck.xml')
        with open(xml_report, "w") as output_file:
            subprocess.call(
                [
                    'cppcheck',
                    '--enable=warning,performance,portability,information,missingInclude',
                    '--cppcheck-build-dir=%s' % self.build_dir,
                    '--project=%s' % build_path,
                    '-i',
                    'include',
                    '--quiet',
                    '--xml'
                ],
                stdout=output_file,
                stderr=output_file)


