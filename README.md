## What is this?
This tool was developed to enable easy analysis of USB-Dataloggers that record humidity and/or temperature, supporting a variety of formats with a comfortable, minimalistic and easy to use, interface. The output is highly configurable, check the example-``config`` file for details.

## Supported Formats

- .xbf (XAML Binary Format)
- .xls (Microsoft Excel)
- .csv (Comma Separated Values) (UTF-8/ASCII/Latin-1)
- Format not supported? Send me a sample file!

## Run on Windows

    pythonw.exe ./src/main/python/main.py

## Run on Linux

    # note: if xcb fails to load on wayland try: apt install --reinstall libxcb-xinerama0
    python ./src/main/python/main.py

## Interface
![QT-Interface](https://media.atlantishq.de/pictures/qt_ths_datenlogger.png)

## Output
![Plot](https://media.atlantishq.de/pictures/ths-plot-example.png)

