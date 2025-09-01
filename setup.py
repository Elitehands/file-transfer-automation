"""Setup script for building executable and managing dependencies"""

from setuptools import setup, find_packages
import sys
import os

with open('requirements.txt', 'r') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

try:
    with open('README.md', 'r', encoding='utf-8') as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = "BBU File Transfer Automation System"

setup(
    name="bbu-file-transfer",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Automated file transfer system for BBU production batches",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    python_requires=">=3.7",
    entry_points={
        'console_scripts': [
            'bbu-transfer=main:main',
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: Microsoft :: Windows",
    ],
    package_data={
        '': ['config/*.json', 'logs/.gitkeep'],
    },
)

PYINSTALLER_SPEC = """
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config', 'config'),
        ('src', 'src'),
    ],
    hiddenimports=[
        'pandas',
        'openpyxl',
        'pywin32',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='File_Transfer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico'  # Optional: add if you have an icon
)
"""

if __name__ == "__main__":
    print("Use this setup for building the application:")
    print("\n1. For development installation:")
    print("   pip install -e .")
    print("\n2. For EXE creation:")
    print("   pip install pyinstaller")
    print("   pyinstaller bbu_transfer.spec")
    print("\n3. For distribution:")
    print("   python setup.py sdist bdist_wheel")