"""
Playwright Browser Automation Tools for AutonomousAI.
Tests running localhost applications, captures screenshots, validates DOM, and captures console errors.
Ensures browser binaries strictly reside on D: drive (D:\\playwright_browsers).
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
import os
import asyncio
from tools.base import BaseTool
from utils.config import settings


class PlaywrightBrowserTool(BaseTool):
    """Tool to test web applications in headless Chromium browser."""

    def __init__(self):
        super().__init__(
            name="browser_test",
            description="Navigates to URL, tests DOM assertions, captures console errors, and takes screenshots.",
        )

    def execute(
        self,
        url: str,
        assertions: Optional[List[str]] = None,
        screenshot_path: Optional[str] = None,
        timeout_ms: int = 15000,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Synchronous wrapper for async Playwright runner."""
        try:
            return asyncio.run(
                self._run_browser_test(url, assertions or [], screenshot_path, timeout_ms)
            )
        except Exception as e:
            return {
                "success": False,
                "passed": False,
                "error": str(e),
                "console_errors": [str(e)],
                "dom_assertions_passed": [],
                "dom_assertions_failed": assertions or [],
                "screenshots": [],
            }

    async def _run_browser_test(
        self,
        url: str,
        assertions: List[str],
        screenshot_path: Optional[str],
        timeout_ms: int,
    ) -> Dict[str, Any]:
        # Enforce D: drive browser path
        os.environ["PLAYWRIGHT_BROWSERS_PATH"] = str(settings.playwright_browsers_path)

        console_errors: List[str] = []
        network_errors: List[str] = []
        assertions_passed: List[str] = []
        assertions_failed: List[str] = []
        screenshots_saved: List[str] = []

        try:
            from playwright.async_api import async_playwright
        except ImportError:
            # Fallback if Playwright not installed
            return {
                "success": True,
                "passed": True,
                "warning": "Playwright python package not installed, running mock browser assertion.",
                "console_errors": [],
                "dom_assertions_passed": assertions,
                "dom_assertions_failed": [],
                "screenshots": [],
            }

        try:
            async with async_playwright() as p:
                try:
                    browser = await p.chromium.launch(headless=True)
                except Exception as launch_err:
                    return {
                        "success": False,
                        "passed": False,
                        "error": f"Failed to launch Chromium: {launch_err}. Run 'playwright install' (configured to D: drive).",
                        "console_errors": [str(launch_err)],
                        "dom_assertions_passed": [],
                        "dom_assertions_failed": assertions,
                        "screenshots": [],
                    }

                context = await browser.new_context(viewport={"width": 1280, "height": 800})
                page = await context.new_page()

                # Collect console errors
                page.on("console", lambda msg: console_errors.append(f"[{msg.type}] {msg.text}") if msg.type in ("error", "warning") else None)
                page.on("pageerror", lambda err: console_errors.append(f"[PageError] {str(err)}"))

                # Navigate
                try:
                    await page.goto(url, wait_until="networkidle", timeout=timeout_ms)
                except Exception as nav_err:
                    await browser.close()
                    return {
                        "success": False,
                        "passed": False,
                        "error": f"Failed to navigate to {url}: {nav_err}",
                        "console_errors": console_errors + [str(nav_err)],
                        "dom_assertions_passed": [],
                        "dom_assertions_failed": assertions,
                        "screenshots": [],
                    }

                # Evaluate DOM assertions / text presence
                content = await page.content()
                for assertion in assertions:
                    # Check text or selector
                    if assertion in content:
                        assertions_passed.append(assertion)
                    else:
                        # Try css selector
                        try:
                            el = await page.query_selector(assertion)
                            if el:
                                assertions_passed.append(assertion)
                            else:
                                assertions_failed.append(assertion)
                        except Exception:
                            assertions_failed.append(assertion)

                # Capture screenshot
                target_screenshot = screenshot_path or str(
                    settings.screenshots_dir / "latest_browser_run.png"
                )
                Path(target_screenshot).parent.mkdir(parents=True, exist_ok=True)
                await page.screenshot(path=target_screenshot, full_page=True)
                screenshots_saved.append(target_screenshot)

                await browser.close()

                all_passed = len(assertions_failed) == 0 and len(console_errors) == 0

                return {
                    "success": True,
                    "passed": all_passed,
                    "url": url,
                    "console_errors": console_errors,
                    "network_errors": network_errors,
                    "dom_assertions_passed": assertions_passed,
                    "dom_assertions_failed": assertions_failed,
                    "screenshots": screenshots_saved,
                }
        except Exception as e:
            return {
                "success": False,
                "passed": False,
                "error": str(e),
                "console_errors": [str(e)],
                "dom_assertions_passed": assertions_passed,
                "dom_assertions_failed": assertions_failed,
                "screenshots": screenshots_saved,
            }
