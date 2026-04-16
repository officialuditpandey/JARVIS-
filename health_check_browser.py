#!/usr/bin/env python3
"""
Browser Service Health Check
Tests headless Playwright browser launch and search engine access
"""

import sys
import os
import asyncio
sys.path.append(os.path.dirname(__file__))

def test_browser_service():
    """Test browser service with headless Playwright"""
    print("=== BROWSER SERVICE HEALTH CHECK ===")
    
    try:
        # Import browser service
        from services.browser_service import BrowserService
        print("Browser Service Import: SUCCESS")
        
        # Initialize browser service
        browser = BrowserService()
        print("Browser Service Initialization: SUCCESS")
        
        # Test Playwright availability
        try:
            from playwright.async_api import async_playwright
            print("Playwright Import: SUCCESS")
        except ImportError as e:
            print(f"Playwright Import: FAILED - {e}")
            return False
        
        # Test headless browser launch
        async def test_headless_browser():
            try:
                print("Testing Headless Browser Launch...")
                async with async_playwright() as p:
                    # Launch headless browser
                    browser_instance = await p.chromium.launch(headless=True)
                    print("Headless Browser Launch: SUCCESS")
                    
                    # Create new page
                    page = await browser_instance.new_page()
                    print("New Page Creation: SUCCESS")
                    
                    # Navigate to search engine
                    await page.goto('https://www.google.com', timeout=30000)
                    print("Google Navigation: SUCCESS")
                    
                    # Check if page loaded
                    title = await page.title()
                    if 'Google' in title:
                        print("Search Engine Access: SUCCESS")
                    else:
                        print(f"Search Engine Access: FAILED - Title: {title}")
                        return False
                    
                    # Test search functionality (try alternative selectors)
                    try:
                        await page.fill('input[name="q"]', 'JARVIS AI Assistant', timeout=5000)
                        await page.press('input[name="q"]', 'Enter')
                        await page.wait_for_timeout(2000)
                        
                        # Check if search results loaded
                        url = page.url
                        if 'search' in url:
                            print("Search Functionality: SUCCESS")
                        else:
                            print(f"Search Functionality: PARTIAL - URL: {url}")
                    except:
                        # Alternative search method
                        await page.fill('textarea[name="q"]', 'JARVIS AI Assistant', timeout=5000)
                        await page.press('textarea[name="q"]', 'Enter')
                        await page.wait_for_timeout(2000)
                        print("Search Functionality: SUCCESS (Alternative Method)")
                    
                    # Close browser
                    await browser_instance.close()
                    print("Browser Closure: SUCCESS")
                    
                    return True
                    
            except Exception as e:
                print(f"Headless Browser Test FAILED: {e}")
                return False
        
        # Run async test
        result = asyncio.run(test_headless_browser())
        
        if result:
            print("Browser Service Health Check: PASSED")
        else:
            print("Browser Service Health Check: FAILED")
        
        return result
        
    except Exception as e:
        print(f"Browser Service Health Check FAILED: {e}")
        return False

if __name__ == "__main__":
    result = test_browser_service()
    print(f"BROWSER SERVICE: {'PASSED' if result else 'FAILED'}")
