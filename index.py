import os, sys
import urllib.request
import urllib.parse
import base64
import parsercatalog as pc
import parserpage as pp
import db
import json
import http.client  # or http.client if you're on Python 3

http.client._MAXHEADERS = 1000

links = []


# # parser for pages
# def parser_page(url):
#     os.makedirs('images', 755, True)
#     # The class Parser (for page) is created
#     parser = pp.PageParser()
#     parsed_url = urllib.parse.urlparse(url)
#     parser.domain = parsed_url.scheme + '://' + parsed_url.netloc
#     # The class Parser is run
#     response = urllib.request.urlopen(url)
#     data = response.read()
#     text = data.decode('utf-8')
#     parser.feed(text)
#
#     # Results are being gotten from Parser
#     result = parser.data
#
#     # It is debugged information (uncomment when you have to view which the parameter
#     # "description" you get from the site)
#     # -------------------------------------------------------------------------------
#     # for x in range(len(parser.data)):
#     #     key = parser.data[x][0]
#     #     for i in range(1, len(parser.data[x])):
#     #         str = ''
#     #         for z in range(len(parser.data[x][i])):
#     #             if key == 'description':
#     #                 str += parser.data[x][i][z] + " "
#     #         print((key + ' - ' + str))
#     # -------------------------------------------------------------------------------
#
#
#     parser.close()
#     return result

# Parser for catalogs
def parser_catalog(url):
    urls = []
    pages = []
    pages.append(url)
    # The class Parser (for catalogs) is created
    parser = pc.CatalogParser()
    parsed_url = urllib.parse.urlparse(url)
    parser.domain = parsed_url.scheme + '://' + parsed_url.netloc
    parser.data_pages.extend(pages)

    i = 0

    # The list of pages of category and the list of links of products are being created
    while i < len(pages):
        parser.data_urls = urls
        response = urllib.request.urlopen(pages[i])
        data = response.read()
        text = data.decode('utf-8')
        # The class Parser is run
        parser.feed(text)
        # Results are being gotten from Parser
        urls = parser.data_urls
        pages = parser.data_pages
        i += 1
    parser.close()

    # print(urls)
    return urls


def run():
    if len(sys.argv) != 2:
        return

    # The connected to DBs is being created
    sql = db.DataBases('db_host', 'db_username', 'db_password', 'db_name', 'db_port')
    sql.connect()
    sql_aws = db.DataBases('gikinstance.cqvojff2wn25.eu-central-1.rds.amazonaws.com', 'gik_db_user1', 'Vfuytpbz10#', 'gik_shop_db1', '3306')
    sql_aws.connect()

    # If we can't create the connection to DB, we exit from the function
    if sql.mydb == False:
        return

    # It gets arguments from the command line and runs the function "Parser_catalog"
    urls = parser_catalog(sys.argv[1])

    i = 0

    # The class Parser (for pages)
    parser = pp.PageParser()
    parsed_url = urllib.parse.urlparse(sys.argv[1])
    parser.domain = parsed_url.scheme + '://' + parsed_url.netloc

    # The queries to DB was created
    query_update_desc = "UPDATE `oc_product_description` SET `description` = %s WHERE `product_id`=%s"
    query_update_img = "UPDATE `oc_product` SET `image` = %s WHERE `product_id`=%s"
    query_insert_img = "INSERT INTO `oc_product_image` (`product_id`, `image`, `sort_order`) VALUE (%s, %s, %s)"
    #query = "INSERT INTO `oc_products` (id, name, cod, img, sku, description, attributes) VALUE (%s, %s, %s, %s, %s, %s, %s)"

    # The processing of array links of products is being started
    print(len(urls))
    while i < len(urls):
        # We have to delete old data from vars
        parser.data = []
        parser.img = []
        parser.desc_text = []
        parser.tbl = []
        response = urllib.request.urlopen(urls[i])
        data = response.read()
        text = data.decode('utf-8')
        parser.feed(text)
        full_desc = ''
        # The description is being created
        for text in parser.desc_text:
            if len(str(text).strip()) > 3:
                full_desc = full_desc + '<p>' + str(text).strip() + '</p>'
        print(parser.sku)

        # Sometimes on the site of dealer the SKU isn't and we have to check it
        if parser.sku != '':
            query_select_id = "SELECT `product_id` FROM `oc_product` WHERE `sku`='" + str(parser.sku) + "'"
            data = sql_aws.query(query_select_id, '', 'S')
            # If we have the product in the shop
            if len(data):
                # All data about product is being printed
                print(data[0][0])
                # Update the description
                sql_aws.query(query_update_desc, (full_desc, str(data[0][0])), 'U')
                # The main picture is being updated
                if len(parser.img) > 0:
                    sql_aws.query(query_update_img, ('catalog/product/' + str(parser.img[0]), str(data[0][0])), 'U')
                # The additional pictures are being updated or added
                if len(parser.img) > 1:
                    for z in range(len(parser.img) - 1):
                        print(str(data[0][0]), 'catalog/product/' + parser.img[z + 1])
                        sql_aws.query(query_insert_img, (str(data[0][0]), 'catalog/product/' + str(parser.img[z + 1]), '0'), 'I')
        print('-----------------------------------------------------------------------')
        i += 1

        # Print the info about the progress of working
        print(str(i) + ' was done from ' + str(len(urls)))

    parser.close()


# Point of entry
run()
