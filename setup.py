from setuptools import setup, find_packages

setup(
    description=" OPC (OLE for Process Control) toolkit for Python 3.x",
    install_requires=['Pyro4>=4.82', 'pywin32>=304'],
    keywords='python, opc, openopc',
    license='GPLv2',
    maintainer='Yue BaoBao',
    maintainer_email='yqbaowo@foxmail.com',
    name="OpenOPC-Python3x",
    packages=find_packages(),
    python_requires='>=3.8',
    url='https://github.com/YQBaobao/openopc',
    version="1.3.3",
)
