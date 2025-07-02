import pygame
import json
import os
from pygame.locals import *

# === Config ===
SCREEN_WIDTH, SCREEN_HEIGHT = 1500, 1000
CHARACTER = "hanami"
ASSET_PATH = f"assets/characters/{CHARACTER}"
POSES_PATH = f"{ASSET_PATH}/Poses"
EXPRESSIONS_PATH = f"{ASSET_PATH}/Expressions"
STORY_PATH = "story.json"
POSE_MAP_PATH = "pose_face_map.json"

# === Load JSON ===
def load_story():
    with open(STORY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_story(data):
    with open(STORY_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def load_pose_map():
    return json.load(open(POSE_MAP_PATH)) if os.path.exists(POSE_MAP_PATH) else {}

def save_pose_map(data):
    with open(POSE_MAP_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

# === Load available parts ===
def get_files():
    if CHARACTER == "cassian":
        poses = sorted(f.split(".")[0] for f in os.listdir(POSES_PATH) if f.endswith(".png"))
        eyes = sorted(f.split(".")[0] for f in os.listdir(f"{EXPRESSIONS_PATH}/eyes"))
        brows = sorted(f.split(".")[0] for f in os.listdir(f"{EXPRESSIONS_PATH}/eyebrows"))
        mouths = sorted(f.split(".")[0] for f in os.listdir(f"{EXPRESSIONS_PATH}/mouth"))
        noses = sorted(f.split(".")[0] for f in os.listdir(f"{EXPRESSIONS_PATH}/nose"))
        return poses, eyes, brows, mouths, noses
    else:
        files = os.listdir(ASSET_PATH)
        poses = sorted(set(f.split(".")[0] for f in files if f[0].isdigit() and "-" not in f and not f.endswith("r.png")))
        right_poses = sorted(set(f.split(".")[0] for f in files if f.endswith("r.png")))
        faces = sorted(set(f.split(".")[0] for f in files if f[0].isalpha() and len(f.split(".")[0]) == 1))
        return poses, right_poses, faces

# === Assemble Cassian's face ===
def get_cassian_face(eye, brow, mouth, nose):
    base = pygame.image.load(f"{EXPRESSIONS_PATH}/base.png").convert_alpha()
    for part, folder in zip([eye, brow, mouth, nose], ["eyes", "eyebrows", "mouth", "nose"]):
        path = f"{EXPRESSIONS_PATH}/{folder}/{part}.png"
        if os.path.exists(path):
            overlay = pygame.image.load(path).convert_alpha()
            base.blit(overlay, (0, 0))
    return base

# === Render composite image ===
def get_combined_image(mode, pose, face=None, right_pose=None, parts=None):
    try:
        if mode == 4:
            pose_img = pygame.image.load(f"{POSES_PATH}/{pose}.png").convert_alpha()
            face_img = get_cassian_face(*parts)
        elif mode == 1:
            return pygame.image.load(f"{ASSET_PATH}/{pose}.png").convert_alpha()
        else:
            left = pygame.image.load(f"{ASSET_PATH}/{pose}.png").convert_alpha()
            right = pygame.image.load(f"{ASSET_PATH}/{right_pose}.png").convert_alpha()
            pose_img = pygame.Surface(left.get_size(), pygame.SRCALPHA)
            pose_img.blit(left, (0, 0))
            pose_img.blit(right, (0, 0))
            face_img = pygame.image.load(f"{ASSET_PATH}/{face}.png").convert_alpha()

        final = pygame.Surface(pose_img.get_size(), pygame.SRCALPHA)
        final.blit(pose_img, (0, 0))
        final.blit(face_img, (0, 0))
        return final
    except Exception as e:
        print(f"[!] Failed to load image: {e}")
        return None

# === Main Tool ===
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Pose Maker")
    font = pygame.font.Font(None, 28)

    story = load_story()
    pose_map = load_pose_map()
    current_page = 0
    mode = 1

    custom_files = sorted([f for f in os.listdir(ASSET_PATH) if f.endswith(".png")])
    custom_file_idx = 0
    selected_custom = 0
    custom_categories = ["bodyL", "bodyR", "head", "eyes", "eyebrows", "mouth", "accessory"]

    if CHARACTER == "cassian":
        poses, eyes, brows, mouths, noses = get_files()
        eye_idx, brow_idx, mouth_idx, nose_idx = 0, 0, 0, 0
    else:
        poses, right_poses, faces = get_files()
        if not faces:
            faces = ["_"]  # dummy entry so indexing doesn't break
        pose_idx, right_pose_idx, face_idx = 0, 0, 0

    pose_idx = 0
    clock = pygame.time.Clock()

    while True:
        screen.fill((30, 30, 30))
        page = story[current_page]
        text = page.get("text", "")

        pose = poses[pose_idx]

        if mode == 0:
            page.setdefault("custom_parts", [])
            for i, part in enumerate(page["custom_parts"]):
                try:
                    fname = part["index"]
                    x = part["x"]
                    y = part["y"]
                    img_path = os.path.join(ASSET_PATH, fname)
                    if os.path.exists(img_path):
                        img = pygame.image.load(img_path).convert_alpha()
                        screen.blit(img, (50 + x, 50 + y))
                    else:
                        print(f"[!] MISSING FILE: {img_path}")
                except Exception as e:
                    print(f"[!] Failed to render part {part}: {e}")

            screen.blit(font.render("Super Custom Mode", True, (255, 255, 0)), (400, 110))
            if page["custom_parts"]:
                part = page["custom_parts"][selected_custom]
                screen.blit(font.render(
                    f"Selected: {part['category']} [{part['index']}] @ ({part['x']}, {part['y']})",
                    True, (255, 255, 255)
                ), (400, 140))

        elif mode == 4:
            parts = [eyes[eye_idx], brows[brow_idx], mouths[mouth_idx], noses[nose_idx]]
            preview = get_combined_image(mode=4, pose=pose, parts=parts)
            if preview:
                screen.blit(preview, (50, 50))

        elif mode == 1:
            face = faces[face_idx]
            preview = get_combined_image(mode=1, pose=pose, face=face)
            if preview:
                screen.blit(preview, (50, 50))

        else:
            face = faces[face_idx]
            right_pose = right_poses[right_pose_idx]
            preview = get_combined_image(mode=2, pose=pose, face=face, right_pose=right_pose)
            if preview:
                screen.blit(preview, (50, 50))

        # Info
        screen.blit(font.render(f"Page {page['page']}: {text}", True, (255, 255, 255)), (400, 80))
        screen.blit(font.render("0–4 = Mode | Enter = Save | Space = Save Preset | PgUp/Dn = Change Page", True,
                                (200, 200, 200)), (10, 920))
        screen.blit(
            font.render("←/→ = Change | WASD = Move (custom) | +/- = Add/Remove (custom)", True, (200, 200, 200)),
            (10, 950))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == QUIT:
                save_story(story)
                save_pose_map(pose_map)
                pygame.quit()
                return

            elif event.type == KEYDOWN:
                if event.key == K_0:
                    mode = 0
                elif event.key == K_1:
                    mode = 1
                elif event.key == K_2:
                    mode = 2
                elif event.key == K_3:
                    mode = 3
                elif event.key == K_4:
                    mode = 4

                elif event.key == K_PAGEUP:
                    current_page = max(0, current_page - 1)
                elif event.key == K_PAGEDOWN:
                    current_page = min(len(story) - 1, current_page + 1)

                if mode == 0:
                    if event.key in [K_PLUS, K_EQUALS]:
                        cat = custom_categories[len(page["custom_parts"]) % len(custom_categories)]
                        fname = custom_files[custom_file_idx]
                        page["custom_parts"].append({"category": cat, "index": fname, "x": 0, "y": 0})
                        selected_custom = len(page["custom_parts"]) - 1
                    elif event.key == K_MINUS:
                        if page["custom_parts"]:
                            page["custom_parts"].pop(selected_custom)
                            selected_custom = max(0, selected_custom - 1)
                    elif event.key == K_TAB:
                        if page["custom_parts"]:
                            selected_custom = (selected_custom + 1) % len(page["custom_parts"])
                    elif page.get("custom_parts"):
                        part = page["custom_parts"][selected_custom]
                        if event.key == K_LEFT:
                            custom_file_idx = (custom_file_idx - 1) % len(custom_files)
                            part["index"] = custom_files[custom_file_idx]
                        elif event.key == K_RIGHT:
                            custom_file_idx = (custom_file_idx + 1) % len(custom_files)
                            part["index"] = custom_files[custom_file_idx]
                        elif event.key == K_w:
                            part["y"] -= 5
                        elif event.key == K_s:
                            part["y"] += 5
                        elif event.key == K_a:
                            part["x"] -= 5
                        elif event.key == K_d:
                            part["x"] += 5

                elif mode == 4:
                    if event.key == K_LEFT:
                        pose_idx = (pose_idx - 1) % len(poses)
                    elif event.key == K_RIGHT:
                        pose_idx = (pose_idx + 1) % len(poses)
                    elif event.key == K_UP:
                        eye_idx = (eye_idx - 1) % len(eyes)
                    elif event.key == K_DOWN:
                        eye_idx = (eye_idx + 1) % len(eyes)
                    elif event.key == K_q:
                        brow_idx = (brow_idx - 1) % len(brows)
                    elif event.key == K_e:
                        brow_idx = (brow_idx + 1) % len(brows)
                    elif event.key == K_z:
                        mouth_idx = (mouth_idx - 1) % len(mouths)
                    elif event.key == K_c:
                        mouth_idx = (mouth_idx + 1) % len(mouths)
                    elif event.key == K_a:
                        nose_idx = (nose_idx - 1) % len(noses)
                    elif event.key == K_d:
                        nose_idx = (nose_idx + 1) % len(noses)

                else:
                    if event.key == K_LEFT:
                        pose_idx = (pose_idx - 1) % len(poses)
                    elif event.key == K_RIGHT:
                        pose_idx = (pose_idx + 1) % len(poses)
                    elif event.key == K_UP:
                        face_idx = (face_idx - 1) % len(faces)
                    elif event.key == K_DOWN:
                        face_idx = (face_idx + 1) % len(faces)
                    elif event.key == K_q and mode == 2:
                        right_pose_idx = (right_pose_idx - 1) % len(right_poses)
                    elif event.key == K_e and mode == 2:
                        right_pose_idx = (right_pose_idx + 1) % len(right_poses)

                if event.key == K_RETURN:
                    page["character"] = CHARACTER
                    page.pop("image", None)
                    page.pop("image_size", None)
                    if mode == 0:
                        page["custom_mode"] = True
                    elif mode == 1:
                        page["pose"] = pose
                        page["face"] = face
                        page.pop("pose_left", None)
                        page.pop("pose_right", None)
                    elif mode == 2:
                        page["pose_left"] = pose
                        page["pose_right"] = right_pose
                        page["face"] = face
                        page.pop("pose", None)
                    elif mode == 4:
                        page["pose"] = pose
                        if len(parts) == 4:
                            page["face_parts"] = parts
                    print("[✓] Saved pose to story.json")

                elif event.key == K_SPACE:
                    name = input("Expression name: ").strip().lower()
                    if name:
                        if CHARACTER not in pose_map:
                            pose_map[CHARACTER] = {}
                        if mode == 1:
                            pose_map[CHARACTER][name] = [pose, face]
                        elif mode == 2:
                            pose_map[CHARACTER][name] = [pose, right_pose, face]
                        elif mode == 4:
                            pose_map[CHARACTER][name] = [pose] + parts
                        print(f"[✓] Saved expression preset '{name}'")

        clock.tick(30)


if __name__ == "__main__":
    main()

