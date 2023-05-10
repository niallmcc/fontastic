# fontastic

A tool to download google web font files

## Google fonts

* Use fontastic.py to:
  * Download and saves truetype font files (for regular, bold and italic font variants) and converts to .woff2 format.  
  * Extract geometry information (width to height ratio) for each code point.  

## Installation

clone this repo or just download the scripts [fontastic.py](fontastic.py) and the requirements file [requirements.txt](requirements.txt) 

## Dependencies

Requires Python 3.8 or later

Uses the [fonttools](https://pypi.org/project/fonttools/), [brotli](https://pypi.org/project/Brotli/) and [requests](https://pypi.org/project/requests/) 
packages. 

To install all dependencies using pip:

```
# pip3 install -r requirements.txt
```

## Usage - fontastic.py

* To download the roboto font files and extract width to height ratios...

```
python3 fontastic.py Roboto <output-folder>
```

...creates the files:

```
<output-folder>/
    Roboto/
        LICENSE.txt
        Roboto-Regular.ttf2
        Roboto-Regular.woff2
        Roboto-Regular.json
        Roboto-Italic.ttf2
        Roboto-Italic.woff2
        Roboto-Italic.json
        Roboto-Bold.ttf2
        Roboto-Bold.woff2
        Roboto-Bold.json
        Roboto-BoldItalic.ttf2
        Roboto-BoldItalic.woff2
        Roboto-BoldItalic.json
```

* JSON format for font geometry files

The format for these files is fairly self-explanatory

```
{
    "download_url": "https://github.com/google/fonts/blob/main/apache/roboto/static/Roboto-Regular.ttf?raw=true", 
    "source_url": "https://github.com/google/fonts/tree/main/apache/roboto",
    "name": "Roboto", 
    "path": "Roboto-Regular.woff2", 
    "weight": "normal", 
    "style": "normal", 
    "glyph_widths": {
        "0": 0.0, 
        "2": 0.0, 
        "13": 0.248046875, 
        "32": 0.248046875, 
        "33": 0.2578125, 
        "34": 0.3203125, 
        "35": 0.61572265625, 
        ...
    }
}
```
