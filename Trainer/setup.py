# Setup LLM_Trainer

import setuptools

import LLM_Trainer

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="LLM_Trainer",
    version=LLM_Trainer.__version__,
    author="Danny Waser",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/wasertech/OneOS",
    packages=setuptools.find_packages(),
    install_requires=[
        "transformers>=4.5.0",
        # "torch>=1.7.0",
        "trl>=0.0.3",
        "peft>=0.0.1",
        "bitsandbytes>=0.0.1",
        "datasets>=1.5.0",
        "einops>=0.3.0",
        "wandb>=0.10.30",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)


