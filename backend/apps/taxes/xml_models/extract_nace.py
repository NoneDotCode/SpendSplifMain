import xml.etree.ElementTree as ET
import json
import os

file_path = os.path.join(os.path.dirname(__file__), 'epo_ciselnik.xml')
tree = ET.parse(file_path)
root = tree.getroot()

data = []

for veta in root.findall('Veta'):
    data.append({
        'code': veta.attrib.get('c_nace'),
        'name': veta.attrib.get('naz_nace')
    })

with open('nace_codes.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
