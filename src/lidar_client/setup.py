from setuptools import find_packages, setup

setup(
    name="lidar_client",
    version="0.1.0",
    author="Tu Nombre",
    author_email="tu@email.com",
    description="Cliente Python para recibir datos de RPLIDAR A1 vía TCP",
    long_description=open("README.md").read() if open("README.md") else "",
    long_description_content_type="text/markdown",
    url="https://github.com/tu-usuario/lidar_client",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        # No tiene dependencias externas, solo usa librerías estándar
    ],
)
