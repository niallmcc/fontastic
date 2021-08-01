
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
    background-image: url('data:image/svg+xml;base64,%s');
}

"""

class Materialise:

    def __init__(self,cache_folder=".",output_folder=".",css_prefix=""):
        """
        Construct an instance

        :param cache_folder: a folder for caching the downloaded icons file and storing an index built on it
        :param output_folder: a folder for storing extracted icon files
        :param css_prefix: a prefix to use on class names when building CSS icon files
        """
        self.logger = logging.getLogger("Converter")
        self.path = "material-design-icons-master"
        self.url = "https://github.com/google/material-design-icons/archive/master.zip"
        self.cache_path = os.path.join(cache_folder,self.path+".zip")
        self.index_path = os.path.splitext(self.cache_path)[0]+".idx"
        self.css_prefix = css_prefix
        self.index = {}
        self.output_folder = output_folder
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

        self.logger.info("Indexed %d icons, styles: %s" % (len(self.icons),", ".join(self.styles)))

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
        setAttribute(d.childNodes[0], "path", "fill", colour)
        return d.toxml().replace('<?xml version="1.0" ?>', '').encode("utf-8")

    def extract(self,name,style="",colour=None):
        """
        Extract an icon from the zip and save out SVG and CSS
        :param name: the name of the icon
        :param style: the style, one of (outline,filled,round,sharp,twotone)
        :param colour: the colour to apply, or None to use the original colour (black)
        """
        key = (name,style)
        if key not in self.index:
            self.logger.warning("Icon with name %s and style %s not found" % (name, style))
        else:
            with zipfile.ZipFile(self.cache_path) as zf:
                with zf.open(self.index[key]) as f:
                    data = f.read()
                    # if a colour is specified try to recolour the icon
                    if colour:
                        data = self.colourise(data,colour)
                    out_name = name
                    if style:
                        out_name += "_"+style
                    if colour:
                        out_name += "_"+colour.replace("#","")
                    # write out the SVG
                    svg_outpath = os.path.join(self.output_folder,out_name)+"_24px.svg"
                    with open(svg_outpath,"wb") as of:
                        of.write(data)
                    self.logger.info("extracted icon %s from %s to %s" % (name, self.index[key], svg_outpath))
                    css_outpath = os.path.join(self.output_folder, out_name) + "_24px.css"
                    class_name = self.css_prefix
                    if class_name:
                        class_name += "-"
                    class_name += out_name.replace("_", "-")
                    # also write out a CSS file, changing the suffix from .svg to .css
                    self.export_css(data, class_name, css_outpath)

    def export_css(self, svg_content, class_name, path):
        """
        Exports a SVG file to a self containded css file defining a class with background-image and a data URI

        :param svg_content: the svg content
        :param class_name: the name of the class
        :param path: the path of the css file to save
        """
        with open(path,"w") as of:
            base64_content = base64.b64encode(svg_content).decode('utf-8')
            of.write(CSS_TEMPLATE % (class_name, base64_content) )

    def save_license(self):
        """
        Saves the icons license file to a file named LICENSE in the output folder
        """
        with open(os.path.join(self.output_folder,"LICENSE"),"wb") as of:
            of.write(self.license)

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.usage = """
        A program which downloads material design icons from github.com/google.
        Extract geometry to a simple JSON formatted file and create a copy in .woff2 format.
        """
    parser.add_argument("--icon-names", help="the name of the icons to extract, comma separated")
    parser.add_argument("--icon-styles", help="the styles to extract, from (filled, outline, round, sharp, twotone), comma separated", default="filled")
    parser.add_argument("--icon-colours", help="attempt to re-colour the icon, comma separated list of colours", default=None)
    parser.add_argument("--css-prefix", help="prefix for css class names", default="")
    parser.add_argument("--output-folder", help="the name of the output folder", default="./icons")
    parser.add_argument("--cache-folder", help="the name of the folder in which to cache the downloaed icon set", default="./cache")
    args = parser.parse_args()

    os.makedirs(args.output_folder,exist_ok=True)
    os.makedirs(args.cache_folder,exist_ok=True)

    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)

    materialise = Materialise(cache_folder=args.cache_folder,output_folder=args.output_folder,css_prefix=args.css_prefix)
    materialise.init()
    names = args.icon_names.split(",")
    for name in names:
        name = name.strip()
        for style in args.icon_styles.split(","):
            style = style.strip()
            if args.icon_colours:
                colours = args.icon_colours.split(",")
                for colour in colours:
                    colour = colour.strip()
                    materialise.extract(name, style=style, colour=colour)
            else:
                materialise.extract(name,style=style)
    if len(names):
        materialise.save_license()