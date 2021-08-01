# Copyright 2020 Niall McCarroll
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os.path
from fontTools.ttLib import TTFont
import requests
import json
import logging


class Converter:
    """
    Utility for downloading and extracting / converting google web fonts
    """

    def __init__(self):
        self.logger = logging.getLogger("Converter")

    def convert(self, font_name, output_folder):
        output_subfolder = os.path.join(output_folder, font_name)
        os.makedirs(output_subfolder, exist_ok=True)
        possible_licenses = ('apache', 'ofl', 'ufl')
        completed = 0
        for weight in ["normal", "bold"]:
            for style in ["normal", "italic"]:
                filename = font_name
                if weight == "normal" and style == "italic":
                    filename += "-Italic"
                elif weight == "bold" and style == "normal":
                    filename += "-Bold"
                elif weight == "bold" and style == "italic":
                    filename += "-BoldItalic"
                else:
                    filename += "-Regular"
                done = False
                for license in possible_licenses:

                    # try two different URL patterns
                    url = "https://github.com/google/fonts/blob/main/%s/%s/static/%s.ttf?raw=true" % (
                        license, font_name.lower(), filename)
                    response = requests.get(url=url)

                    if not response.ok:
                        url = "https://github.com/google/fonts/blob/main/%s/%s/%s.ttf?raw=true" % (
                            license, font_name.lower(), filename)
                        response = requests.get(url=url)

                    if response.ok:
                        ttf_filename = filename + ".ttf"
                        woff2_filename = filename + ".woff2"
                        json_filename = filename + ".json"
                        ttf_path = os.path.join(output_subfolder, ttf_filename)
                        json_path = os.path.join(output_subfolder, json_filename)
                        woff2_path = os.path.join(output_subfolder, woff2_filename)

                        open(ttf_path, "wb").write(response.content)
                        source_url = "https://github.com/google/fonts/tree/main/%s/%s" % (license, font_name.lower())
                        glyph_count = self.extract(font_name, weight, style, ttf_path, json_path, woff2_path, url,
                                                   source_url)
                        self.logger.info(
                            "Downloading variant weight=%s, style=%s (%d codes) from %s" % (
                            weight, style, glyph_count, url))

                        done = True
                        completed += 1
                        possible_licenses = (license,)
                        break
                    else:
                        pass  # fetching the font file did not work, maybe try a different license
                if not done:
                    self.logger.warning("Unable to download variant weight=%s, style=%s" % (weight, style))

        if completed == 0:
            self.logger.error("No font variants processed.  Check the font name is correct.")
        else:
            self.__download_license_files(possible_licenses[0], font_name.lower(), output_subfolder)

    def __download_license_files(self, license, font_name_lower, output_subfolder):
        # try to download the various license files that may be associated with the font
        for filename in ["UFL.txt", "LICENSE.txt", "OFL.txt"]:
            url = "https://raw.githubusercontent.com/google/fonts/main/%s/%s/%s" % (license, font_name_lower, filename)
            response = requests.get(url)
            if response.ok:
                self.logger.info("Downloading license file from %s" % (url))
                with open(os.path.join(output_subfolder, filename), "wb") as of:
                    of.write(response.content)

    def extract(self, font_name, weight, style, ttf_path, json_path, woff2_path, download_url, source_url):
        """ Extract the width to height ratio for each glyph and convert to woff2"""

        # extract geometry...
        # https://stackoverflow.com/questions/4190667/how-to-get-width-of-a-truetype-font-character-in-1200ths-of-an-inch-with-python
        font = TTFont(ttf_path)
        cmap = font['cmap']
        t = cmap.getcmap(3, 1).cmap
        s = font.getGlyphSet()
        units_per_em = font['head'].unitsPerEm

        def unicodeEscape(codepoint):
            return str(chr(codepoint)).encode('unicode-escape').decode('ascii')

        glyph_widths = {}
        for code in t:
            if t[code] in s:
                ratio = s[t[code]].width / units_per_em
                glyph_widths[str(code)] = ratio

        # save geometry and metadata to a JSON formatted file
        o = {
            "download_url": download_url,
            "source_url": source_url,
            "name": font_name,
            "path": os.path.split(woff2_path)[1],
            "weight": weight,
            "style": style,
            "glyph_widths": glyph_widths
        }

        with open(json_path, "w") as of:
            of.write(json.dumps(o))

        # save the font back out as .woff2
        font.flavor = 'woff2'
        font.save(woff2_path)

        return len(glyph_widths)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.usage = """
        A program which downloads google fonts (with bold and italic variants if available) from github.com/google.
        Extract geometry to a simple JSON formatted file and create a copy in .woff2 format.
        """
    parser.add_argument("font_name", help="the name of the font, eg Raleway")
    parser.add_argument("output_folder", help="the name of the output folder.  "
                                              + "A subfolder named after the font will be created under this folder.")
    args = parser.parse_args()

    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)

    converter = Converter()
    converter.convert(args.font_name, args.output_folder)
