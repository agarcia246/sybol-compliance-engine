from pathlib import Path
from setuptools import find_packages, setup

BASE_DIR = Path(__file__).resolve().parent
README = BASE_DIR / "README.md"

with README.open("r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="sybol-compliance-engine",
    version="0.1.0",
    description="AI compliance engine for media authenticity scoring and verifiable credential issuance",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="IEU Labs x Sybol",
    url="https://github.com/ieu-labs/sybol-compliance-engine",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    include_package_data=True,
    python_requires=">=3.10",
    install_requires=[
        "fastapi>=0.110,<1.0",
        "uvicorn[standard]>=0.27,<1.0",
        "pydantic>=2.6,<3.0",
        "qdrant-client>=1.8,<2.0",
        "llama-index>=0.10,<0.12",
        "sentence-transformers>=2.6,<3.0",
        "transformers>=4.40,<5.0",
        "torch>=2.2,<3.0",
        "opencv-python>=4.9,<5.0",
        "exifread>=3.0,<4.0",
        "imagehash>=4.3,<5.0",
        "pillow>=10.0,<11.0",
        "numpy>=1.26,<3.0",
        "scikit-learn>=1.4,<2.0",
        "httpx>=0.27,<1.0",
        "python-multipart>=0.0.9,<1.0",
        "jsonschema>=4.21,<5.0",
        "pymupdf>=1.24,<2.0",
    ],
    extras_require={
        "dev": [
            "pytest>=8.0,<9.0",
            "pytest-cov>=5.0,<6.0",
            "pytest-asyncio>=0.23,<1.0",
            "pytest-mock>=3.12,<4.0",
            "hypothesis>=6.100,<7.0",
            "ruff>=0.4,<1.0",
            "black>=24.0,<25.0",
            "mypy>=1.8,<2.0",
            "ragas>=0.1,<0.2",
            "deepeval>=0.20,<0.30",
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
)