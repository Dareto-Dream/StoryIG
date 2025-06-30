import pygame
import json
import os
from pygame.locals import *

# === Config ===
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
CHARACTER = "cassian"  # Change to active character name
ASSET_PATH = f"assets/characters/{CHARACTER}"
POSES_PATH = f"{ASSET_PATH}/Poses"
EXPRESSIONS_PATH = f"{ASSET_PATH}/Expressions"
STORY_PATH = "story.json"
POSE_MAP_PATH = "pose_face_map.json"

# === Load JSON ===
def load_story():
    with open(STORY_PATH, 'r') as f:
        return json.load(f)

def save_story(data):
    with open(STORY_PATH, 'w') as f:
        json.dump(data, f, indent=4)

def load_pose_map():
    return json.load(open(POSE_MAP_PATH)) if os.path.exists(POSE_MAP_PATH) else {}

def save_pose_map(data):
    with open(POSE_MAP_PATH, 'w') as f:
        json.dump(data, f, indent=4)

# === Load available parts ===
def get_files():
    if CHARACTER == "cassian":
        poses = sorted(f.split('.')[0] for f in os.listdir(POSES_PATH) if f.endswith('.png'))
        eyes = sorted(f.split('.')[0] for f in os.listdir(f"{EXPRESSIONS_PATH}/eyes"))
        brows = sorted(f.split('.')[0] for f in os.listdir(f"{EXPRESSIONS_PATH}/eyebrows"))
        mouths = sorted(f.split('.')[0] for f in os.listdir(f"{EXPRESSIONS_PATH}/mouth"))
        noses = sorted(f.split('.')[0] for f in os.listdir(f"{EXPRESSIONS_PATH}/nose"))
        return poses, eyes, brows, mouths, noses
    else:
        files = os.listdir(ASSET_PATH)
        poses = sorted(set(f.split('.')[0] for f in files if f[0].isdigit() and '-' not in f and not f.endswith("r.png")))
        right_poses = sorted(set(f.split('.')[0] for f in files if f.endswith('r.png')))
        faces = sorted(set(f.split('.')[0] for f in files if f[0].isalpha() and len(f.split('.')[0]) == 1))
        return poses, right_poses, faces

# === Assemble Cassian's face ===
def get_cassian_face(eye, brow, mouth, nose):
    base = pygame.image.load(f"{EXPRESSIONS_PATH}/base.png").convert_alpha()
    for part, folder in zip([eye, brow, mouth, nose], ['eyes', 'eyebrows', 'mouth', 'nose']):
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
            pose_img = pygame.image.load(f"{ASSET_PATH}/{pose}.png").convert_alpha()
            face_img = pygame.image.load(f"{ASSET_PATH}/{face}.png").convert_alpha()
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
    mode = 4  # 1 = single, 2 = split, 3 = L/R+face, 4 = cassian

    if mode == 4:
        poses, eyes, brows, mouths, noses = get_files()
        eye_idx, brow_idx, mouth_idx, nose_idx = 0, 0, 0, 0
    else:
        poses, right_poses, faces = get_files()
        pose_idx, right_pose_idx, face_idx = 0, 0, 0

    pose_idx = 0
    clock = pygame.time.Clock()

    while True:
        screen.fill((30, 30, 30))
        page = story[current_page]
        text = page.get("text", "")

        pose = poses[pose_idx]

        if mode == 4:
            parts = [
                eyes[eye_idx],
                brows[brow_idx],
                mouths[mouth_idx],
                noses[nose_idx]
            ]
            preview = get_combined_image(mode, pose, parts=parts)
        elif mode == 1:
            face = faces[face_idx]
            preview = get_combined_image(mode, pose, face)
        else:
            face = faces[face_idx]
            right_pose = right_poses[right_pose_idx]
            preview = get_combined_image(mode, pose, face, right_pose)

        if preview:
            screen.blit(preview, (50, 50))

        # === Display Info ===
        screen.blit(font.render(f"Page {page['page']}: {text}", True, (255, 255, 255)), (400, 80))
        screen.blit(font.render(f"Mode: {mode}", True, (255, 255, 0)), (400, 110))
        screen.blit(font.render(f"Pose: {pose}", True, (255, 255, 255)), (400, 140))

        if mode == 4:
            screen.blit(font.render(f"Eyes: {parts[0]}", True, (255, 255, 255)), (400, 170))
            screen.blit(font.render(f"Brows: {parts[1]}", True, (255, 255, 255)), (400, 200))
            screen.blit(font.render(f"Mouth: {parts[2]}", True, (255, 255, 255)), (400, 230))
            screen.blit(font.render(f"Nose: {parts[3]}", True, (255, 255, 255)), (400, 260))
        elif mode == 2:
            screen.blit(font.render(f"Right Pose: {right_pose}", True, (255, 255, 255)), (400, 170))
            screen.blit(font.render(f"Face: {face}", True, (255, 255, 255)), (400, 200))
        else:
            screen.blit(font.render(f"Face: {face}", True, (255, 255, 255)), (400, 170))

        screen.blit(font.render("←→ Pose | ↑↓ Eyes | Q/E Brows | Z/C Mouth | A/D Nose", True, (200, 200, 200)), (10, 520))
        screen.blit(font.render("1–4: Change mode | Enter: Save to story | Space: Save expression", True, (200, 200, 200)), (10, 550))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == QUIT:
                save_story(story)
                save_pose_map(pose_map)
                pygame.quit()
                return

            elif event.type == KEYDOWN:
                if event.key == K_LEFT:
                    pose_idx = (pose_idx - 1) % len(poses)
                elif event.key == K_RIGHT:
                    pose_idx = (pose_idx + 1) % len(poses)

                elif event.key == K_UP and mode == 4:
                    eye_idx = (eye_idx - 1) % len(eyes)
                elif event.key == K_DOWN and mode == 4:
                    eye_idx = (eye_idx + 1) % len(eyes)
                elif event.key == K_q and mode == 4:
                    brow_idx = (brow_idx - 1) % len(brows)
                elif event.key == K_e and mode == 4:
                    brow_idx = (brow_idx + 1) % len(brows)
                elif event.key == K_z and mode == 4:
                    mouth_idx = (mouth_idx - 1) % len(mouths)
                elif event.key == K_c and mode == 4:
                    mouth_idx = (mouth_idx + 1) % len(mouths)
                elif event.key == K_a and mode == 4:
                    nose_idx = (nose_idx - 1) % len(noses)
                elif event.key == K_d and mode == 4:
                    nose_idx = (nose_idx + 1) % len(noses)

                elif event.key == K_1:
                    mode = 1
                elif event.key == K_2:
                    mode = 2
                elif event.key == K_3:
                    mode = 3
                elif event.key == K_4:
                    mode = 4

                elif event.key == K_RETURN:
                    page["character"] = CHARACTER
                    if mode == 1:
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
                        page["face_parts"] = parts
                    if "image" in page:
                        del page["image"]
                    if "image_size" in page:
                        del page["image_size"]
                    print(f"[✓] Saved to story.json: {page}")

                elif event.key == K_SPACE:
                    name = input("Enter expression name: ").strip().lower()
                    if name:
                        if CHARACTER not in pose_map:
                            pose_map[CHARACTER] = {}
                        if mode == 1:
                            pose_map[CHARACTER][name] = [pose, face]
                        elif mode == 2:
                            pose_map[CHARACTER][name] = [pose, right_pose, face]
                        elif mode == 4:
                            pose_map[CHARACTER][name] = [pose] + parts
                        print(f"[✓] Saved to pose_face_map.json: {name}")

                elif event.key == K_PAGEUP:
                    current_page = max(0, current_page - 1)
                elif event.key == K_PAGEDOWN:
                    current_page = min(len(story) - 1, current_page + 1)

        clock.tick(30)

if __name__ == "__main__":
    main()