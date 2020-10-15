from html.parser import HTMLParser


class CatalogParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.domain = ''
        self.tag_a_c = 0
        self.tag_a_p = 0
        self.data_urls = []
        self.data_pages = []
        self.tag_div = 0

    def handle_starttag(self, tag, attrs):
        # Getting pages of a category
        if tag == 'a':
            if ('id', 'r1') in attrs:
                for attr, value in attrs:
                    if self.tag_a_c == 0 and attr == 'href':
                        self.tag_a_c += 1
                        # Checking for doubles and it is catalog and it isn't part of filters
                        if self.data_pages.count(self.domain + value) == 0 and value[:9] == '/category' and value[-9:] != '#filters/':
                            self.data_pages.append(self.domain + value)
            # Getting subcategory
            if 'product-name' in str(attrs) and self.tag_div > 0:
                if ('rel', 'rel nofollow') not in attrs:
                    if ('class', 'clickFilter') not in attrs:
                        for attr, value in attrs:
                            if attr == 'href' and self.tag_a_c == 0:
                                self.tag_a_c += 1
                                if self.data_pages.count('https:' + value) == 0:
                                    if value[:8] != '/product':
                                        if value[1] != '/':
                                            self.data_pages.append('https:/' + value)
                                        else:
                                            self.data_pages.append('https:' + value)
            # Getting links to products
            if 'productLink' in str(attrs):
                for attr, value in attrs:
                    if attr == 'href' and self.tag_a_p == 0:
                        self.tag_a_p += 1
                        if self.data_urls.count(self.domain + value) == 0:
                            self.data_urls.append(self.domain + value)
        if tag == 'div':
            if 'container-item' in str(attrs):
                self.tag_div += 1

    def handle_endtag(self, tag):
        if tag == 'a' and self.tag_a_c:
            self.tag_a_c -= 1
        if tag == 'a' and self.tag_a_p:
            self.tag_a_p -= 1
        if tag == 'div' and self.tag_div > 0:
            self.tag_div -= 1
