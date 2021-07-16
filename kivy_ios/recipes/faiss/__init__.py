# TODO
# hardcoded version numbers?
# fix swigfaiss build
# ....

# brew install swig

from kivy_ios.toolchain import PythonRecipe, shprint
from os.path import join, exists
import sh
import os


class FaissRecipe(PythonRecipe):
    version = "v1.7.1"
    url = "https://github.com/facebookresearch/faiss/archive/refs/tags/{version}.tar.gz"
    depends = ["python", "numpy", "openmp"]
    include_per_arch = True
    libraries = [
        "build/faiss/libfaiss.a",
    ]

    def build_arch(self, arch):
        openmp_dir = '/Users/robertsmith/ML/kivy-tensorflow-helloworld/.buildozer/ios/platform/kivy-ios/build/openmp/arm64/openmp-12.0.1.src/build/runtime/src'
        openmp_lib = join(openmp_dir, 'libomp.a')

        python_lib = join(self.ctx.build_dir, 'python3', arch.arch,
                          f'Python-{self.ctx.hostpython_recipe.version}',
                          f'libpython{self.ctx.python_ver}.a')
        python_include = join(self.ctx.dist_dir, 'root', 'python3', 'include',
                              f'python{self.ctx.python_ver}')
        numpy_dir = join(self.ctx.build_dir, 'numpy', arch.arch,
                         'numpy-1.20.2')  ###
        numpy_include = join(numpy_dir, 'build',
                             f'src.macosx-10.15-x86_64-3.9', 'numpy',
                             'core', 'include', 'numpy')
        numpy_include_dir = join(numpy_dir, 'numpy', 'core', 'include')

        build_env = arch.get_env()
        build_env['CXXFLAGS'] = build_env.get(
            'CXXFLAGS',
            '') + f" -Dnil=nil -std=c++11 -I{openmp_dir} -I{numpy_include}"

        command = sh.Command("cmake")
        shprint(command,
                "-Bbuild",
                "-S.",
                "-DFAISS_ENABLE_GPU=OFF",
                "-DBUILD_SHARED_LIBS=OFF",
                "-DCMAKE_SYSTEM_NAME=iOS",
                "-DCMAKE_SYSTEM_NAME=Darwin",
                f"-DCMAKE_OSX_ARCHITECTURES={arch}",
                f"-DCMAKE_OSX_SYSROOT={arch.sysroot}",
                "-DCMAKE_CXX_COMPILER=/usr/bin/clang++",
                "-DCMAKE_CXX_COMPILER_ID=AppleClang",
                "-DOpenMP_CXX_FLAGS=-Xclang -fopenmp",
                "-DOpenMP_CXX_LIB_NAMES=omp",
                f"-DOpenMP_omp_LIBRARY={openmp_lib}",
                "-DBLA_VENDOR=Apple",
                f"-DPython_EXECUTABLE={self.ctx.hostpython}",
                f"-DPython_LIBRARY={python_lib}",
                f"-DPython_INCLUDE_DIR={python_include}",
                f"-DPython_NumPy_INCLUDE_DIR={numpy_include_dir}",
                _env=build_env)

        command = sh.Command("make")
        shprint(command, "-C", "build", "-j", "faiss", _env=build_env)
        shprint(command, "-C", "build", "-j", "swigfaiss", _env=build_env)

        super(FaissRecipe, self).build_arch(arch)

    def install(self):
        arch = list(self.filtered_archs)[0]
        build_dir = self.get_build_dir(arch.arch)
        os.chdir(join(build_dir, "build", "faiss", "python"))
        hostpython = sh.Command(self.ctx.hostpython)
        build_env = arch.get_env()
        dest_dir = join(self.ctx.dist_dir, "root", "python3")
        build_env['PYTHONPATH'] = self.ctx.site_packages_dir
        shprint(hostpython,
                "setup.py",
                "install",
                "--prefix",
                dest_dir,
                _env=build_env)


recipe = FaissRecipe()
