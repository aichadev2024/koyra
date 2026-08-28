import zipfile
import xml.etree.ElementTree as ET
with zipfile.ZipFile('C:/DEV/koyra/Cahier_des_charges_Koyra_Distribution.docx') as docx:
    tree = ET.fromstring(docx.read('word/document.xml'))
    print('\n'.join(''.join(node.itertext()) for node in tree.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p')))
