import asyncio
import random
from playwright.async_api import async_playwright
from config import Config

class HumanBehavior:
    @staticmethod
    def watch_time():
        return random.randint(15, 55)

    @staticmethod
    def should_like():
        return random.random() < Config.LIKE_PROBABILITY

    @staticmethod
    def should_follow():
        return random.random() < Config.FOLLOW_PROBABILITY

    @staticmethod
    def pause_between_actions():
        base = random.randint(Config.MIN_DELAY, Config.MAX_DELAY)
        if random.random() < 0.15:
            base += random.randint(300, 900)
        return base

class TikTokEngine:
    def __init__(self):
        self.proxies = Config.PROXY_LIST
        self.daily_actions = 0

    def _get_proxy(self):
        if not self.proxies:
            return None
        return random.choice(self.proxies)

    async def _browser_context(self):
        p = await async_playwright().start()
        proxy = self._get_proxy()
        
        browser = await p.chromium.launch(
            headless=True,
            proxy={"server": proxy} if proxy else None,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
        )
        
        context = await browser.new_context(
            user_agent=random.choice([
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
            ]),
            viewport={"width": random.choice([1366, 1440, 1920]), "height": random.choice([768, 900, 1080])}
        )
        
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            window.chrome = { runtime: {} };
        """)
        
        return p, browser, context

    async def view_video(self, url: str):
        if self.daily_actions >= Config.MAX_DAILY_ACTIONS:
            return {"success": False, "error": "daily limit reached"}

        p, browser, context = await self._browser_context()
        try:
            page = await context.new_page()
            await page.goto(url, wait_until="domcontentloaded")
            
            await page.mouse.wheel(0, random.randint(200, 600))
            await asyncio.sleep(random.uniform(1, 3))
            
            watch_time = HumanBehavior.watch_time()
            await asyncio.sleep(watch_time)
            
            await page.mouse.wheel(0, random.randint(300, 800))
            await asyncio.sleep(random.uniform(0.5, 1.5))
            
            liked = False
            if HumanBehavior.should_like():
                like_btn = await page.query_selector('[data-e2e="like-icon"]')
                if like_btn:
                    await like_btn.click()
                    liked = True
                    await asyncio.sleep(random.uniform(0.5, 1.5))
            
            followed = False
            if HumanBehavior.should_follow():
                follow_btn = await page.query_selector('[data-e2e="follow-button"]')
                if follow_btn:
                    await follow_btn.click()
                    followed = True
                    await asyncio.sleep(random.uniform(0.5, 1.5))
            
            self.daily_actions += 1
            
            return {
                "success": True,
                "watch_time": watch_time,
                "liked": liked,
                "followed": followed
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            await browser.close()
            await p.stop()

    async def run_campaign(self, targets: list):
        results = []
        for i, target in enumerate(targets):
            if self.daily_actions >= Config.MAX_DAILY_ACTIONS:
                break
            
            result = await self.view_video(target)
            results.append({"target": target, "result": result})
            
            pause = HumanBehavior.pause_between_actions()
            await asyncio.sleep(pause)
            
            if i % random.randint(3, 6) == 0 and i > 0:
                await asyncio.sleep(random.randint(600, 1800))
        
        return results