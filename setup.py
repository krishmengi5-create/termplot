from setuptools import setup, find_packages

setup(
    name="termplot",
    version="1.0.0",
    author="Krish Mengi",
    author_email="krishmengi.bt25ele@pec.edu.in",
    description="Interactive terminal mathematical function visualizer using high-resolution Braille graphics",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/krishmengi5-create/termplot",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Utilities",
    ],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "termplot=termplot.main:main",
        ],
    },
)
