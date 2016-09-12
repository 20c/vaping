
from setuptools import find_packages, setup

version = open('facsimile/VERSION').read().strip()
requirements = open('facsimile/requirements.txt').read().split("\n")
test_requirements = open('facsimile/requirements-test.txt').read().split("\n")

setup(
    name='vaping',
    version=version,
    author='20C',
    author_email='code@20c.com',
    description='vaping is a healthy alternative to smokeping!',
    long_description='',
    license='LICENSE',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Telecommunications Industry',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Internet',
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

