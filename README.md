# fontastic

Tools to download google font files and material design icons

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

```
# To download the roboto font files and extract width to height ratios...

python3 fontastic.py Roboto <output-folder>

Creates the files:

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

## JSON format for font geometry files

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


Just download zip containing latest material design icons (~500Mb) to the cache folder and 
index it ready for extraction:

```
python3 materialise.py --cache-folder /tmp
```

To get the names of the icons visit https://fonts.google.com/icons?selected=Material+Icons
Select an icon and on the right hand side of the screen, a panel is displayed.  Just above the buttons to manually 
download the SVG and PNG files, a text box provides the unique name of the icon in lower case letters and underscores.

Extract specific icons `home` and `folder` to the icons subfolder of the current directory in outline and round styles

```
python3 materialise.py --cache-folder /tmp --output-folder ./icons 
      --icon-names "home,folder" 
      --icon-styles "outline,round"
```

Creates the following files

```
icons/
    home_outline_24px.svg
    home_round_24px.svg
    home_outline_24px.css
    home_round_24px.css
    folder_outline_24px.svg
    folder_round_24px.svg
    folder_outline_24px.css
    folder_round_24px.css
```

Download the same icons but attempt convert to orange and purple (experimental):

```
python3 materialise.py --cache-folder /tmp --output-folder `pwd`/icons 
    --icon-names "home,folder" --icon-styles "outline,round"
    --icon-colours "orange,purple"
```

Creates the following files

```
icons/
    home_outline_orange_24px.svg
    home_round_orange_24px.svg
    home_outline_purple_24px.svg
    home_round_purple_24px.svg
    home_outline_orange_24px.css
    home_round_orange_24px.css
    home_outline_purple_24px.css
    home_round_purple_24px.css
    folder_outline_orange_24px.svg
    folder_round__orange_24px.svg
    folder_outline_purple_24px.svg
    folder_round_purple_24px.svg
    folder_outline_orange_24px.css
    folder_round__orange_24px.css
    folder_outline_purple_24px.css
    folder_round_purple_24px.css
```



