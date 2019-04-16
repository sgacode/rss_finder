import os
import os.path
from setuptools import find_packages, setup
try: # for pip >= 10
    from pip._internal.req import parse_requirements
except ImportError: # for pip <= 9.0.3
    from pip.req import parse_requirements

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

# parse_requirements() returns generator of pip.req.InstallRequirement objects
cur_dir = os.path.abspath(os.path.dirname(__file__))
install_reqs = parse_requirements(os.path.join(cur_dir, 'requirements.txt'), session=False)
reqs = [str(ir.req) for ir in install_reqs]

setup(
    name='rss_finder',
    version='1.0',
    packages=find_packages(),
    description='RSS feed finder',
    author='Egor Serikov',
    author_email='serikov.egor@gmail.com',
    classifiers=[],
    install_requires=reqs
)