import pygame
import xml.etree.ElementTree as ET
from tools.arrow_handler import DEFAULT_SPRITE_KEYS

FNF_DIRECTION_COLOR = {
    'left':   'purple',
    'down':   'blue',
    'up':     'green',
    'right':  'red'
}

def load_sprites_from_xml(image_path, xml_path, scale=1.0):
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

        frame = image.subsurface(pygame.Rect(x, y, w, h)).copy()
        if scale != 1.0:
            frame = pygame.transform.smoothscale(
                frame,
                (int(w * scale), int(h * scale))
            )
        raw_frames[name] = frame

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

def load_character_sprites_from_xml(image_path, xml_path, scale=1.0):
    import pygame
    import xml.etree.ElementTree as ET

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

        # Check for 'rotated="true"'
        rotated = sub.attrib.get('rotated', 'false') == 'true'
        if rotated:
            frame = image.subsurface(pygame.Rect(x, y, w, h)).copy()
            frame = pygame.transform.rotate(frame, 90)  # 90 degrees CCW
        else:
            frame = image.subsurface(pygame.Rect(x, y, w, h)).copy()

        if scale != 1.0:
            frame = pygame.transform.smoothscale(
                frame,
                (int(frame.get_width() * scale), int(frame.get_height() * scale))
            )
        frames[name] = frame

    return frames

def load_character_frames(name_prefix, frames_dict, anims=('idle', 'singLEFT', 'singDOWN', 'singUP', 'singRIGHT')):
    """
    Loads multi-frame character animations from FNF-style XML-named frames.
    Supports names like 'Down0000', 'Left0001', 'Idle0003', etc.
    """
    # Mapping from loader anim name to FNF XML base
    FNF_ANIM_MAP = {
        'idle': 'Idle',
        'singLEFT': 'Left',
        'singDOWN': 'Down',
        'singUP': 'Up',
        'singRIGHT': 'Right'
    }

    anim_map = {}
    for anim in anims:
        base = FNF_ANIM_MAP.get(anim, anim)
        frames = []
        i = 0
        while True:
            # Look for FNF style names like 'Down0000', 'Left0004', etc.
            key = f"{base}{i:04d}"
            if key in frames_dict:
                frames.append(frames_dict[key])
                i += 1
            else:
                break
        if frames:
            anim_map[anim] = frames
    return anim_map