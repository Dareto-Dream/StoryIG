import pygame
import xml.etree.ElementTree as ET
from tools.arrow_handler import DEFAULT_SPRITE_KEYS

FNF_DIRECTION_COLOR = {
    'left':   'purple',
    'down':   'blue',
    'up':     'green',
    'right':  'red'
}

def load_sprites_from_xml(image_path, xml_path):
    image = pygame.image.load(image_path).convert_alpha()
    tree = ET.parse(xml_path)
    root = tree.getroot()

    raw_frames = {}
    for sub in root.findall('SubTexture'):
        name = sub.attrib['name']
        x = int(sub.attrib['x'])
        y = int(sub.attrib['y'])
        w = int(sub.attrib['width'])
        h = int(sub.attrib['height'])

        raw_frames[name] = image.subsurface(pygame.Rect(x, y, w, h)).copy()

    # Convert to arrow_frames structure
    arrow_frames = {}
    for dir in DEFAULT_SPRITE_KEYS:
        color = FNF_DIRECTION_COLOR[dir]
        arrow_frames[dir] = {
            'idle': raw_frames[DEFAULT_SPRITE_KEYS[dir]['idle']],
            'flash': raw_frames[DEFAULT_SPRITE_KEYS[dir]['flash']],
            'hold': raw_frames[DEFAULT_SPRITE_KEYS[dir]['hold']],
            'hold_piece': raw_frames.get(f"{color} hold piece instance 10000"),
            'hold_end': raw_frames.get(f"{color} hold end instance 10000"),
        }

    # Optionally include raw XML access
    arrow_frames['_raw'] = raw_frames

    return arrow_frames


def load_character_frames(name_prefix, frames_dict, anims=('idle', 'singLEFT', 'singDOWN', 'singUP', 'singRIGHT')):
    """
    Loads multi-frame character animations from XML-named frames.
    Example keys: 'tiffany_singLEFT_0', 'tiffany_singLEFT_1', ...
    """
    anim_map = {}
    for anim in anims:
        frames = []
        i = 0
        while True:
            key = f"{name_prefix}_{anim}_{i}"
            if key in frames_dict:
                frames.append(frames_dict[key])
                i += 1
            else:
                break
        if frames:
            anim_map[anim] = frames
    return anim_map