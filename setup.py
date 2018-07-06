
from setuptools import find_packages, setup


def read_file(name):
    with open(name) as fobj:
        return fobj.read().strip()


long_description = read_file("README.md")
version = read_file("facsimile/VERSION")
requirements = read_file("facsimile/requirements.txt").split('\n')
test_requirements = read_file("facsimile/requirements-test.txt").split('\n')


setup(
    name='vaping',
    version=version,
    author='20C',
    author_email='code@20c.com',
    description='vaping is a healthy alternative to smokeping!',
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='LICENSE',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: No Input/Output (Daemon)',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Telecommunications Industry',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Monitoring',
        'Topic :: System :: Networking :: Monitoring',
    ],
    packages = find_packages(),
    include_package_data=True,
    url='https://github.com/20c/vaping',
    download_url='https://github.com/20c/vaping/%s' % version,
    install_requires=requirements,
    test_requires=test_requirements,
    entry_points={
        'console_scripts': [
            'vaping=vaping.cli:cli',
        ]
    },
    zip_safe=True,
)

