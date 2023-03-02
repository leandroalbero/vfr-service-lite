import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="vfr-service-lite",
    version="0.0.1",
    author="Jobandtalent",
    author_email="leandro.albero@jobandtalent.com",
    description="A minimal version of the VFR service for use on a collab environment",
    url="https://github.com/leandroalbero/vfr-service-lite",
    license='MIT',
    packages=setuptools.find_packages(),
    install_requires=['requests']
)
