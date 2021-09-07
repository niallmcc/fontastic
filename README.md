# fontastic

Tools to download google web font files and material design icons

## Google fonts

* Use fontastic.py to:
  * Download and saves truetype font files (for regular, bold and italic font variants) and converts to .woff2 format.  
  * Extract geometry information (width to height ratio) for each code point.  

## Material design icons

* Use materialise.py to:
  * Download the latest material design icons zip
  * Extract icons for specific names and styles (filled,outline,sharp,round,twotone) 
  * Colourise icons (experimental) from the default colour (black)
  * Save icons as svg and css (background-image+data URI) files
  
## Installation

clone this repo or just download the scripts [extract.py](extract.py) and the requirements file [requirements.txt](requirements.txt) 

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
## Usage - materialise.py

* Download zip containing latest material design icons (~500Mb) to the cache folder and 
index it ready for extraction:

```
python3 materialise.py --cache-folder /tmp
```

To get the names of the icons visit https://fonts.google.com/icons?selected=Material+Icons
Select an icon and on the right hand side of the screen, a panel is displayed.  Just above the buttons to manually 
download the SVG and PNG files, a text box provides the unique name of the icon in lower case letters and underscores.

* Extract specific icons `home` and `folder` to the icons subfolder of the current directory in outline and round styles

```
python3 materialise.py --cache-folder /tmp --svg-output-folder ./icons \ 
      --icon-names home folder  \
      --icon-styles outline round
```

Creates the following files

```
icons/
    home_outlined_24px.svg
    home_round_24px.svg
    folder_outlined_24px.svg
    folder_round_24px.svg
```
    
* Extracts the same icons but attempt convert to orange and purple (experimental):

```
python3 materialise.py --cache-folder /tmp --svg-output-folder ./icons \
    --icon-names home folder --icon-styles outlined round \
    --icon-colours orange purple
```

...creates the following files

```
icons/
    home_outline_orange_24px.svg
    home_round_orange_24px.svg
    home_outlined_purple_24px.svg
    home_round_purple_24px.svg
    folder_outlined_orange_24px.svg
    folder_round_orange_24px.svg
    folder_outlined_purple_24px.svg
    folder_round_purple_24px.svg
```
    
* Create a CSS-based icon file

```
python3 ../materialise.py --cache-folder /tmp --css-output-path icons.css \
    --icon-names home folder --icon-styles outlined round \
    --icon-colours orange purple
```

...creates or appends to a CSS file containing a class for each extracted icon, for example:

```
.home-round-orange {
    /* material-icon home round orange */
    background-image: url('data:image/svg+xml;base64,PHN2ZyBoZWlnaHQ9IjI0IiB2aWV3Qm94PSIwIDAgMjQgMjQiIHdpZHRoPSIyNCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cGF0aCBkPSJNMCAwaDI0djI0SDBWMHoiIGZpbGw9Im5vbmUiLz48cGF0aCBkPSJNMTAgMTl2LTVoNHY1YzAgLjU1LjQ1IDEgMSAxaDNjLjU1IDAgMS0uNDUgMS0xdi03aDEuN2MuNDYgMCAuNjgtLjU3LjMzLS44N0wxMi42NyAzLjZjLS4zOC0uMzQtLjk2LS4zNC0xLjM0IDBsLTguMzYgNy41M2MtLjM0LjMtLjEzLjg3LjMzLjg3SDV2N2MwIC41NS40NSAxIDEgMWgzYy41NSAwIDEtLjQ1IDEtMXoiIGZpbGw9Im9yYW5nZSIvPjwvc3ZnPg==');
}
```

* You can specify a file containing one icon name per line, using the `--icon-names-file <PATH>` option

* When writing icons as CSS classes, specify a prefix for the class names using `--css-prefix <PREFIX>`

* When specifying icon names, colours or styles, you can rename the names/colours,styles by adding a suffix `=newname`

For example:

```
python3 ../materialise.py --cache-folder /tmp --css-output-path icons.css \
    --icon-names "home=house" folder --icon-styles "outlined=outline" round \
    --icon-colours "#FF2035=red" purple
```