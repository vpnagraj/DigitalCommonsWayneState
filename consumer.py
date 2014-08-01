''' Consumer for Wayne State University -- Digital Commons '''

from lxml import etree
from xml.etree import ElementTree
from datetime import date, timedelta
import requests
from scrapi_tools import lint
from scrapi_tools.document import RawDocument, NormalizedDocument

TODAY = date.today()
YESTERDAY = TODAY - timedelta(10)
NAME = "DigitalCommonsWayneState"

def consume():
    base_url = 'http://digitalcommons.wayne.edu/do/oai/?verb=ListRecords&metadataPrefix=oai_dc&from='
    url = base_url + str(YESTERDAY) + 'T00:00:00Z'
    data = requests.get(url)
    doc =  etree.XML(data.content)

    print url

    namespaces = {'dc': 'http://purl.org/dc/elements/1.1/', 
                'oai_dc': 'http://www.openarchives.org/OAI/2.0/',
                'ns0': 'http://www.openarchives.org/OAI/2.0/'}

    records = doc.xpath('//oai_dc:record', namespaces=namespaces)

    xml_list = []
    for record in records:
        doc_id = record.xpath('ns0:header/ns0:identifier', namespaces=namespaces)[0].text
        record = ElementTree.tostring(record)
        record = '<?xml version="1.0" encoding="UTF-8"?>\n' + record
        xml_list.append(RawDocument({
                    'doc': record,
                    'source': NAME,
                    'doc_id': doc_id,
                    'filetype': 'xml'
                }))

    return xml_list

    ## TODO: fix if there are no records found... what would the XML look like?

def normalize(raw_doc, timestamp):
    raw_doc = raw_doc.get('doc')
    doc = etree.XML(raw_doc)

    namespaces = {'dc': 'http://purl.org/dc/elements/1.1/', 
                'oai_dc': 'http://www.openarchives.org/OAI/2.0/oai_dc/',
                'ns0': 'http://www.openarchives.org/OAI/2.0/'}

    contributors = doc.findall('ns0:metadata/oai_dc:dc/dc:creator', namespaces=namespaces)
    contributor_list = []
    for contributor in contributors:
        contributor_list.append(contributor.text)
    title = doc.findall('ns0:metadata/oai_dc:dc/dc:title', namespaces=namespaces)

    doc_id = doc.xpath('ns0:header/ns0:identifier', 
                                namespaces=namespaces)[0].text

    ## Using this for the abstract for now...
    ## TODO: make this an actual absttract maybe by going to the source...
    try: 
        description = doc.xpath('ns0:metadata/oai_dc:dc/dc:description', namespaces=namespaces)[0].text
    except IndexError:
        description = "No abstract available"

    normalized_dict = {
            'title': title[0].text,
            'contributors': contributor_list,
            'properties': {
                'abstract': description
            },
            'meta': {},
            'id': doc_id,
            'source': NAME,
            'timestamp': str(timestamp)
    }

    print normalized_dict
    return NormalizedDocument(normalized_dict)
        

if __name__ == '__main__':
    print(lint(consume, normalize))