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

import sys
import os.path
import sqlite3

conn = sqlite3.connect('font_dimensions.db')

from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._c_m_a_p import CmapSubtable

suffix_map = {
    "-Bold.ttf": ("bold", "normal"),
    "-BoldItalic.ttf": ("bold", "italic"),
    "-Italic.ttf": ("normal", "italic"),
    "-Regular.ttf": ("normal", "normal")
}

def convert(font_name, ttf_path, license):
    for suffix in suffix_map:
        if ttf_path.endswith(suffix):
            (weight, style) = suffix_map[suffix]
            ttf_filename = os.path.split(ttf_path)[1]

            # https://stackoverflow.com/questions/4190667/how-to-get-width-of-a-truetype-font-character-in-1200ths-of-an-inch-with-python
            font = TTFont(ttf_path)
            cmap = font['cmap']
            t = cmap.getcmap(3, 1).cmap
            s = font.getGlyphSet()
            units_per_em = font['head'].unitsPerEm
            table_name = font_name + "_" + weight + "_" + style

            ratios = []
            count = 0
            for code in t:
                if t[code] in s:
                    ratio = s[t[code]].width / units_per_em
                    ratios.append((code, ratio))
                    count += 1

            conn.execute("CREATE TABLE %s(char VARCHAR,ratio VARCHAR)" % (table_name))
            conn.commit()

            for (code, ratio) in ratios:
                ins = 'INSERT INTO %s VALUES("%s", "%.3f")' % (table_name, str(code), ratio)
                conn.execute(ins)

            conn.execute(
                'INSERT INTO FONTS VALUES("%s","%s","%s","%s","%s")' % (font_name, weight, style, table_name, license))
            conn.commit()
            print("%s -> %s %s (%d glyphs)" % (ttf_path, table_name, license, count))


def scanFolder(license,dir):
    try:
        conn.execute(
            "CREATE TABLE FONTS(name VARCHAR, weight VARCHAR, style VARCHAR, tablename VARCHAR, license VARCHAR)")
    except:
        pass

    for folder in os.listdir(dir):
        subfolder = os.path.join(dir, folder)
        if not os.path.isdir(subfolder):
            continue
        for file in os.listdir(subfolder):
            filepath = os.path.join(subfolder, file)
            try:
                convert(folder, filepath, license)
            except Exception as ex:
                print("Error converting %s: %s" % (filepath, str(ex)))


if __name__ == '__main__':
    input_folder = sys.argv[1]
    for license in ["ufl","ofl","apache"]:
        license_folder = os.path.join(input_folder,license)
        scanFolder(license,license_folder)
