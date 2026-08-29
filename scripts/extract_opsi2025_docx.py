from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as ET

path = Path('/home/ubuntu/upload/OPSI2025.docx')
ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
with ZipFile(path) as archive:
    root = ET.fromstring(archive.read('word/document.xml'))

print('DOCUMENT_XML_EXTRACTED')
for i, paragraph in enumerate(root.findall('.//w:body/w:p', ns), start=1):
    text = ''.join(node.text or '' for node in paragraph.findall('.//w:t', ns)).strip()
    if text:
        print(f'P{i}: {text}')

tables = root.findall('.//w:body/w:tbl', ns)
print('TABLES', len(tables))
for ti, table in enumerate(tables, start=1):
    print(f'\nTABLE {ti}')
    for row in table.findall('./w:tr', ns):
        cells = []
        for cell in row.findall('./w:tc', ns):
            text = ''.join(node.text or '' for node in cell.findall('.//w:t', ns)).strip()
            cells.append(text)
        print(' | '.join(cells))
