# ... (unchanged imports and config)
import pygame
import json
import os
from pygame.locals import *
from character_renderer import render_character  # assumes this exists

# === Config ===
SCREEN_WIDTH, SCREEN_HEIGHT = 1500, 1000
CHARACTERS = ["mc", "tiffany", "hanami", "harumi", "cassian"]
char_idx = 0
CHARACTER = CHARACTERS[char_idx]
ASSET_PATH = f"assets/characters/{CHARACTER}"
POSES_PATH = f"{ASSET_PATH}/Poses"
EXPRESSIONS_PATH = f"{ASSET_PATH}/Expressions"
STORY_PATH = "story.json"
POSE_MAP_PATH = "pose_face_map.json"
mode = 1  # Default mode

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
    try:
        if CHARACTER == "cassian":
            poses = sorted(f.split(".")[0] for f in os.listdir(POSES_PATH) if f.endswith(".png"))
            eyes = sorted(f.split(".")[0] for f in os.listdir(f"{EXPRESSIONS_PATH}/eyes"))
            brows = sorted(f.split(".")[0] for f in os.listdir(f"{EXPRESSIONS_PATH}/eyebrows"))
            mouths = sorted(f.split(".")[0] for f in os.listdir(f"{EXPRESSIONS_PATH}/mouth"))
            noses = sorted(f.split(".")[0] for f in os.listdir(f"{EXPRESSIONS_PATH}/nose"))
            return poses, eyes, brows, mouths, noses

        elif CHARACTER == "tiffany":
            files = sorted(f.split(".")[0] for f in os.listdir(ASSET_PATH) if f.endswith(".png"))
            print(f"[DEBUG] Loaded Tiffany's files: {files}")
            return files, [], ["_"]

        else:
            files = os.listdir(ASSET_PATH)
            poses = sorted(set(f.split(".")[0] for f in files if f[0].isdigit() and "-" not in f and not f.endswith("r.png")))
            right_poses = sorted(set(f.split(".")[0] for f in files if f.endswith("r.png")))
            faces = sorted(set(f.split(".")[0] for f in files if f[0].isalpha() and len(f.split(".")[0]) == 1))
            return poses, right_poses, faces
    except Exception as e:
        print(f"[!] Error loading files for {CHARACTER}: {e}")
        return [], [], [], [], []

def reload_assets():
    global CHARACTER, ASSET_PATH, POSES_PATH, EXPRESSIONS_PATH
    global poses, right_poses, faces, eyes, brows, mouths, noses
    global pose_idx, right_pose_idx, face_idx, eye_idx, brow_idx, mouth_idx, nose_idx
    global custom_files, custom_file_idx

    CHARACTER = CHARACTERS[char_idx]
    ASSET_PATH = f"assets/characters/{CHARACTER}"
    POSES_PATH = f"{ASSET_PATH}/Poses"
    EXPRESSIONS_PATH = f"{ASSET_PATH}/Expressions"

    if CHARACTER == "cassian":
        poses, eyes, brows, mouths, noses = get_files()
        pose_idx = eye_idx = brow_idx = mouth_idx = nose_idx = 0
        if not poses or not eyes:
            print(f"[!] Warning: missing parts for {CHARACTER}")
    else:
        poses, right_poses, faces = get_files()
        if not poses:
            poses = ["_"]
        if not faces:
            faces = ["_"]
        pose_idx = right_pose_idx = face_idx = 0

    # Refresh custom files list for current character
    custom_files = sorted([f for f in os.listdir(ASSET_PATH) if f.endswith(".png")])
    custom_file_idx = 0

# === Main Tool ===
def main():
    global char_idx, mode
    global pose_idx, right_pose_idx, face_idx, eye_idx, brow_idx, mouth_idx, nose_idx
    global poses, right_poses, faces, eyes, brows, mouths, noses
    global custom_files, custom_file_idx

    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Pose Maker")
    font = pygame.font.Font(None, 28)

    reload_assets()
    mode = 4 if CHARACTER == "cassian" else 1

    story = load_story()
    pose_map = load_pose_map()
    current_page = 0
    selected_custom = 0
    custom_categories = ["bodyL", "bodyR", "head", "eyes", "eyebrows", "mouth", "accessory"]

    clock = pygame.time.Clock()

    while True:
        screen.fill((30, 30, 30))
        page = story[current_page]
        text = page.get("text", "")

        temp_page = {"character": CHARACTER}
        try:
            if mode == 0:
                page.setdefault("custom_parts", [])
                temp_page["custom_parts"] = page["custom_parts"]
            elif mode == 1 and poses and faces:
                temp_page["pose"] = poses[pose_idx]
                temp_page["face"] = faces[face_idx]
            elif mode == 2 and poses and right_poses and faces:
                temp_page["pose_left"] = poses[pose_idx]
                temp_page["pose_right"] = right_poses[right_pose_idx]
                temp_page["face"] = faces[face_idx]
            elif mode == 4 and poses and eyes and brows and mouths and noses:
                temp_page["pose"] = poses[pose_idx]
                temp_page["face_parts"] = [eyes[eye_idx], brows[brow_idx], mouths[mouth_idx], noses[nose_idx]]
        except IndexError:
            print("[!] Index error building temp_page.")
            temp_page = {}

        preview = render_character(temp_page)
        if preview:
            screen.blit(preview, (50, 50))
        else:
            print("[!] Failed to render character preview.")

        screen.blit(font.render(f"Character: {CHARACTER}", True, (255, 255, 0)), (10, 20))
        screen.blit(font.render(f"Page {page['page']}: {text}", True, (255, 255, 255)), (400, 80))
        screen.blit(font.render("0–4 = Mode | Enter = Save | Space = Save Preset | PgUp/Dn = Change Page", True, (200, 200, 200)), (10, 920))
        screen.blit(font.render("←/→ = Change | WASD = Move (custom) | +/- = Add/Remove (custom)", True, (200, 200, 200)), (10, 950))

        if mode == 0 and page["custom_parts"]:
            part = page["custom_parts"][selected_custom]
            screen.blit(font.render(f"Selected: {part['category']} [{part['index']}] @ ({part['x']}, {part['y']})", True, (255, 255, 255)), (400, 140))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == QUIT:
                save_story(story)
                save_pose_map(pose_map)
                pygame.quit()
                return

            elif event.type == KEYDOWN:
                if event.key in [K_0, K_1, K_2, K_3, K_4]:
                    mode = int(event.unicode)

                elif event.key in [K_LEFTBRACKET, K_RIGHTBRACKET]:
                    char_idx = (char_idx + (1 if event.key == K_RIGHTBRACKET else -1)) % len(CHARACTERS)
                    reload_assets()
                    mode = 4 if CHARACTER == "cassian" else 1
                    print(f"[DEBUG] Switched to: {CHARACTER}")
                    print(f"[DEBUG] poses: {poses}")

                    # Sync custom_file_idx after switching characters
                    if page.get("custom_parts"):
                        selected_index = page["custom_parts"][selected_custom]["index"]
                        if selected_index in custom_files:
                            custom_file_idx = custom_files.index(selected_index)
                        else:
                            custom_file_idx = 0

                elif event.key == K_PAGEUP:
                    current_page = max(0, current_page - 1)
                elif event.key == K_PAGEDOWN:
                    current_page = min(len(story) - 1, current_page + 1)

                # === Mode-specific input ===
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
                            selected_index = page["custom_parts"][selected_custom]["index"]
                            if selected_index in custom_files:
                                custom_file_idx = custom_files.index(selected_index)
                            else:
                                custom_file_idx = 0
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

                # === SAVE TO PAGE ===
                if event.key == K_RETURN:
                    page["character"] = CHARACTER
                    for key in ["image", "image_size", "custom_mode", "pose", "pose_left", "pose_right", "face", "face_parts"]:
                        page.pop(key, None)

                    if mode == 0:
                        page["custom_parts"] = temp_page["custom_parts"]
                        page["custom_mode"] = True
                    elif mode == 1:
                        page["pose"] = temp_page["pose"]
                        page["face"] = temp_page["face"]
                    elif mode == 2:
                        page["pose_left"] = temp_page["pose_left"]
                        page["pose_right"] = temp_page["pose_right"]
                        page["face"] = temp_page["face"]
                    elif mode == 4:
                        page["pose"] = temp_page["pose"]
                        page["face_parts"] = temp_page["face_parts"]
                    print("[✓] Saved pose to story.json")

                elif event.key == K_SPACE:
                    name = input("Expression name: ").strip().lower()
                    if name:
                        if CHARACTER not in pose_map:
                            pose_map[CHARACTER] = {}
                        if mode == 1:
                            pose_map[CHARACTER][name] = [temp_page["pose"], temp_page["face"]]
                        elif mode == 2:
                            pose_map[CHARACTER][name] = [temp_page["pose_left"], temp_page["pose_right"], temp_page["face"]]
                        elif mode == 4:
                            pose_map[CHARACTER][name] = [temp_page["pose"]] + temp_page["face_parts"]
                        print(f"[✓] Saved expression preset '{name}'")

        clock.tick(30)

if __name__ == "__main__":
    main()
