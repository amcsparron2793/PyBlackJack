from io import BytesIO
from functools import lru_cache
from pathlib import Path
from typing import Iterable, Tuple, Optional

import pygame

from svglib.svglib import svg2rlg
from reportlab import rl_config as _rl_config
from reportlab.graphics import renderPM

# Diagnostics flags
_PLACEHOLDER_USED = False
_RENDER_BACKEND = "placeholder"

# Reasonable default aspect ratio for poker cards (width:height)
CARD_AR = 63 / 88  # ~0.716


@lru_cache(maxsize=512)
def load_svg_as_surface(svg_path: Path, target_height: int = 180) -> pygame.Surface:
    """
    Load an SVG file and rasterize it into a pygame Surface using svglib + reportlab.

    If rendering fails, returns a placeholder surface with the card name.

    Caches by (svg_path, target_height).
    """
    svg_path = Path(svg_path)
    width = int(target_height * CARD_AR)

    def _placeholder(color=(240, 240, 240, 255), border=(0, 0, 0), text: Optional[str] = None) -> pygame.Surface:
        global _PLACEHOLDER_USED
        _PLACEHOLDER_USED = True
        surf = pygame.Surface((width, target_height), pygame.SRCALPHA)
        surf.fill(color)
        try:
            pygame.draw.rect(surf, border, surf.get_rect(), 2)
        except Exception:
            pass
        if text:
            try:
                fnt = pygame.font.Font(None, 18)
                txt = fnt.render(text, True, border)
                rect = txt.get_rect(center=surf.get_rect().center)
                surf.blit(txt, rect)
            except Exception:
                pass
        return surf

    # Treat non-existent paths or directories as missing assets
    if not svg_path.exists() or not svg_path.is_file():
        try:
            print(f"[card_renderer] Missing card asset: {svg_path}")
        except Exception:
            pass
        return _placeholder(color=(160, 0, 0, 255), text=(svg_path.name or "missing"))

    try:
        # FIXME: change this to just open the png's as bytes directly
        png_bytes = _rasterize_svg_to_png_bytes(svg_path, target_height)
        if png_bytes:
            bio = BytesIO(png_bytes)
            # Provide a namehint so pygame can detect PNG format from memory
            surf = pygame.image.load(bio, "card.png").convert_alpha()
            # Some SVGs may not match our AR; scale to expected height while preserving image AR
            if surf.get_height() != target_height:
                scale_ratio = target_height / surf.get_height()
                new_size = (int(surf.get_width() * scale_ratio), target_height)
                surf = pygame.transform.smoothscale(surf, new_size)
            return surf
    except Exception as e:
        print(f"[card_renderer] Rasterizer failed for '{svg_path}': {e}")
    return _placeholder(text=svg_path.stem)


def draw_hand(
    screen: pygame.Surface,
    card_paths: Iterable[Path],
    start_xy: Tuple[int, int],
    target_height: int = 180,
    x_spacing: int = 24,
):
    """Draw a horizontal row of card images given SVG Paths."""
    x, y = start_xy
    for p in card_paths:
        card_surf = load_svg_as_surface(Path(p), target_height)
        screen.blit(card_surf, (x, y))
        x += card_surf.get_width() - x_spacing  # slight overlap for a fanned look



def get_renderer_status():
    """Return renderer diagnostics for the svglib/reportlab renderer."""
    try:
        rl_backend = getattr(_rl_config, 'renderPMBackend', 'unknown')
    except Exception:
        rl_backend = 'unknown'
    return {
        'placeholder_used': _PLACEHOLDER_USED,
        'backend': globals().get('_RENDER_BACKEND', 'unknown'),
        'reportlab_backend': rl_backend,
        'available_backends': {},
    }



def _rasterize_svg_to_png_bytes(svg_path: Path, target_height: int) -> Optional[bytes]:
    """
    Convert SVG to PNG bytes using svglib + reportlab only.
    Returns PNG bytes on success, or None on failure.
    """
    global _RENDER_BACKEND
    try:
        drawing = svg2rlg(str(svg_path))
        if drawing is None or not getattr(drawing, 'height', 0):
            _RENDER_BACKEND = "placeholder"
            return None
        scale = float(target_height) / float(drawing.height)
        drawing.width *= scale
        drawing.height *= scale
        drawing.scale(scale, scale)
        png_bytes = renderPM.drawToString(drawing, fmt='PNG')
        _RENDER_BACKEND = "svglib-reportlab"
        return png_bytes
    except Exception as e:
        # svglib/reportlab path failed; try a minimal CairoSVG fallback if available
        try:
            print(f"[card_renderer] svglib/reportlab failed: {e}")
        except Exception:
            pass
        _RENDER_BACKEND = "placeholder"
        return None
