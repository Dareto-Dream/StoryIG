# ------------------- MAIN GAME LOOP DEMO ------------------------
import pygame

from conductor import Conductor
from discord import presence
from tools.character_animations import CharacterAnimator
from tools.xml_sprite_loader import *

if __name__ == "__main__":
    import sys

    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Conductor (Character) Test")
    clock = pygame.time.Clock()

    frames = load_sprites_from_xml(
        "assets/minigame/notes/NOTE_assets.png",
        "assets/minigame/notes/NOTE_assets.xml",
        scale=0.7 # arrow scale
    )

    # For a mod character:
    dustman_raw = load_character_sprites_from_xml("assets/minigame/characters/dearest_fnfbaby.png",
                                                  "assets/minigame/characters/dearest_fnfbaby.xml", scale=0.6)
    dustman_frames = load_character_frames("unused", dustman_raw)
    megaman_raw = load_character_sprites_from_xml("assets/minigame/characters/nmi_real.png",
                                                  "assets/minigame/characters/nmi_real.xml", scale=0.6)
    tiffany_frames = load_character_frames("tiffany", megaman_raw)
    player_animator = CharacterAnimator(dustman_frames, position=(950, 620))
    tiffany_animator = CharacterAnimator(tiffany_frames, position=(330, 620))

    # Load 6 background layers
    layer_filenames = [
        "snowone.png", "snowtwo.png", "snowthree.png",
        "snowfour.png", "snowfive.png", "snowsix.png"
    ]

    # Load and scale each layer to (1280, 720)
    background_layers = [
        pygame.transform.smoothscale(
            pygame.image.load(f"assets/minigame/backgrounds/mutation/{filename}").convert_alpha(),
            (1280, 720)
        )
        for filename in reversed(layer_filenames)
    ]
    # highground_img = pygame.image.load("assets/minigame/backgrounds/lefrontree.png").convert_alpha() # ITS OVER LUKE I HAVE THE HIGHGROUND
    # highground_img = pygame.transform.smoothscale(highground_img, (1280, 720))

    player_key_map = {
        pygame.K_a: 'left',
        pygame.K_s: 'down',
        pygame.K_w: 'up',
        pygame.K_d: 'right',
        # Arrow key controls
        pygame.K_LEFT: 'left',
        pygame.K_DOWN: 'down',
        pygame.K_UP: 'up',
        pygame.K_RIGHT: 'right'
    }

    side_configs = [
        {
            'name': "player",
            'animator': player_animator,
            'arrow_x': 900,
            'is_player': True,
            'key_map': player_key_map,
        },
        {
            'name': "tiffany",
            'animator': tiffany_animator,
            'arrow_x': 350,
        }
    ]

    conductor = Conductor("mutation", frames, screen, side_configs)
    presence.set_presence(state="Playing Alpha", large_image="fakebaby", details="UZI from Murder Drones", small_image="vn",
                          small_text="Im dead")

    running = True
    while running:
        dt = clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            conductor.handle_input(event)
        conductor.update(dt)
        if hasattr(conductor, "judgement_splash"):
            conductor.judgement_splash.update(dt)
        for layer in background_layers:
            screen.blit(layer, (0, 0))
        conductor.draw()
        if hasattr(conductor, "judgement_splash"):
            conductor.judgement_splash.draw(screen)
        # screen.blit(highground_img, (0, 0))
        pygame.display.flip()

    pygame.quit()
    sys.exit()