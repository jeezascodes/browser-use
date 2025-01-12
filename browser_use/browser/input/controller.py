import logging
import time
from typing import Optional, Tuple

import pyautogui
from playwright.async_api import Page

from browser_use.browser.input.coordinates import (
    ElementBounds,
    WindowBounds,
    calculate_click_coordinates,
    get_screen_bounds
)
from browser_use.dom.views import DOMElementNode

logger = logging.getLogger(__name__)

class PhysicalInputController:
    """
    Handles physical mouse and keyboard interactions through PyAutoGUI.
    Provides methods for converting DOM coordinates to screen coordinates and
    performing physical input actions.
    """

    def __init__(self):
        # Configure PyAutoGUI settings for safety and reliability
        pyautogui.FAILSAFE = True  # Move mouse to corner to abort
        pyautogui.PAUSE = 0.1  # Small pause between actions
        
        # For testing and verification
        self._mock_coordinates: Optional[Tuple[int, int]] = None

    async def get_element_coordinates(
        self,
        page: Page,
        element_node: DOMElementNode
    ) -> Tuple[int, int]:
        """
        Converts DOM element coordinates to screen coordinates.
        
        Args:
            page: Playwright page instance
            element_node: DOM element to get coordinates for
            
        Returns:
            Tuple of (x, y) screen coordinates for element center
        """
        if self._mock_coordinates:
            return self._mock_coordinates

        # Get element position relative to viewport
        bounds = await page.evaluate("""(params) => {
            const element = document.evaluate(
                params.xpath, 
                document, 
                null,
                XPathResult.FIRST_ORDERED_NODE_TYPE, 
                null
            ).singleNodeValue;
            
            if (!element) return null;
            
            const rect = element.getBoundingClientRect();
            return {
                x: rect.left,
                y: rect.top,
                width: rect.width,
                height: rect.height
            };
        }""", {"xpath": element_node.xpath})

        if not bounds:
            raise ValueError(f"Could not find element with xpath: {element_node.xpath}")

        # Get browser window position on screen
        window_position = await page.evaluate("""() => {
            return {
                x: window.screenX || window.screenLeft,
                y: window.screenY || window.screenTop
            };
        }""")

        # Calculate click coordinates using our utility
        element_bounds = ElementBounds(**bounds)
        window_bounds = WindowBounds(**window_position)
        
        return calculate_click_coordinates(
            element_bounds=element_bounds,
            window_bounds=window_bounds,
            validate_bounds=True
        )

    async def perform_click(
        self,
        x: int,
        y: int,
        verify_cursor: bool = True
    ) -> None:
        """
        Performs a physical mouse click at specified coordinates.
        
        Args:
            x: Screen x coordinate to click
            y: Screen y coordinate to click
            verify_cursor: Whether to verify cursor position after movement
        """
        # Move mouse to position
        pyautogui.moveTo(x, y, duration=0.2)
        
        if verify_cursor:
            # Get actual cursor position
            current_x, current_y = pyautogui.position()
            if abs(current_x - x) > 2 or abs(current_y - y) > 2:
                raise ValueError(
                    f"Cursor not at expected position. "
                    f"Expected ({x}, {y}), got ({current_x}, {current_y})"
                )

        # Perform click
        pyautogui.click()
        
        # Small pause to let click register
        time.sleep(0.1)

    async def type_text(
        self,
        text: str,
        x: int | None = None,
        y: int | None = None,
        click_first: bool = True
    ) -> None:
        """
        Types text using physical keyboard input.
        
        Args:
            text: Text to type
            x: Screen x coordinate to click before typing (optional)
            y: Screen y coordinate to click before typing (optional)
            click_first: Whether to click before typing
        """
        if click_first:
            if x is not None and y is not None:
                pyautogui.moveTo(x, y, duration=0.2)
            pyautogui.click()
            time.sleep(0.1)
            
        pyautogui.write(text)

    async def scroll(self, amount: int) -> None:
        """
        Performs physical mouse scroll.
        
        Args:
            amount: Number of units to scroll (positive=up, negative=down)
        """
        pyautogui.scroll(amount)

    def set_mock_coordinates(
        self, 
        x: Optional[int] = None,
        y: Optional[int] = None
    ) -> None:
        """
        Sets mock coordinates for testing.
        
        Args:
            x: Mock x coordinate
            y: Mock y coordinate
        """
        if x is not None and y is not None:
            self._mock_coordinates = (x, y)
        else:
            self._mock_coordinates = None