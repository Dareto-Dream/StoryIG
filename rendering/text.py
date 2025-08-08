import pygame
import re

class TextManager:
    def __init__(self, font_path="assets/fonts/VarelaRound-Regular.ttf", font_size=24, max_width=760):
        self.font_path = font_path
        self.font_size = font_size
        self.font = pygame.font.Font(font_path, font_size)
        self.max_width = max_width
        self.font_cache = {}  # (bold, italic, underline) -> font
        self.reset()

    # --------------------
    # Public API
    # --------------------
    def reset(self):
        self.full_text = ""
        self.typed_text = ""
        self.typing = False
        self._idx = 0
        self._speed_ms = 40  # default; overwritten by start()
        self._accum_ms = 0
        self._last_ticks = pygame.time.get_ticks()

    def start(self, text, speed=None):
        """Begin typewriter for given text. speed is ms/char."""
        self.full_text = (text or "").replace("\r", "")
        self.typed_text = ""
        self.typing = True
        self._idx = 0
        self._speed_ms = int(speed) if speed is not None else 40
        self._accum_ms = 0
        self._last_ticks = pygame.time.get_ticks()

    def update(self):
        """Advance typewriter based on elapsed time."""
        if not self.typing:
            return
        now = pygame.time.get_ticks()
        dt = now - self._last_ticks
        self._last_ticks = now
        self._accum_ms += dt

        # emit as many chars as time allows
        while self._accum_ms >= self._speed_ms and self._idx < len(self.full_text):
            self.typed_text += self.full_text[self._idx]
            self._idx += 1
            self._accum_ms -= self._speed_ms

        if self._idx >= len(self.full_text):
            self.typing = False

    def skip(self):
        """Finish typewriter instantly."""
        self.typed_text = self.full_text
        self._idx = len(self.full_text)
        self.typing = False

    def draw(self, screen, pos, color=(0, 0, 0)):
        """
        Draw typed_text at pos with wrapping to self.max_width.
        Supports: **bold**, *italic*, __underline__, ***bold+italic***,
                  [color=red]text[/color] or [color=#e33]text[/color]
        """
        x, y = pos
        default_color = color
        max_width = self.max_width

        # Split into logical lines by \n, then wrap each
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
                segment = segment.replace('\r', '')  # safety on CRLF

                # --- Render this segment with style, get (surface, plain_text, (font, color)) ---
                surf, txt, style = self._render_chunk(segment, default_color)
                surf_width = surf.get_width()
                font, chunk_color = style

                # Case A: The segment itself is wider than a full line, and we're at line start.
                # Split into multiple physical lines with same style.
                if surf_width > max_width and current_line_width == 0:
                    remaining = txt
                    while remaining:
                        take = self._fit_prefix_with_font(font, remaining, max_width)
                        part = remaining[:take]
                        part_surf = font.render(part, True, chunk_color)
                        screen.blit(part_surf, (x, y))
                        y += self.font.get_linesize()
                        # Trim leading spaces to avoid indenting next line
                        remaining = remaining[take:].lstrip(' ')
                    # Done with this big segment
                    continue

                # Case B: Adding this segment would overflow the current line → wrap first
                if current_line_width + surf_width > max_width and current_line_chunks:
                    # Draw current line buffer
                    pos_x = x
                    for s_, _txt in current_line_chunks:
                        screen.blit(s_, (pos_x, y))
                        pos_x += s_.get_width()
                    y += self.font.get_linesize()

                    # Now handle the overflowing segment on a fresh line:
                    if surf_width > max_width:
                        # This segment is too big even for an empty line → split it
                        remaining = txt
                        while remaining:
                            take = self._fit_prefix_with_font(font, remaining, max_width)
                            part = remaining[:take]
                            part_surf = font.render(part, True, chunk_color)
                            if len(remaining) > take:
                                screen.blit(part_surf, (x, y))
                                y += self.font.get_linesize()
                                remaining = remaining[take:].lstrip(' ')
                            else:
                                # Keep the last fragment in the buffer for normal flow
                                current_line_chunks = [(part_surf, part)]
                                current_line_width = part_surf.get_width()
                                remaining = ''
                    else:
                        # Fits on fresh line as-is
                        current_line_chunks = [(surf, txt)]
                        current_line_width = surf_width
                else:
                    # Append to current line
                    current_line_chunks.append((surf, txt))
                    current_line_width += surf_width

            # Flush the last buffered line for this raw_line
            if current_line_chunks:
                pos_x = x
                for s_, _txt in current_line_chunks:
                    screen.blit(s_, (pos_x, y))
                    pos_x += s_.get_width()
                y += self.font.get_linesize()

    # --------------------
    # Internals
    # --------------------
    def _get_styled_font(self, bold=False, italic=False, underline=False):
        key = (bold, italic, underline)
        if key not in self.font_cache:
            font = pygame.font.Font(self.font_path, self.font_size)
            font.set_bold(bold)
            font.set_italic(italic)
            font.set_underline(underline)
            self.font_cache[key] = font
        return self.font_cache[key]

    def _fit_prefix_with_font(self, font, text, max_width):
        """
        Return number of characters from `text` that fit within `max_width`.
        Tries to cut at whitespace; falls back to char-level binary search.
        """
        if not text:
            return 0
        # Fast path: everything fits
        if font.size(text)[0] <= max_width:
            return len(text)

        lo, hi, best = 1, len(text), 0
        while lo <= hi:
            mid = (lo + hi) // 2
            width = font.size(text[:mid])[0]
            if width <= max_width:
                best = mid
                lo = mid + 1
            else:
                hi = mid - 1

        if best <= 0:
            return 1  # make progress even on tiny widths

        # Prefer breaking at the last space within the slice
        snap = text.rfind(' ', 0, best)
        if snap != -1 and snap > 0:
            return snap
        return best

    def _render_chunk(self, text, default_color):
        """
        Return (surface, plain_text, (font, color)) for a single formatted chunk.
        Supports ***bold+italic***, **bold**, *italic*, __underline__, [color=...][/color].
        Allows bold/italic/underline INSIDE color tags.
        """
        chunk_color = default_color
        bold = italic = underline = False

        # [color=red]text[/color] or [color=#hex]text[/color]
        color_match = re.match(r'^\[color=(.+?)\](.+?)\[/color\]$', text)
        if color_match:
            color_str = color_match.group(1).strip()
            inner = color_match.group(2)
            try:
                chunk_color = pygame.Color(color_str)
            except ValueError:
                chunk_color = default_color
            # Now allow *** / ** / * / __ inside the colored text
            biu = self._parse_biu(inner)
            inner_text, bold, italic, underline = biu
            font = self._get_styled_font(bold, italic, underline)
            surface = font.render(inner_text, True, chunk_color)
            return surface, inner_text, (font, chunk_color)

        # No color: parse BIU combos on the whole segment
        inner_text, bold, italic, underline = self._parse_biu(text)
        font = self._get_styled_font(bold, italic, underline)
        surface = font.render(inner_text, True, chunk_color)
        return surface, inner_text, (font, chunk_color)

    def _parse_biu(self, text):
        """
        Parse bold/italic/underline markers for the whole segment.
        Returns (plain_text, bold, italic, underline).
        Order matters: *** first, then **, then *, then __.
        """
        # ***bold+italic***
        m = re.match(r'^\*\*\*(.+?)\*\*\*$', text)
        if m:
            return m.group(1), True, True, False
        # **bold**
        m = re.match(r'^\*\*(.+?)\*\*$', text)
        if m:
            return m.group(1), True, False, False
        # *italic*
        m = re.match(r'^\*(.+?)\*$', text)
        if m:
            return m.group(1), False, True, False
        # __underline__
        m = re.match(r'^__(.+?)__$', text)
        if m:
            return m.group(1), False, False, True
        # plain text
        return text, False, False, False
