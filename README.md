# TennisForTwo
Original from https://bitbucket.org/SpindleyQ/tennisfortwo/src/master/

Updated to python 3.8.5

# Installation
```
git clone https://github.com/falsidge/TennisForTwo
cd TennisForTwo
pip install pygame twisted
python TennisForTwo.py
```

# Build
```
pyinstaller TennisForTwo.spec
```
or
```
pyinstaller TennisForTwo.py --add-data data;data --add-data tennis.bmp;. --add-data freesansbold.ttf;. --exclude-module numpy --exclude-module scipy --exclude-module lib2to3
``` 
include --onefile for one exe file
