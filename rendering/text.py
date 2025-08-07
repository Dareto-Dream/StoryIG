import pygame
import re

class TextManager:
    def __init__(self, font_path="assets/fonts/VarelaRound-Regular.ttf", font_size=24, max_width=760):
        self.font = pygame.font.Font(font_path, font_size)
        self.font_path = font_path
        self.font_size = font_size
        self.max_width = max_width
        self.font_cache = {}  # Cache for styled fonts
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

    def _get_styled_font(self, bold=False, italic=False, underline=False):
        key = (bold, italic, underline)
        if key not in self.font_cache:
            font = pygame.font.Font(self.font_path, self.font.get_height())
            font.set_bold(bold)
            font.set_italic(italic)
            font.set_underline(underline)
            self.font_cache[key] = font
        return self.font_cache[key]

    def _render_chunk(self, text, default_color):
        chunk_color = default_color
        bold = italic = underline = False

        # [color=red]text[/color]
        color_match = re.match(r'\[color=(.+?)\](.+?)\[/color\]', text)
        if color_match:
            try:
                chunk_color = pygame.Color(color_match.group(1))
            except ValueError:
                chunk_color = default_color
            text = color_match.group(2)
        # ***bolditalic***
        elif re.match(r'^\*\*\*(.+)\*\*\*$', text):
            text = re.sub(r'^\*\*\*(.+)\*\*\*$', r'\1', text)
            bold = True
            italic = True
        # **bold**
        elif re.match(r'^\*\*(.+)\*\*$', text):
            text = re.sub(r'^\*\*(.+)\*\*$', r'\1', text)
            bold = True
        # *italic*
        elif re.match(r'^\*(.+)\*$', text):
            text = re.sub(r'^\*(.+)\*$', r'\1', text)
            italic = True
        # __underline__
        elif re.match(r'^__(.+)__$', text):
            text = re.sub(r'^__(.+)__$', r'\1', text)
            underline = True

        font_to_use = self._get_styled_font(bold, italic, underline)
        return font_to_use.render(text, True, chunk_color), text

    def draw(self, screen, pos, color=(0, 0, 0)):
        x, y = pos
        default_color = color
        max_width = self.max_width
        lines = self.typed_text.split('\n')
        for raw_line in lines:
            # Split the line into markdown segments
            pattern = r'(\*\*\*.+?\*\*\*|\*\*.+?\*\*|\*.+?\*|__.+?__|\[color=.+?\].+?\[/color\])'
            segments = re.split(pattern, raw_line)
            current_line_chunks = []
            current_line_width = 0

            for segment in segments:
                if not segment:
                    continue
                # Allow for lines with only whitespace (important for certain stories)
                segment = segment.replace('\r', '')

                surf, txt = self._render_chunk(segment, default_color)
                surf_width = surf.get_width()

                # If adding this chunk would overflow, wrap first
                if current_line_width + surf_width > max_width and current_line_chunks:
                    # Draw current line
                    pos_x = x
                    for s, _ in current_line_chunks:
                        screen.blit(s, (pos_x, y))
                        pos_x += s.get_width()
                    y += self.font.get_linesize()
                    # Start new line with this chunk
                    current_line_chunks = [(surf, txt)]
                    current_line_width = surf_width
                else:
                    current_line_chunks.append((surf, txt))
                    current_line_width += surf_width

            # Draw the last line for this raw_line
            if current_line_chunks:
                pos_x = x
                for s, _ in current_line_chunks:
                    screen.blit(s, (pos_x, y))
                    pos_x += s.get_width()
                y += self.font.get_linesize()