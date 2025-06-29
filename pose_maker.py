import pygame
import json
import os
from pygame.locals import *

# === Config ===
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
CHARACTER = "tiffany"  # Change to active character name
ASSET_PATH = f"assets/characters/{CHARACTER}"
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

# === Load pose/face files ===
def get_files():
    files = os.listdir(ASSET_PATH)
    poses = sorted(set(f.split('.')[0] for f in files if f[0].isdigit() and '-' not in f and not f.endswith("r.png")))
    right_poses = sorted(set(f.split('.')[0] for f in files if f.endswith('r.png')))
    faces = sorted(set(f.split('.')[0] for f in files if f[0].isalpha() and len(f.split('.')[0]) == 1))
    return poses, right_poses, faces

# === Render composite image ===
def get_combined_image(pose, face, mode, right_pose=None):
    try:
        pose_img = None
        if mode == 1:
            pose_img = pygame.image.load(f"{ASSET_PATH}/{pose}.png").convert_alpha()
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
    mode = 1  # 1 = full-body, 2 = split-body

    poses, right_poses, faces = get_files()
    pose_idx, right_pose_idx, face_idx = 0, 0, 0

    clock = pygame.time.Clock()

    while True:
        screen.fill((30, 30, 30))
        page = story[current_page]
        text = page.get("text", "")

        pose = poses[pose_idx]
        right_pose = right_poses[right_pose_idx] if right_poses else None
        face = faces[face_idx]

        preview = get_combined_image(pose, face, mode, right_pose)
        if preview:
            screen.blit(preview, (50, 50))

        # UI Info
        screen.blit(font.render(f"Page {page['page']}: {text}", True, (255, 255, 255)), (400, 100))
        screen.blit(font.render(f"Mode: {'Split' if mode == 2 else 'Full'} Body [1/2]", True, (255, 255, 0)), (400, 140))
        screen.blit(font.render(f"Pose: {pose}", True, (255, 255, 255)), (400, 180))
        if mode == 2:
            screen.blit(font.render(f"Right Pose: {right_pose}", True, (255, 255, 255)), (400, 210))
        screen.blit(font.render(f"Face: {face}", True, (255, 255, 255)), (400, 240))
        screen.blit(font.render("Arrows = Pose/Face | Q/E = Right Pose | Space = name expression | Enter = write to story | PgUp/PgDn = flip pages", True, (200, 200, 200)), (10, 550))

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
                elif event.key == K_UP:
                    face_idx = (face_idx - 1) % len(faces)
                elif event.key == K_DOWN:
                    face_idx = (face_idx + 1) % len(faces)
                elif event.key == K_q and mode == 2:
                    right_pose_idx = (right_pose_idx - 1) % len(right_poses)
                elif event.key == K_e and mode == 2:
                    right_pose_idx = (right_pose_idx + 1) % len(right_poses)
                elif event.key == K_1:
                    mode = 1
                elif event.key == K_2:
                    mode = 2

                elif event.key == K_RETURN:
                    page["character"] = CHARACTER
                    page["face"] = face
                    if mode == 1:
                        page["pose"] = pose
                        page.pop("pose_left", None)
                        page.pop("pose_right", None)
                    else:
                        page["pose_left"] = pose
                        page["pose_right"] = right_pose
                        page.pop("pose", None)
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
                        else:
                            pose_map[CHARACTER][name] = [pose, right_pose, face]
                        print(f"[✓] Saved to pose_face_map.json: {name}")

                elif event.key == K_PAGEUP:
                    current_page = max(0, current_page - 1)
                elif event.key == K_PAGEDOWN:
                    current_page = min(len(story) - 1, current_page + 1)

        clock.tick(30)

if __name__ == "__main__":
    main()