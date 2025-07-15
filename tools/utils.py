import cv2
import pygame

class VideoPlayer:
    def __init__(self, path, screen_size=(1280, 720), loop=False):
        self.cap = cv2.VideoCapture(path)
        self.screen_size = screen_size
        self.loop = loop
        self.frame = None
        self.done = False
        self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 30
        self.frame_interval = 1000.0 / self.fps  # ms per frame
        self.last_frame_time = 0

        # Ensure first frame is available
        self.update(0)

        # Force load the first frame on init
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, self.screen_size)
            self.frame = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
        else:
            self.frame = None
            self.done = True

    def update(self, dt):
        if self.done:
            return None
        self.last_frame_time += dt
        # Only decode a new frame if enough time has passed
        if self.last_frame_time < self.frame_interval:
            return self.frame
        self.last_frame_time -= self.frame_interval
        ret, frame = self.cap.read()
        if not ret:
            if self.loop:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = self.cap.read()
                if not ret:
                    self.done = True
                    return None
            else:
                self.done = True
                return None
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, self.screen_size)
        self.frame = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
        return self.frame

    def draw(self, screen):
        if self.frame is not None:
            screen.blit(self.frame, (0, 0))

    def release(self):
        self.cap.release()
