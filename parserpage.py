from html.parser import HTMLParser
import urllib.request
import os


class PageParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.domain = ''
        self.recording = 0
        self.span = 0
        self.table = 0
        self.td = False
        self.data = []
        self.sku = ''
        self.tbl = []
        self.desc = 0
        self.id = ''
        self.pro_id = 0
        self.desc_text = []
        self.img = []
        self.h1 = 0
        self.h1_text = ''

    def handle_starttag(self, tag, attrs):
        # Getting photos
        if tag == "img":
            if 'bb' in str(attrs):
                self.recording += 1
                for attr, value in attrs:
                    if attr == 'src':
                        try:
                            urllib.request.urlretrieve(self.domain + value, 'images/' + os.path.split(value)[1])
                            self.img.append(('images/' + os.path.split(value)[1]))
                        except urllib.error.URLError as e:
                            if not hasattr(e, "code"):
                                raise

        # Getting the span with SKU of product
        if tag == "span":
            if 'cod' in str(attrs):
                self.span += 1

        # Getting the table with attributes
        if tag == "table":
            if 'reviewtab' in str(attrs):
                self.table += 1

        # Getting the start of a table with attributes
        if tag == 'td' and self.table > 0:
            self.td = True

        # Getting description and SKU
        if tag == 'div':
            if 'tab-description' in str(attrs):
                self.desc += 1
            if 'pro_id' in str(attrs):
                self.pro_id += 1

        # Getting the title of product
        if tag == 'h1':
            if 'titleopus' in str(attrs):
                self.h1 += 1

    # Getting data from internal tags
    def handle_endtag(self, tag):
        if tag == 'img' and self.recording:
            self.data.append(self.img)
            self.recording -= 1

        if tag == 'span' and self.span > 0:
            self.span -= 1

        if tag == 'table' and self.table > 0:
            self.data.append(self.tbl)
            self.table -= 1

        if tag == 'td' and self.table > 0:
            self.td = False

        if tag == 'div' and self.pro_id > 0:
            self.pro_id -= 1

        if tag == 'div' and self.desc > 0:
            self.data.append(self.desc_text)
            self.desc -= 1

        if tag == 'h1' and self.h1 > 0:
            self.h1 -= 1

    def handle_data(self, data):
        if self.table:
            if self.td:
                self.tbl.append(data)

        if self.span:
            self.sku = data.split(': ')[1]
            self.data.append([data.split(': ')[1]])

        if self.desc:
            self.desc_text.append(data)

        if self.pro_id:
            self.id = data
            self.data.append([data])

        if self.h1:
            self.h1_text = data

    def handle_decl(self, data):
        if self.recording or self.span or self.table:
            if data == '' and data != "\n":
                self.data.append(data)

    def add_to_sublist(self, name, array):
        for sublist in self.data:
            if name in sublist:
                #sublist.append(array)
                break
