import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="stagg-ekg-plus-calvinmclean",
    version="0.0.1",
    author="Calvin McLean",
    author_email="calvinlmc@gmail.com",
    description="A Python library for interacting with the Fellow Stagg EKG+ using Bluetooth LE",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/calvinmclean/stagg-ekg-plus",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Linux",
    ],
    python_requires='>=3.6',
)
