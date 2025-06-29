import pygame
import json
import os
from pygame.locals import *

# === Config ===
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
CHARACTER = "mc"  # <-- Change this to match your folder/character
ASSET_PATH = f"assets/characters/{CHARACTER}"
STORY_PATH = "story.json"
POSE_MAP_PATH = "pose_face_map.json"

# === Load Assets ===
def get_image(file):
    return pygame.image.load(os.path.join(ASSET_PATH, file)).convert_alpha()

def load_story():
    with open(STORY_PATH, 'r') as f:
        return json.load(f)

def save_story(story):
    with open(STORY_PATH, 'w') as f:
        json.dump(story, f, indent=4)

def load_pose_map():
    if os.path.exists(POSE_MAP_PATH):
        with open(POSE_MAP_PATH, 'r') as f:
            return json.load(f)
    return {}

def save_pose_map(data):
    with open(POSE_MAP_PATH, 'w') as f:
        json.dump(data, f, indent=4)

# === Get Available Poses/Faces ===
def get_sorted_assets():
    poses, faces = [], []
    for f in os.listdir(ASSET_PATH):
        name = f.lower()
        if name.endswith(".png"):
            if name[0].isdigit():
                poses.append(f.split('.')[0])
            elif name[0].isalpha() and len(name.split('.')[0]) == 1:
                faces.append(f.split('.')[0])
    return sorted(list(set(poses))), sorted(list(set(faces)))

# === Combine Pose + Face ===
def get_combined_image(pose, face):
    pose_img = get_image(f"{pose}.png")
    face_img = get_image(f"{face}.png")
    result = pygame.Surface(pose_img.get_size(), pygame.SRCALPHA)
    result.blit(pose_img, (0, 0))
    result.blit(face_img, (0, 0))
    return result

# === Draw ===
def draw(screen, img, text, pose, face):
    screen.fill((30, 30, 30))
    if img:
        screen.blit(img, (50, 50))
    font = pygame.font.Font(None, 28)
    text_surf = font.render(f"Text: {text}", True, (255, 255, 255))
    pose_surf = font.render(f"Pose: {pose} | Face: {face}", True, (255, 255, 0))
    instr_surf = font.render("Left/Right pose, Up/Down face, Enter = write to page, Space = name emotion", True, (200, 200, 200))
    screen.blit(text_surf, (400, 100))
    screen.blit(pose_surf, (400, 150))
    screen.blit(instr_surf, (50, 550))
    pygame.display.flip()

# === Main ===
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Pose Maker")

    poses, faces = get_sorted_assets()
    pose_idx = 0
    face_idx = 0
    story = load_story()
    pose_map = load_pose_map()
    current_page = 0

    clock = pygame.time.Clock()

    while True:
        page = story[current_page]
        pose = poses[pose_idx]
        face = faces[face_idx]
        img = get_combined_image(pose, face)
        draw(screen, img, page.get("text", ""), pose, face)

        for event in pygame.event.get():
            if event.type == QUIT:
                save_story(story)
                save_pose_map(pose_map)
                pygame.quit()
                return
            elif event.type == KEYDOWN:
                if event.key == K_RIGHT:
                    pose_idx = (pose_idx + 1) % len(poses)
                elif event.key == K_LEFT:
                    pose_idx = (pose_idx - 1) % len(poses)
                elif event.key == K_DOWN:
                    face_idx = (face_idx + 1) % len(faces)
                elif event.key == K_UP:
                    face_idx = (face_idx - 1) % len(faces)
                elif event.key == K_RETURN:
                    # Save pose/face to current page
                    page = story[current_page]
                    page["pose"] = pose
                    page["face"] = face
                    page["character"] = CHARACTER  # Force-set character for rendering

                    # Clean up old single-image field
                    if "image" in page:
                        del page["image"]
                    if "image_size" in page:
                        del page["image_size"]

                    print(f"[✓] Updated page {page['page']} with pose {pose}, face {face}, and character '{CHARACTER}'")
                elif event.key == K_SPACE:
                    # Prompt for emotion name
                    name = input("Enter emotion name to save: ").strip()
                    if name:
                        if CHARACTER not in pose_map:
                            pose_map[CHARACTER] = {}
                        pose_map[CHARACTER][name] = [pose, face]
                        print(f"Saved expression '{name}' to pose_face_map.json")
                elif event.key == K_PAGEUP:
                    current_page = max(0, current_page - 1)
                elif event.key == K_PAGEDOWN:
                    current_page = min(len(story) - 1, current_page + 1)

        clock.tick(30)

if __name__ == "__main__":
    main()
