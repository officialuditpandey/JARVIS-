#!/usr/bin/env python3
"""
Browser Service for JARVIS - Phase 3 Ghost Browser
Web Agent functionality using Playwright with advanced capabilities
"""

import os
import asyncio
import json
import re
from typing import Dict, Any, Optional, List
from datetime import datetime
import sys

# Add JARVIS backend path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from playwright.async_api import async_playwright, Browser, BrowserContext, Page
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    print("Playwright not available - browser service disabled")
    PLAYWRIGHT_AVAILABLE = False

class BrowserService:
    """Ghost Browser service for web automation and search"""
    
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.is_running = False
        self.headless = True
        self.current_url = ""
        self.page_history = []
        
        # Ghost Browser settings
        self.ghost_mode = True
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        
        print("Ghost Browser Service initialized")
    
    async def start_browser(self, headless: bool = True) -> bool:
        """Start Ghost Browser instance"""
        if not PLAYWRIGHT_AVAILABLE:
            print("Playwright not available")
            return False
        
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=headless,
                args=[
                    '--no-sandbox',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--disable-gpu'
                ]
            )
            
            # Create context with stealth settings
            self.context = await self.browser.new_context(
                user_agent=self.user_agent,
                viewport={'width': 1920, 'height': 1080},
                ignore_https_errors=True,
                java_script_enabled=True
            )
            
            # Add stealth scripts
            await self.context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
            """)
            
            self.page = await self.context.new_page()
            self.is_running = True
            self.headless = headless
            
            print(f"Ghost Browser started (headless: {headless})")
            return True
            
        except Exception as e:
            print(f"Failed to start Ghost Browser: {e}")
            return False
    
    async def stop_browser(self) -> bool:
        """Stop Ghost Browser instance"""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if hasattr(self, 'playwright'):
                await self.playwright.stop()
            
            self.is_running = False
            print("Ghost Browser stopped")
            return True
            
        except Exception as e:
            print(f"Failed to stop Ghost Browser: {e}")
            return False
    
    async def maps(self, url: str) -> Dict[str, Any]:
        """Navigate to a website (Maps functionality)"""
        if not self.is_running or not self.page:
            return {"success": False, "error": "Browser not running"}
        
        try:
            # Ensure URL has protocol
            if not url.startswith(('http://', 'https://')):
                url = f"https://{url}"
            
            # Add to history
            if self.current_url:
                self.page_history.append(self.current_url)
            
            await self.page.goto(url, timeout=30000, wait_until='domcontentloaded')
            self.current_url = self.page.url
            
            # Wait for page to load
            await self.page.wait_for_load_state('networkidle', timeout=10000)
            
            return {
                "success": True,
                "url": self.page.url,
                "title": await self.page.title(),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def search(self, query: str, search_engine: str = "google") -> Dict[str, Any]:
        """Search Google and return top 3 snippets"""
        if not self.is_running or not self.page:
            return {"success": False, "error": "Browser not running"}
        
        try:
            if search_engine.lower() == "google":
                await self.page.goto("https://www.google.com", timeout=30000)
                
                # Fill search query with fallback selectors
                try:
                    await self.page.fill('textarea[name="q"]', query, timeout=5000)
                    await self.page.press('textarea[name="q"]', 'Enter')
                except:
                    # Fallback to older Google search input
                    await self.page.fill('input[name="q"]', query, timeout=5000)
                    await self.page.press('input[name="q"]', 'Enter')
                
                # Wait for results with fallback
                try:
                    await self.page.wait_for_selector('div.g', timeout=10000)
                except:
                    await self.page.wait_for_selector('h3', timeout=5000)  # Fallback to h3 elements
                
                # Extract top 3 snippets
                snippets = []
                results = await self.page.query_selector_all('div.g')
                
                for i, result in enumerate(results[:3]):
                    try:
                        # Get title
                        title_elem = await result.query_selector('h3')
                        title = await title_elem.inner_text() if title_elem else "No title"
                        
                        # Get snippet
                        snippet_elem = await result.query_selector('div.VwiC3b')
                        snippet = await snippet_elem.inner_text() if snippet_elem else "No snippet"
                        
                        # Get URL
                        link_elem = await result.query_selector('a')
                        url = await link_elem.get_attribute('href') if link_elem else ""
                        
                        snippets.append({
                            "rank": i + 1,
                            "title": title,
                            "snippet": snippet,
                            "url": url
                        })
                        
                    except Exception as e:
                        print(f"Error extracting result {i+1}: {e}")
                        continue
                
                self.current_url = self.page.url
                
                return {
                    "success": True,
                    "query": query,
                    "search_engine": search_engine,
                    "results": snippets,
                    "total_results": len(snippets),
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {"success": False, "error": f"Search engine {search_engine} not supported"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def scrape_text(self, clean: bool = True) -> Dict[str, Any]:
        """Read the text of the current page"""
        if not self.is_running or not self.page:
            return {"success": False, "error": "Browser not running"}
        
        try:
            # Get page title
            title = await self.page.title()
            
            # Get all text content
            body_text = await self.page.inner_text('body')
            
            if clean:
                # Clean up the text
                body_text = re.sub(r'\s+', ' ', body_text)  # Replace multiple spaces
                body_text = re.sub(r'\n\s*\n', '\n\n', body_text)  # Replace multiple newlines
                body_text = body_text.strip()
            
            # Extract metadata
            url = self.page.url
            timestamp = datetime.now().isoformat()
            
            # Split into paragraphs for better readability
            paragraphs = [p.strip() for p in body_text.split('\n\n') if p.strip()]
            
            return {
                "success": True,
                "url": url,
                "title": title,
                "full_text": body_text,
                "paragraphs": paragraphs,
                "paragraph_count": len(paragraphs),
                "word_count": len(body_text.split()),
                "timestamp": timestamp
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def go_back(self) -> bool:
        """Go back in browser history"""
        if not self.is_running or not self.page:
            return False
        
        try:
            await self.page.go_back()
            self.current_url = self.page.url
            return True
        except:
            return False
    
    async def go_forward(self) -> bool:
        """Go forward in browser history"""
        if not self.is_running or not self.page:
            return False
        
        try:
            await self.page.go_forward()
            self.current_url = self.page.url
            return True
        except:
            return False
    
    async def refresh(self) -> bool:
        """Refresh current page"""
        if not self.is_running or not self.page:
            return False
        
        try:
            await self.page.reload()
            return True
        except:
            return False
    
    async def take_screenshot(self, filename: str = None) -> str:
        """Take screenshot of current page"""
        if not self.is_running or not self.page:
            return ""
        
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"ghost_browser_screenshot_{timestamp}.png"
            
            await self.page.screenshot(path=filename)
            return filename
        except Exception as e:
            print(f"Screenshot failed: {e}")
            return ""
    
    def get_status(self) -> Dict[str, Any]:
        """Get Ghost Browser service status"""
        return {
            "is_running": self.is_running,
            "headless": self.headless,
            "ghost_mode": self.ghost_mode,
            "current_url": self.current_url,
            "history_count": len(self.page_history),
            "playwright_available": PLAYWRIGHT_AVAILABLE,
            "last_updated": datetime.now().isoformat()
        }
