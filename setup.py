from setuptools import find_packages, setup

setup(
    name="lidar_client",
    version="0.1.0",
    author="Pablo Tarrio",
    author_email="pablo.tarrio@uie.edu",
    description="Cliente Python para recibir datos de RPLIDAR A1 vía TCP",
    long_description=open("README_lidar_client.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/PabloTarrio/create3-lidar-client",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[],
)
