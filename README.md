# EosImport
A small script to import images from an camera SD-Card to your computer, in my case from an EOS DSLR.

The script also renames the files during the import to the format YYYYMMDD-IMG_XXXX_CAMERA.EXT, as Adobe Photoshop Lightroom does by default.

## Install
Download the source code to whereever you want:
`git clone https://github.com/prsmr/EosImport.git .` 

## Usage
Use the binary directly in the git-repository or move it to /bin or /usr/bin to access it system-wide by typing

`./EosImport` (in the local git-repository)
or 
`EosImport` (system-wide after moving, regardless of where you are)

The binary was created by using [PyInstaller](https://pypi.org/project/pyinstaller/).

You can of course also use Python
`python EosImport.py`
