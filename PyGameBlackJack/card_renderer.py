from functools import lru_cache
from pathlib import Path
from typing import Iterable, Tuple, Optional

import pygame

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PNG_CARDS_DIR = PROJECT_ROOT / "MiscProjectFiles" / "PlayingCards" / "PNG-cards"

# Diagnostics flags
_PLACEHOLDER_USED = False
_RENDER_BACKEND = "placeholder"

# Reasonable default aspect ratio for poker cards (width:height)
CARD_AR = 63 / 88  # ~0.716


@lru_cache(maxsize=512)
def load_svg_as_surface(svg_path: Path, target_height: int = 180) -> pygame.Surface:
    """
    Load a card image as a pygame Surface using pre-rendered PNG assets.

    Accepts incoming Paths that may point to SVG files; those are mapped to the
    corresponding PNG file in MiscProjectFiles/PlayingCards/PNG-cards.

    If loading fails, returns a placeholder surface with the card name.

    Caches by (input path, target_height).
    """
    in_path = Path(svg_path)
    width = int(target_height * CARD_AR)

    def _placeholder(color=(240, 240, 240, 255), border=(0, 0, 0), text: Optional[str] = None) -> pygame.Surface:
        global _PLACEHOLDER_USED, _RENDER_BACKEND
        _PLACEHOLDER_USED = True
        _RENDER_BACKEND = "placeholder"
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

    # Determine the PNG path
    def _map_to_png_path(p: Path) -> Path:
        name = p.name
        # flip extension to .png
        name = Path(name).with_suffix('.png').name
        # If path includes SVG-cards-1.3, redirect to PNG-cards directory
        try:
            parts = list(p.parts)
            if 'SVG-cards-1.3' in parts:
                return PNG_CARDS_DIR / name
        except Exception:
            pass
        # If already a PNG somewhere, use it directly
        if p.suffix.lower() == '.png':
            return p
        # Default: assume filename exists in PNG_CARDS_DIR
        return PNG_CARDS_DIR / name

    png_path = _map_to_png_path(in_path)

    # Missing asset handling
    if not png_path.exists() or not png_path.is_file():
        try:
            print(f"[card_renderer] Missing PNG card asset: {png_path} (from {in_path})")
        except Exception:
            pass
        return _placeholder(color=(160, 0, 0, 255), text=(in_path.name or "missing"))

    try:
        surf = pygame.image.load(str(png_path)).convert_alpha()
        # Scale to requested height preserving AR
        if surf.get_height() != target_height:
            scale_ratio = target_height / max(1, surf.get_height())
            new_size = (int(max(1, surf.get_width()) * scale_ratio), target_height)
            surf = pygame.transform.smoothscale(surf, new_size)
        global _RENDER_BACKEND
        _RENDER_BACKEND = "png"
        return surf
    except Exception as e:
        try:
            print(f"[card_renderer] Failed to load PNG '{png_path}': {e}")
        except Exception:
            pass
        return _placeholder(text=in_path.stem)


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
    """Return renderer diagnostics for the image renderer."""
    return {
        'placeholder_used': _PLACEHOLDER_USED,
        'backend': globals().get('_RENDER_BACKEND', 'unknown'),
    }
