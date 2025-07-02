def run_minigame(screen):
    import pygame
    # Init game screen (or use subsurface of main VN screen if shared)
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    running = True
    start_time = pygame.time.get_ticks()

    while running:
        dt = clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return  # Don't quit app
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # Game logic...
        # Drawing logic...
        pygame.display.flip()

        # End condition
        if pygame.time.get_ticks() - start_time > 15000:  # End after 15 seconds
            running = False
