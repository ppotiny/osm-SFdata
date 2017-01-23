__author__ = 'Praneetha'

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
    """Cleans the elements that need to be cleaned and places them in a
    dictionary to be written in a csv"""
    if element.tag == 'node':
        csv_format = dict.fromkeys(sql_schema.schema_keys['nodes'])  # Creates dictionary from list of desired keys
        csv_format['type'] = element.tag  # In this case, the type is 'node'
        for k in csv_format:
            # 'type' is not an XML attribute of this element. Don't check for it.
            if k != 'type':
                csv_format[k] = element.attrib[k]
        DATA.append(csv_format)

        # Iterates through the tags of the current node
        for tag in element.iter('tag'):
            csv_format = dict.fromkeys(sql_schema.schema_keys['nodes_tags'])
            csv_format['type'] = 'nodes_tag'
            csv_format['key'] = tag.attrib['k']
            csv_format['id'] = element.attrib['id']
            if tag.attrib['k'] in AUDIT_KEYS:
                #  If this key can be audited, audit it before passing it to the dictionary
                func = AUDIT_KEYS[tag.attrib['k']]
                csv_format['value'] = func(tag.attrib['v'])
            else:
                csv_format['value'] = tag.attrib['v']
            DATA.append(csv_format)

    # Similar to nodes
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

        pos = 0  # The first node in a way, is at position 0
        for node in element.iter('nd'):
            csv_format = dict.fromkeys(sql_schema.schema_keys['ways_nodes'])
            csv_format['id'] = element.attrib['id']  # This id refers to the way, not the node
            csv_format['node_id'] = node.attrib['ref']  # This id refers to the actual node
            csv_format['position'] = pos
            csv_format['type'] = 'ways_node'
            pos += 1
            DATA.append(csv_format)


def process_map(filename):
    """Iterates through every element in the file and shapes the
    specified elements"""
    print 'Processing XML...'
    for _, element in ET.iterparse(filename):
        if element.tag == 'node' or element.tag == 'way':
            shape_element(element)

    print 'Finished Processing. Load to CSV files'


def convert_to_csv():
    """Converts all strings into unicode and puts each modified
    row into the desired unicodecsv"""
    for c_file in CSV_FILES:
        # Selects all rows where type belongs to a specific file (e.g. - node --> nodes.csv)
        file_data = [row for row in DATA if ('type' in row) and (row['type'] == c_file[:-5])]
        for row in file_data:
            DATA.remove(row)  # Remove selected rows from DATA. We no longer need to iterate through them

        # We only need a 'type' column to differentiate between nodes_tags and ways_tags
        # Remove 'type' from the current rows if they don't belong to those files
        if 'tag' not in c_file:
            for row in file_data:
                row.pop('type')

        with io.open(c_file, 'wb') as csv_file:
            csv_writer = unicodecsv.writer(csv_file, sql_schema.schema_keys[c_file[:-4]])

            # Put the keys in the header of the csv.
            header = []
            for key in sql_schema.schema_keys[c_file[:-4]]:  # Specifies order of keys
                if key in file_data[0].keys():  # Only get keys that are actually in the data
                    header.append(key.decode('utf-8'))  # Converts to unicode
            csv_writer.writerow(header)

            # Converts all data into unicode and writes to the csv
            for i, row in enumerate(file_data):
                uni_row = []  # Holds the row with unicode values
                for v in sql_schema.schema_keys[c_file[:-4]]:
                    if v in row:
                        if isinstance(row[v], unicode):  # For unicode, add it as is
                            uni_row.append(row[v])
                        elif isinstance(row[v], int):  # For integers, convert it to a string then to unicode, then add
                            uni_row.append(str(row[v]).decode('utf-8'))
                        else:  # If it's a string, convert it to unicode, then add
                            uni_row.append(row[v].decode('utf-8'))
                csv_writer.writerow(uni_row)  # Write the modified row to the csv

        print 'Loaded '+c_file


def csv_to_sql():
    """Puts each CSV file into an SQLite database"""
    print "\nLoad to SQLite database..."
    db = sqlite3.connect(FILENAME[:-4]+".db")
    cur = db.cursor()

    # Loads each csv into the specified table
    load_table(cur, sql_schema.nodes, 'nodes.csv')
    load_table(cur, sql_schema.nodes_tags, 'nodes_tags.csv')
    load_table(cur, sql_schema.ways, 'ways.csv')
    load_table(cur, sql_schema.ways_tags, 'ways_tags.csv')
    load_table(cur, sql_schema.ways_nodes, 'ways_nodes.csv')

    db.commit()  # Commits these changes to the database
    print 'Done!'


def load_table(cur, table, t_csv):
    """Loads each row of the csv into the table"""
    cur.execute(table)
    with io.open(t_csv, 'rb') as csv_file:
        csv_reader = unicodecsv.reader(csv_file, encoding='utf-8')
        header = next(csv_reader)  # Gets the first row

        # Creates a string of 'x' question marks, where 'x' is the number of values in one row
        column_num = ','.join('?' for i in range(len(header)))

        # Replaces each question mark with a row value. Then does an SQL insert into the database
        for row in csv_reader:
            cur.execute("INSERT INTO " + t_csv[:-4] + " VALUES ("+column_num+");", row)

    print "Loaded nodes.csv into SQLite db"


process_map(FILENAME)
convert_to_csv()
#csv_to_sql()

