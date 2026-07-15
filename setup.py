from __future__ import annotations

from setuptools import setup

try:
    from setuptools.command.bdist_wheel import bdist_wheel as orig_bdist_wheel
except ImportError:
    cmdclass = {}
else:
    class bdist_wheel(orig_bdist_wheel):
        def finalize_options(self):
            orig_bdist_wheel.finalize_options(self)
            self.root_is_pure = False  # not a pure-python package

        def get_tag(self):
            _, _, plat = orig_bdist_wheel.get_tag(self)
            # No Python source, no extensions — tag as py2.py3 none <platform>
            return 'py2.py3', 'none', plat

    cmdclass = {'bdist_wheel': bdist_wheel}

setup(cmdclass=cmdclass)
