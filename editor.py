import json
import os

STORY_PATH = "proto.json"
DEFAULT_BG = "assets/backgrounds/residential.png"
DEFAULT_POS = [100, 200]

def load_story():
    if os.path.exists(STORY_PATH):
        with open(STORY_PATH, 'r') as f:
            return json.load(f)
    return []

def save_story(story):
    with open(STORY_PATH, 'w') as f:
        json.dump(story, f, indent=4)

def main():
    story = load_story()
    current_page = story[-1]['page'] + 1 if story else 1

    while True:
        char_name = input("Character (or 'exit'): ").strip().lower()
        if char_name == "exit":
            break

        text = input("Text: ").strip()

        page = {
            "page": current_page,
            "speaker": char_name.capitalize(),
            "image": f"assets/characters/{char_name}.png",
            "background": DEFAULT_BG,
            "position": DEFAULT_POS,
            "text": text,
            "inputs": []
        }

        story.append(page)
        save_story(story)
        print(f"Page {current_page} added.\n")
        current_page += 1

if __name__ == "__main__":
    main()
