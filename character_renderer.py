import pygame
import os

def load_image_safe(path):
    try:
        return pygame.image.load(path).convert_alpha()
    except Exception as e:
        print(f"[!] Failed to load {path}: {e}")
        return None

def render_character(page, base_path="assets/characters"):
    character = page.get("character")
    if not character:
        return None

    char_path = os.path.join(base_path, character)

    # === Cassian Modular (face_parts) ===
    if page.get("face_parts") and "pose" in page:
        pose = load_image_safe(os.path.join(char_path, "Poses", f"{page['pose']}.png"))
        base = load_image_safe(os.path.join(char_path, "Expressions", "base.png"))
        if not pose or not base:
            return None
        for part, folder in zip(page['face_parts'], ["eyes", "eyebrows", "mouth", "nose"]):
            part_path = os.path.join(char_path, "Expressions", folder, f"{part}.png")
            overlay = load_image_safe(part_path)
            if overlay:
                base.blit(overlay, (0, 0))
        final = pygame.Surface(pose.get_size(), pygame.SRCALPHA)
        final.blit(pose, (0, 0))
        final.blit(base, (0, 0))
        return final

    # === Dual Pose + Face (e.g. bodyL, bodyR + face) ===
    elif all(k in page for k in ("pose_left", "pose_right", "face")):
        left = load_image_safe(os.path.join(char_path, f"{page['pose_left']}.png"))
        right = load_image_safe(os.path.join(char_path, f"{page['pose_right']}.png"))
        face = load_image_safe(os.path.join(char_path, f"{page['face']}.png"))
        if not all([left, right, face]):
            return None
        pose = pygame.Surface(left.get_size(), pygame.SRCALPHA)
        pose.blit(left, (0, 0))
        pose.blit(right, (0, 0))
        pose.blit(face, (0, 0))
        return pose

    # === Single Pose + Face ===
    elif all(k in page for k in ("pose", "face")):
        pose = load_image_safe(os.path.join(char_path, f"{page['pose']}.png"))
        face = load_image_safe(os.path.join(char_path, f"{page['face']}.png"))
        if not pose or not face:
            return None
        final = pygame.Surface(pose.get_size(), pygame.SRCALPHA)
        final.blit(pose, (0, 0))
        final.blit(face, (0, 0))
        return final

    # === Single Image ===
    elif "image" in page:
        return load_image_safe(page["image"])

    # === Custom Mode? ===
    elif "custom_parts" in page:
        surf = pygame.Surface((800, 800), pygame.SRCALPHA)
        for part in page["custom_parts"]:
            part_img = load_image_safe(os.path.join(char_path, part["index"]))
            if part_img:
                surf.blit(part_img, (part["x"], part["y"]))
        return surf

    return None
