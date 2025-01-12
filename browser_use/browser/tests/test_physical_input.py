import pytest
from browser_use.browser.browser import Browser, BrowserConfig
from browser_use.browser.context import BrowserContext

TEST_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Physical Input Test</title>
    <style>
        .container { padding: 20px; }
        #result { margin-top: 10px; }
        body { min-height: 2000px; }  /* Force page to be taller */
        #scrollTarget { 
            position: absolute;
            top: 1000px;
            padding: 20px;
            background: #eee;
            border: 1px solid #ccc;
        }
    </style>
</head>
<body>
    <div class="container">
        <button id="testButton" onclick="document.getElementById('result').textContent = 'Button Clicked!'">
            Click Me
        </button>
        <input id="testInput" type="text" oninput="document.getElementById('inputResult').textContent = this.value">
        <div id="result"></div>
        <div id="inputResult"></div>
        <div id="scrollTarget">Scroll Target</div>
    </div>
</body>
</html>
"""

@pytest.fixture
async def physical_browser():
    """Create a browser with physical input enabled"""
    config = BrowserConfig(
        use_physical_input=True,
        physical_input_actions={'click_element', 'input_text', 'scroll_down', 'scroll_up'},
        headless=False  # Need to see the browser for physical input
    )
    browser = Browser(config=config)
    yield browser
    await browser.close()

@pytest.fixture
async def context(physical_browser):
    """Create a context and set up test page"""
    context = await physical_browser.new_context()
    page = await context.get_current_page()
    await page.set_content(TEST_HTML)
    yield context
    await context.close()

@pytest.mark.asyncio
async def test_physical_input_initialization(physical_browser, context):
    """Test that physical input controller is properly initialized"""
    assert context.physical_input is not None
    assert physical_browser.config.use_physical_input is True

@pytest.mark.asyncio
async def test_physical_click(context):
    """Test physical clicking of a button"""
    # Get initial state
    state = await context.get_state()
    
    # Find the button in the selector map
    button_element = None
    for element in state.selector_map.values():
        if element.tag_name == 'button' and element.attributes.get('id') == 'testButton':
            button_element = element
            break
    
    assert button_element is not None, "Button element not found"
    
    # Click the button
    await context._click_element_node(button_element)
    
    # Verify the click worked by checking the result text
    page = await context.get_current_page()
    result_text = await page.evaluate('() => document.getElementById("result").textContent')
    assert result_text == 'Button Clicked!'

@pytest.mark.asyncio
async def test_physical_input(context):
    """Test physical text input"""
    # Get initial state
    state = await context.get_state()
    
    # Find the input element
    input_element = None
    for element in state.selector_map.values():
        if element.tag_name == 'input' and element.attributes.get('id') == 'testInput':
            input_element = element
            break
    
    assert input_element is not None, "Input element not found"
    
    # Type into the input
    test_text = "Hello, Physical Input!"
    await context._input_text_element_node(input_element, test_text)
    
    # Verify the input worked
    page = await context.get_current_page()
    input_result = await page.evaluate('() => document.getElementById("inputResult").textContent')
    assert input_result == test_text

# @pytest.mark.asyncio
# async def test_physical_scroll(context):
#     """Test physical scrolling"""
#     # Get the current scroll position
#     page = await context.get_current_page()
#     initial_scroll = await page.evaluate('() => window.scrollY')
    
#     # Scroll down
#     await context.scroll_by(500)
    
#     # Get new scroll position
#     new_scroll = await page.evaluate('() => window.scrollY')
#     assert new_scroll > initial_scroll, "Page did not scroll down"
    
#     # Scroll back up
#     await context.scroll_by(-500)
    
#     # Verify we're back at the top
#     final_scroll = await page.evaluate('() => window.scrollY')
#     assert abs(final_scroll - initial_scroll) < 50, "Page did not scroll back up"

# @pytest.mark.asyncio
# async def test_fallback_to_dom(context):
#     """Test fallback to DOM methods when physical input fails"""
#     # Intentionally cause physical input to fail by passing invalid coordinates
#     if context.physical_input:
#         context.physical_input.set_mock_coordinates(-1, -1)
    
#     state = await context.get_state()
#     button_element = next(
#         (el for el in state.selector_map.values() 
#          if el.tag_name == 'button' and el.attributes.get('id') == 'testButton'),
#         None
#     )
    
#     assert button_element is not None, "Button element not found"
    
#     # Click should still work via DOM methods
#     await context._click_element_node(button_element)
    
#     page = await context.get_current_page()
#     result_text = await page.evaluate('() => document.getElementById("result").textContent')
#     assert result_text == 'Button Clicked!'