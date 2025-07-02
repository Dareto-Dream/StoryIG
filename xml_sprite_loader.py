import pygame
import xml.etree.ElementTree as ET

def load_sprites_from_xml(image_path, xml_path):
    image = pygame.image.load(image_path).convert_alpha()
    tree = ET.parse(xml_path)
    root = tree.getroot()

    frames = {}
    for sub in root.findall('SubTexture'):
        name = sub.attrib['name']
        x = int(sub.attrib['x'])
        y = int(sub.attrib['y'])
        w = int(sub.attrib['width'])
        h = int(sub.attrib['height'])

        frames[name] = image.subsurface(pygame.Rect(x, y, w, h))

    return frames