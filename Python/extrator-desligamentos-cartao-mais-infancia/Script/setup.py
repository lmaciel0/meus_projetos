"""
Setup do projeto Leitor de Desligamentos CMIC
"""

from setuptools import setup, find_packages
from pathlib import Path

# Ler README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="leitor-desligamentos-cmic",
    version="1.0.0",
    description="Ferramenta para extrair dados de PDFs de desligamento do Cartão Mais Infância Ceará",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Prefeitura Municipal de Fortaleza",
    author_email="desenvolvimento@fortaleza.ce.gov.br",
    url="https://github.com/fortaleza/leitor-desligamentos-cmic",
    
    packages=find_packages(),
    
    python_requires=">=3.12",
    
    install_requires=[
        "pdfplumber>=0.10.0",
        "PyPDF2>=4.0.0",
        "pytesseract>=0.3.10",
        "pdf2image>=1.16.0",
        "python-dotenv>=1.0.0",
        "pandas>=2.0.0",
        "openpyxl>=3.10.0",
        "xlsxwriter>=3.1.0",
    ],
    
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "isort>=5.12.0",
        ]
    },
    
    entry_points={
        "console_scripts": [
            "leitor-desligamentos=main:main",
        ]
    },
    
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Topic :: Office/Business",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Operating System :: OS Independent",
    ],
    
    keywords="pdf extraction data processing xlsx csv cmic fortaleza",
    project_urls={
        "Bug Reports": "https://github.com/fortaleza/leitor-desligamentos-cmic/issues",
        "Source": "https://github.com/fortaleza/leitor-desligamentos-cmic",
        "Documentation": "https://github.com/fortaleza/leitor-desligamentos-cmic/blob/main/README.md",
    },
)
