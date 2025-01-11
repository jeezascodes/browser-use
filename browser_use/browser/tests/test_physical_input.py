import pytest
from playwright.async_api import Page
import pyautogui

from browser_use.browser.input.controller import PhysicalInputController
from browser_use.dom.views import DOMElementNode

@pytest.fixture
def controller():
    return PhysicalInputController()

@pytest.fixture
def mock_element_node():
    """Creates a mock DOM element for testing"""
    return DOMElementNode(
        tag_name='button',
        xpath='//button[1]',
        attributes={'class': 'test-button'},
        children=[],
        is_visible=True,
        is_interactive=True,
        is_top_element=True,
        parent=None
    )

@pytest.fixture
async def test_page(browser):
    """Creates a test page with a button element"""
    page = await browser.new_page()
    await page.set_content('''
        <html>
            <body>
                <button class="test-button">Test Button</button>
            </body>
        </html>
    ''')
    return page

class TestPhysicalInputController:
    
    async def test_get_element_coordinates(self, controller, mock_element_node, test_page):
        """Test coordinate conversion returns valid screen coordinates"""
        x, y = await controller.get_element_coordinates(test_page, mock_element_node)
        
        # Coordinates should be integers
        assert isinstance(x, int)
        assert isinstance(y, int)
        
        # Coordinates should be within screen bounds
        screen_width, screen_height = pyautogui.size()
        assert 0 <= x <= screen_width
        assert 0 <= y <= screen_height

    async def test_verify_element_position(self, controller, mock_element_node, test_page):
        """Test element position verification with valid coordinates"""
        # Get real coordinates
        x, y = await controller.get_element_coordinates(test_page, mock_element_node)
        
        # Verify position
        is_valid = await controller.verify_element_position(test_page, mock_element_node, x, y)
        assert is_valid is True

    async def test_verify_invalid_position(self, controller, mock_element_node, test_page):
        """Test element position verification fails with invalid coordinates"""
        is_valid = await controller.verify_element_position(test_page, mock_element_node, -1, -1)
        assert is_valid is False

    async def test_mock_coordinates(self, controller, mock_element_node, test_page):
        """Test mock coordinates for testing"""
        # Set mock coordinates
        mock_x, mock_y = 100, 100
        controller.set_mock_coordinates(mock_x, mock_y)
        
        # Get coordinates should return mock values
        x, y = await controller.get_element_coordinates(test_page, mock_element_node)
        assert (x, y) == (mock_x, mock_y)
        
        # Clear mock coordinates
        controller.set_mock_coordinates(None, None)
        
        # Should now return real coordinates
        x, y = await controller.get_element_coordinates(test_page, mock_element_node)
        assert (x, y) != (mock_x, mock_y)

    @pytest.mark.integration
    async def test_perform_click(self, controller):
        """Test physical click moves mouse to position"""
        # Get current mouse position
        start_x, start_y = pyautogui.position()
        
        # Click at different position
        test_x, test_y = start_x + 100, start_y + 100
        await controller.perform_click(test_x, test_y)
        
        # Verify mouse moved
        end_x, end_y = pyautogui.position()
        assert abs(end_x - test_x) <= 2  # Allow small margin of error
        assert abs(end_y - test_y) <= 2

    @pytest.mark.integration
    async def test_type_text(self, controller):
        """Test physical keyboard input"""
        # Note: This test requires a text editor or input field to be in focus
        test_text = "test input"
        await controller.type_text(test_text, click_first=False)
        # Real verification would require OCR or clipboard checking
        
    @pytest.mark.integration
    async def test_scroll(self, controller):
        """Test physical scroll action"""
        await controller.scroll(-100)  # Scroll down
        await controller.scroll(100)   # Scroll up
        # Visual verification required for scroll tests

    async def test_error_handling(self, controller, mock_element_node, test_page):
        """Test error handling for invalid element"""
        # Create invalid element node
        invalid_element = DOMElementNode(
            tag_name='button',
            xpath='//button[999]',  # Non-existent element
            attributes={},
            children=[],
            is_visible=True,
            is_interactive=True,
            is_top_element=True,
            parent=None
        )
        
        # Should raise ValueError for non-existent element
        with pytest.raises(ValueError):
            await controller.get_element_coordinates(test_page, invalid_element)

if __name__ == "__main__":
    pytest.main(["-v", "test_controller.py"])