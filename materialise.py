
import requests
import os.path
import logging
import re
import zipfile
import pickle
from xml.dom.minidom import parseString
import base64

CSS_TEMPLATE = \
"""
.%s {
    /* material-icon %s %s %s */
    background-image: url('data:image/svg+xml;base64,%s');
}

"""

CSS_HEADER1="/* Icons are extracted from Google Material Icons (https://github.com/google/material-design-icons) and are\n"
CSS_HEADER2="   licensed under Apache 2 License (https://github.com/google/material-design-icons/blob/master/LICENSE) */\n"

class Materialise:

    def __init__(self,cache_folder=".",svg_output_folder=".",css_output_path="icons.css", css_prefix=""):
        """
        Construct an instance

        :param cache_folder: a folder for caching the downloaded icons file and storing an index built on it
        :param svg_output_folder: a folder for storing extracted icon svg files
        :param css_output_path: a path to store extracted CSS icon definitions
        :param css_prefix: a prefix to use on class names when building CSS icon files
        """
        self.logger = logging.getLogger("Materialise")
        self.path = "material-design-icons-master"
        self.url = "https://github.com/google/material-design-icons/archive/master.zip"
        self.cache_path = os.path.join(cache_folder,self.path+".zip")
        self.index_path = os.path.splitext(self.cache_path)[0]+".idx"
        self.css_prefix = css_prefix
        self.index = {}
        self.svg_output_folder = svg_output_folder
        self.css_output_path = css_output_path

        # create a regexp to match the paths of filenames within the zip
        self.path_regexp = re.compile("material-design-icons-master/src/[^/]+/([^/]+)/materialicons([^/]*)/24px.svg")
        self.icons = set()
        self.styles = set()
        self.license = ""

    def init(self):
        """
        initialise's the instance, by:
        (1) downloading the large icons zip file from https://github.com/google/material-design-icons/archive/master.zip
        (2) searching the zip for svg icon files and saving the details in a pickled dictionary

        Files created in (1) and (2) are stored in the cache folder (see the constructor).  If the files already exist
        these steps are skipped.
        """
        # first download the icons zip if its not already in the cache folder
        if not os.path.exists(self.cache_path):
            self.logger.info("Downloading icons from %s to %s" % (self.url, self.cache_path))
            response = requests.get(self.url)
            if response.ok:
                with open(self.cache_path, "wb") as of:
                    of.write(response.content)
                self.logger.info("Downloading icons from %s to %s" % (self.url, self.cache_path))

        # extract the license
        with zipfile.ZipFile(self.cache_path) as zf:
            with zf.open("material-design-icons-master/LICENSE") as f:
                self.license = f.read()

        # build the index if not already cached
        if not os.path.exists(self.index_path):
            self.logger.info("Indexing downloaded icons...")
            with zipfile.ZipFile(self.cache_path) as zf:
                for name in zf.namelist():
                    if name.endswith("24px.svg"):
                        matches = self.path_regexp.match(name)
                        if matches:
                            icon_name = matches.group(1)
                            icon_style = matches.group(2)
                            if icon_style == "":
                                icon_style = "filled"
                            key = (icon_name,icon_style)
                            if key in self.icons:
                                self.logger.warning("found multiple matches for %s,%s" % (icon_name,icon_style) )
                            self.index[key] = name
            with open(self.index_path,"wb") as indexf:
                pickle.dump(self.index,indexf)
            self.logger.info("Indexing complete")
        else:
            with open(self.index_path,"rb") as indexf:
                self.index = pickle.load(indexf)

        # get a summary of all icon names and styles
        for (name,style) in self.index.keys():
            self.styles.add(style)
            self.icons.add(name)

        self.logger.info("Index contains %d icons, styles: %s" % (len(self.icons),", ".join(self.styles)))

    def colourise(self,contents, colour):
        """
        Attempt to re-colour the icon
        :param contents: the contents of the icon
        :param colour: the colour to apply, eg "red" or "#FF0000"
        :return:
        """

        def setAttribute(node, tag, attr, value):
            if node.tagName == tag:
                attrs = dict(node.attributes.items())
                if attr not in attrs:
                    node.attributes[attr] = value
            for child in node.childNodes:
                if child.nodeType == node.ELEMENT_NODE:
                    setAttribute(child, tag, attr, value)

        d = parseString(contents)

        # changing the fill colour of the following elements (if not already set)
        # is sufficient for the subset of icons investigated.  Likely more SVG elements
        # may need to be added to this list
        for tag in ["path","polygon","rect","circle"]:
            setAttribute(d.childNodes[0], tag, "fill", colour)

        return d.toxml().replace('<?xml version="1.0" ?>', '').encode("utf-8")

    def open(self):
        self.zf = zipfile.ZipFile(self.cache_path)

    def close(self):
        self.zf.close()
        self.zf = None

    def extract(self,name,newname,style="",newstyle="",colour="black",newcolour=""):
        """
        Extract an icon from the zip and save out SVG and CSS
        :param name: the name of the icon in the icon set
        :param newname: the new icon name to output
        :param style: the style, one of (outline,filled,round,sharp,twotone)
        :param newstyle: the new icon style to output (defaults to the original style name)
        :param colour: the colour to apply, (defaults to the original black colour)
        :param newcolour: the new colour name to output (defaults to the original colour)
        """
        key = (name,style)
        if key not in self.index:
            self.logger.warning("Icon with name %s and style %s not found" % (name, style))
        else:
            with self.zf.open(self.index[key]) as f:
                data = f.read()
                # if a colour is specified try to recolour the icon
                if colour and colour != "black":
                    data = self.colourise(data,colour)
                out_name = newname
                out_class = newname
                if newstyle:
                    out_name += "_" + newstyle.replace(".","")
                    out_class += ("-" + newstyle) if not newstyle.startswith('.') else newstyle
                if newcolour:
                    out_name += "_" + newcolour.replace(".","")
                    out_class += ("-" + newcolour) if not newcolour.startswith(".") else newcolour
                # write out the SVG
                if self.svg_output_folder:
                    out_name = out_name.replace("-","_")
                    svg_outpath = os.path.join(self.svg_output_folder,out_name) + "_24px.svg"
                    with open(svg_outpath,"wb") as of:
                        of.write(data)
                    self.logger.info("extracted svg to %s" % (svg_outpath))
                if self.css_output_path:
                    if newstyle:
                        newstyle = "-"+newstyle
                    if newcolour:
                        newcolour = "-"+newcolour
                    css_outpath = self.css_output_path % { "style": newstyle, "colour": newcolour }
                    css_selector = self.css_prefix
                    if self.css_prefix:
                        css_selector += "-"
                    css_selector += out_class
                    # also write out a CSS file, changing the suffix from .svg to .css
                    self.export_css(data, css_selector, css_outpath, name, style, colour)
                    self.logger.info("appending CSS class %s to %s" % (css_selector, css_outpath))

    def export_css(self, svg_content, class_name, path, name, style, colour):
        """
        Appends a SVG icon definition to a file (defining a class with background-image and a data URI)

        :param svg_content: the svg content
        :param class_name: the name of the class
        :param path: the path of the css file to save
        :param name: the name of the icon in the icon set
        :param style: the style, one of (outline,filled,round,sharp,twotone)
        :param colour: the colour to apply, or None to use the original colour (black)
        """
        if not os.path.exists(path):
            with open(path,"w") as of:
                of.write(CSS_HEADER1)
                of.write(CSS_HEADER2)
                of.write("\n")

        with open(path,"a") as of:
            base64_content = base64.b64encode(svg_content).decode('utf-8')
            if colour is None:
                colour = ""
            of.write(CSS_TEMPLATE % (class_name, name, style, colour, base64_content) )

    def save_license(self):
        """
        Saves the icons license file to a file named LICENSE in the output folder
        """
        if self.svg_output_folder:
            with open(os.path.join(self.svg_output_folder,"LICENSE"),"wb") as of:
                of.write(self.license)

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.usage = """
        A program which downloads material design icons from github.com/google.
        Extract geometry to a simple JSON formatted file and create a copy in .woff2 format.
        """
    parser.add_argument("--icon-names", nargs="+", default=[], help="the name of the icons to extract")
    parser.add_argument("--icon-names-file", default="", help="path to a file containing the names of the icons to extract, one per line")
    parser.add_argument("--icon-styles", nargs="+", default=["filled="], help="the styles to extract, from (filled, outlined, round, sharp, twotone)")
    parser.add_argument("--icon-colours", nargs="+", default=["black="], help="attempt to re-colour the icon with one or more colours")
    parser.add_argument("--css-prefix", help="prefix for css class names", default="")
    parser.add_argument("--svg-output-folder", help="the name of the output folder to store svg files", default="")
    parser.add_argument("--css-output-path", help="the name of the file to store css icon definitions", default="")
    parser.add_argument("--cache-folder", help="the name of the folder in which to cache the downloaed icon set", default="./cache")
    args = parser.parse_args()

    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)

    logger = logging.getLogger("Materialise")

    logger.info("Icon Names  : " + str(args.icon_names))
    logger.info("Icon Styles : " + str(args.icon_styles))
    logger.info("Icon Colours: " + str(args.icon_colours))

    if args.svg_output_folder:
        os.makedirs(args.svg_output_folder,exist_ok=True)

    os.makedirs(args.cache_folder,exist_ok=True)


    materialise = Materialise(cache_folder=args.cache_folder,svg_output_folder=args.svg_output_folder,css_output_path=args.css_output_path,css_prefix=args.css_prefix)
    materialise.init()
    names = []
    names += args.icon_names
    if args.icon_names_file:
        with open(args.icon_names_file) as f:
            for line in f.readlines():
                name = line.strip()
                if name:
                    names.append(name)

    materialise.open()
    for name in names:
        name = name.strip()
        newname = name
        if "=" in name:
            (name, newname) = name.split("=")
        for style in args.icon_styles:
            style = style.strip()
            newstyle = style
            if "=" in style:
                (style, newstyle) = style.split("=")
            for colour in args.icon_colours:
                colour = colour.strip()
                newcolour = colour
                if "=" in colour:
                    (colour, newcolour) = colour.split("=")
                materialise.extract(name, newname, style=style, newstyle=newstyle, colour=colour, newcolour=newcolour)
    if len(names):
        materialise.save_license()
    materialise.close()