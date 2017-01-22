__author__ = 'Praneetha'

# http://stackoverflow.com/questions/25049962/is-encoding-is-an-invalid-keyword-error-inevitable-in-python-2-x

import io
import audit
import sqlite3
import sql_schema
import xml.etree.ElementTree as ET
import unicodecsv


FILENAME = 'SanFranciscoSMALL.OSM'
DATA = []
CSV_FILES = ['nodes.csv', 'nodes_tags.csv', 'ways.csv', 'ways_tags.csv', 'ways_nodes.csv']
AUDIT_KEYS = {'phone': audit.audit_phones,
              'addr:city': audit.audit_street,
              'source': audit.audit_sources}


def shape_element(element):
    if element.tag == 'node':
        csv_format = dict.fromkeys(sql_schema.schema_keys['nodes'])
        csv_format['type'] = element.tag
        for k in csv_format:
            if k != 'type':
                csv_format[k] = element.attrib[k]
        DATA.append(csv_format)

        for tag in element.iter('tag'):
            csv_format = dict.fromkeys(sql_schema.schema_keys['nodes_tags'])
            csv_format['type'] = 'nodes_tag'
            csv_format['key'] = tag.attrib['k']
            csv_format['id'] = element.attrib['id']
            if tag.attrib['k'] in AUDIT_KEYS:
                func = AUDIT_KEYS[tag.attrib['k']]
                csv_format['value'] = func(tag.attrib['v'])
            else:
                csv_format['value'] = tag.attrib['v']
            DATA.append(csv_format)

    elif element.tag == 'way':
        csv_format = dict.fromkeys(sql_schema.schema_keys['ways'])
        csv_format['type'] = 'way'
        for k in csv_format:
            if k != 'type':
                csv_format[k] = element.attrib[k]
        DATA.append(csv_format)

        for tag in element.iter('tag'):
            csv_format = dict.fromkeys(sql_schema.schema_keys['ways_tags'])
            csv_format['type'] = 'ways_tag'
            csv_format['key'] = tag.attrib['k']
            csv_format['id'] = element.attrib['id']
            if tag.attrib['k'] in AUDIT_KEYS:
                func = AUDIT_KEYS[tag.attrib['k']]
                csv_format['value'] = func(tag.attrib['v'])
            else:
                csv_format['value'] = tag.attrib['v']
            DATA.append(csv_format)

        pos = 0
        for node in element.iter('nd'):
            csv_format = dict.fromkeys(sql_schema.schema_keys['ways_nodes'])
            csv_format['id'] = element.attrib['id']
            csv_format['node_id'] = node.attrib['ref']
            csv_format['position'] = pos
            csv_format['type'] = 'ways_node'
            pos += 1
            DATA.append(csv_format)


def process_map(filename):
    print 'Processing XML...'
    for _, element in ET.iterparse(filename):
        if element.tag == 'node' or element.tag == 'way':
            shape_element(element)

    print 'Finished Processing. Load to CSV files'


def convert_to_csv():
    for c_file in CSV_FILES:
        file_data = [row for row in DATA if ('type' in row) and (row['type'] == c_file[:-5])]
        for row in file_data:
            DATA.remove(row)
        if 'tag' not in c_file:
            for row in file_data:
                row.pop('type')
        with io.open(c_file, 'wb') as csv_file:
            csv_writer = unicodecsv.writer(csv_file, sql_schema.schema_keys[c_file[:-4]])
            header = []
            for key in sql_schema.schema_keys[c_file[:-4]]:
                if key in file_data[0].keys():
                    header.append(key.decode('utf-8'))
            csv_writer.writerow(header)
            for i, row in enumerate(file_data):
                uni_row = []
                for v in sql_schema.schema_keys[c_file[:-4]]:
                    if v in row:
                        if isinstance(row[v], unicode):
                            if c_file == 'ways_nodes.csv': print type(row[v])
                            uni_row.append(row[v])
                        elif isinstance(row[v], int):
                            uni_row.append(str(row[v]).decode('utf-8'))
                        else:
                            uni_row.append(row[v].decode('utf-8'))
                csv_writer.writerow(uni_row)
        print 'Loaded '+c_file


def csv_to_sql():

    print "\nLoad to SQLite database..."
    db = sqlite3.connect(FILENAME[:-4]+".db")
    cur = db.cursor()

    load_table(cur, sql_schema.nodes, 'nodes.csv')
    load_table(cur, sql_schema.nodes_tags, 'nodes_tags.csv')
    load_table(cur, sql_schema.ways, 'ways.csv')
    load_table(cur, sql_schema.ways_tags, 'ways_tags.csv')
    load_table(cur, sql_schema.ways_nodes, 'ways_nodes.csv')

    db.commit()
    print 'Done!'


def load_table(cur, table, t_csv):
    cur.execute(table)
    with io.open(t_csv, 'rb') as csv_file:
        csv_reader = unicodecsv.reader(csv_file, encoding='utf-8')
        header = next(csv_reader)
        column_num = ','.join('?' for i in range(len(header)))
        for row in csv_reader:
            cur.execute("INSERT INTO " + t_csv[:-4] + " VALUES ("+column_num+");", row)
    print "Loaded nodes.csv into SQLite db"


process_map(FILENAME)
convert_to_csv()
#csv_to_sql()

