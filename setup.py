from setuptools import setup, find_packages

setup(
    description=" OPC (OLE for Process Control) toolkit for Python 3.x",
    install_requires=['Pyro4>=4.82', 'pywin32==304', 'waitress==2.1.2', 'paste==3.5.3'],
    keywords='python, opc, openopc',
    license='GPLv2',
    maintainer='Yue BaoBao',
    maintainer_email='yqbaowo@foxmail.com',
    name="OpenOPC_Py38",
    packages=find_packages(),
    python_requires='>=3.8',
    url='https://github.com/YQBaobao/openopc-python3.8',
    version="1.4.0",
    author='yqbao',
    author_email='yqbaowo@gmail.com',
    zip_safe=False
)
