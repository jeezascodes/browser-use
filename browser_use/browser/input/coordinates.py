"""
Utilities for calculating physical click coordinates taking into account
browser position and UI elements.
"""

import platform
from typing import TypedDict

import pyautogui


class ElementBounds(TypedDict):
    """Element position and size"""
    x: int
    y: int
    width: int
    height: int


class WindowBounds(TypedDict):
    """Browser window position on screen"""
    x: int
    y: int


class BrowserOffsets(TypedDict):
    """Browser UI element sizes"""
    header: int    # Height of browser header/toolbar
    border: int    # Window border width
    sidebar: int   # Width of any sidebar (devtools, etc)


class ScreenBounds(TypedDict):
    """Screen dimensions"""
    width: int
    height: int


DEFAULT_BROWSER_OFFSETS = BrowserOffsets(
    header=80,     # Standard Chrome header height
    border=2,      # Standard window border
    sidebar=0      # No sidebar by default
)


def get_screen_bounds() -> ScreenBounds:
    """
    Get the primary screen dimensions using the most appropriate method
    for the current platform.
    
    Returns:
        ScreenBounds containing width and height of primary screen
    """
    # For now, use pyautogui's cross-platform solution
    width, height = pyautogui.size()
    return ScreenBounds(width=width, height=height)


def calculate_click_coordinates(
    element_bounds: ElementBounds,
    window_bounds: WindowBounds,
    browser_offsets: BrowserOffsets = DEFAULT_BROWSER_OFFSETS,
    validate_bounds: bool = True
) -> tuple[int, int]:
    """
    Calculate the actual screen coordinates for clicking an element.
    
    Args:
        element_bounds: Element's position and size relative to page
        window_bounds: Browser window's position on screen
        browser_offsets: Browser UI element sizes (header, borders, etc)
        validate_bounds: Whether to validate coordinates are within screen bounds
        
    Returns:
        Tuple of (x, y) screen coordinates targeting element's center
    
    Raises:
        ValueError: If coordinates are outside screen bounds and validate_bounds is True
    """
    # Calculate element's center point
    element_center_x = element_bounds['x'] + (element_bounds['width'] / 2)
    element_center_y = element_bounds['y'] + (element_bounds['height'] / 2)

    # Adjust for window position and browser UI
    screen_x = int(window_bounds['x'] + element_center_x + browser_offsets['border'])
    screen_y = int(window_bounds['y'] + element_center_y + browser_offsets['header'] + browser_offsets['border'])

    # Validate coordinates are within screen bounds if requested
    if validate_bounds:
        screen_bounds = get_screen_bounds()
        if not is_coordinate_on_screen((screen_x, screen_y), screen_bounds):
            raise ValueError(
                f"Calculated coordinates ({screen_x}, {screen_y}) are outside "
                f"screen bounds ({screen_bounds['width']}, {screen_bounds['height']})"
            )
    
    return (screen_x, screen_y)


def is_coordinate_on_screen(
    coordinates: tuple[int, int],
    screen_bounds: ScreenBounds
) -> bool:
    """
    Verify if coordinates are within screen bounds.
    
    Args:
        coordinates: Tuple of (x, y) screen coordinates
        screen_bounds: Screen dimensions
        
    Returns:
        True if coordinates are within screen bounds
    """
    x, y = coordinates
    return (0 <= x < screen_bounds['width'] and 
            0 <= y < screen_bounds['height'])


def adjust_coordinates_for_dpi(
    coordinates: tuple[int, int],
    dpi_scale: float = 1.0
) -> tuple[int, int]:
    """
    Adjust coordinates for screen DPI scaling.
    
    Args:
        coordinates: Tuple of (x, y) screen coordinates
        dpi_scale: DPI scaling factor (e.g., 1.5 for 150% scaling)
        
    Returns:
        Tuple of adjusted (x, y) coordinates
    """
    x, y = coordinates
    return (int(x * dpi_scale), int(y * dpi_scale))