import pygame
import re

class TextManager:
    def __init__(self, font_path="assets/fonts/VarelaRound-Regular.ttf", font_size=24, max_width=760):
        self.font = pygame.font.Font(font_path, font_size)
        self.max_width = max_width
        self.reset()

    def reset(self):
        self.full_text = ""
        self.typed_text = ""
        self.typing = False
        self.start_time = 0
        self.speed = 40  # ms per char (default)

    def start(self, text, speed=None):
        self.full_text = text
        self.typed_text = ""
        self.typing = True
        self.start_time = pygame.time.get_ticks()
        if speed is not None:
            self.speed = speed

    def update(self):
        if not self.typing:
            return
        elapsed = pygame.time.get_ticks() - self.start_time
        chars_to_show = elapsed // self.speed if self.speed > 0 else len(self.full_text)
        self.typed_text = self.full_text[:chars_to_show]
        if chars_to_show >= len(self.full_text):
            self.typing = False

    def skip(self):
        self.typed_text = self.full_text
        self.typing = False

    def draw(self, screen, pos, color=(0, 0, 0)):
        x, y = pos
        default_color = color
        font_path = "assets/fonts/VarelaRound-Regular.ttf"
        lines = self.typed_text.split('\n')
        for line in lines:
            wrapped_lines = []
            current_line = ""
            for word in line.split(' '):
                test_line = (current_line + " " + word).strip() if current_line else word
                if self.font.size(test_line)[0] <= self.max_width:
                    current_line = test_line
                else:
                    wrapped_lines.append(current_line)
                    current_line = word
            if current_line:
                wrapped_lines.append(current_line)
            for wrapped in wrapped_lines:
                # Use regex to find all markdown segments in the line
                pos_x = x
                pattern = r'(\*\*\*.+?\*\*\*|\*\*.+?\*\*|\*.+?\*|__.+?__|\[color=.+?\].+?\[/color\])'
                parts = re.split(pattern, wrapped)
                for part in parts:
                    if not part:
                        continue
                    font_to_use = pygame.font.Font(font_path, self.font.get_height())
                    chunk_color = default_color
                    render_text = part

                    # [color=red]text[/color]
                    color_match = re.match(r'\[color=(.+?)\](.+?)\[/color\]', part)
                    if color_match:
                        chunk_color = pygame.Color(color_match.group(1))
                        render_text = color_match.group(2)
                    # ***bolditalic***
                    elif re.match(r'^\*\*\*(.+)\*\*\*$', part):
                        render_text = re.sub(r'^\*\*\*(.+)\*\*\*$', r'\1', part)
                        font_to_use.set_bold(True)
                        font_to_use.set_italic(True)
                    # **bold**
                    elif re.match(r'^\*\*(.+)\*\*$', part):
                        render_text = re.sub(r'^\*\*(.+)\*\*$', r'\1', part)
                        font_to_use.set_bold(True)
                    # *italic*
                    elif re.match(r'^\*(.+)\*$', part):
                        render_text = re.sub(r'^\*(.+)\*$', r'\1', part)
                        font_to_use.set_italic(True)
                    # __underline__
                    elif re.match(r'^__(.+)__$', part):
                        render_text = re.sub(r'^__(.+)__$', r'\1', part)
                        font_to_use.set_underline(True)

                    rendered = font_to_use.render(render_text, True, chunk_color)
                    screen.blit(rendered, (pos_x, y))
                    pos_x += rendered.get_width()
                y += self.font.get_linesize()