import requests
from bs4 import BeautifulSoup
import time
import logging
import re
from urllib.parse import urljoin, quote_plus
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

logger = logging.getLogger(__name__)

class ScraperService:
    """Service for scraping music from various sources"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.base_urls = {
            'masstamilan': 'https://masstamilan.dev',
            'backup_masstamilan': 'https://www.masstamilan.com'
        }
    
    def get_driver(self):
        """Setup Chrome driver for Selenium"""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            
            driver = webdriver.Chrome(
                ChromeDriverManager().install(),
                options=chrome_options
            )
            return driver
        except Exception as e:
            logger.error(f"Failed to setup Chrome driver: {str(e)}")
            return None
    
    def clean_search_query(self, query):
        """Clean and optimize search query"""
        # Remove special characters and extra spaces
        query = re.sub(r'[^\w\s]', ' ', query)
        query = ' '.join(query.split())
        
        # Remove common words that might interfere with search
        stop_words = ['original', 'soundtrack', 'ost', 'feat', 'featuring', 'remix', 'version']
        words = query.lower().split()
        words = [word for word in words if word not in stop_words]
        
        return ' '.join(words)
    
    def search_masstamilan(self, query):
        """Search for songs on masstamilan with multiple fallback strategies"""
        try:
            cleaned_query = self.clean_search_query(query)
            logger.info(f"🔍 Searching for: {cleaned_query}")
            
            # Try multiple search approaches
            search_results = []
            
            # Method 1: Direct search on main site
            results1 = self._search_masstamilan_direct(cleaned_query, self.base_urls['masstamilan'])
            search_results.extend(results1)
            
            # Method 2: Try backup site if main site failed
            if not search_results:
                logger.info("Trying backup site...")
                results2 = self._search_masstamilan_direct(cleaned_query, self.base_urls['backup_masstamilan'])
                search_results.extend(results2)
            
            # Method 3: Try with Selenium if direct methods failed
            if not search_results:
                logger.info("Trying with Selenium...")
                results3 = self._search_masstamilan_selenium(cleaned_query)
                search_results.extend(results3)
            
            # Method 4: Try with different query variations
            if not search_results:
                logger.info("Trying query variations...")
                variations = self._generate_query_variations(cleaned_query)
                for variation in variations:
                    results4 = self._search_masstamilan_direct(variation, self.base_urls['masstamilan'])
                    search_results.extend(results4)
                    if search_results:  # Stop if we found something
                        break
            
            # Remove duplicates and filter results
            unique_results = self._filter_and_deduplicate_results(search_results)
            
            logger.info(f"✅ Found {len(unique_results)} unique search results")
            return unique_results[:20]  # Limit to top 20 results
            
        except Exception as e:
            logger.error(f"❌ Error searching masstamilan: {str(e)}")
            return []
    
    def _generate_query_variations(self, query):
        """Generate different variations of the search query"""
        variations = []
        
        # Remove common words one by one
        words = query.split()
        if len(words) > 2:
            for i in range(len(words)):
                variation = ' '.join(words[:i] + words[i+1:])
                if len(variation.strip()) > 3:
                    variations.append(variation.strip())
        
        # Try just the first few words
        if len(words) > 2:
            variations.append(' '.join(words[:2]))
            variations.append(' '.join(words[:3]))
        
        # Try different character replacements
        variations.append(query.replace(' ', '+'))
        variations.append(query.replace('&', 'and'))
        variations.append(query.replace('and', '&'))
        
        return list(set(variations))[:5]  # Return up to 5 unique variations
    
    def _filter_and_deduplicate_results(self, results):
        """Filter and remove duplicate search results"""
        seen_urls = set()
        seen_titles = set()
        filtered_results = []
        
        for result in results:
            url = result.get('url', '')
            title = result.get('title', '').lower().strip()
            
            # Skip if we've seen this URL or very similar title
            if url in seen_urls or title in seen_titles:
                continue
            
            # Skip if title is too short or contains unwanted content
            if len(title) < 5 or any(word in title.lower() for word in ['advertisement', 'ad', 'promo']):
                continue
            
            seen_urls.add(url)
            seen_titles.add(title)
            filtered_results.append(result)
        
        return filtered_results
    
    def _search_masstamilan_direct(self, query, base_url=None):
        """Direct search using requests"""
        try:
            if not base_url:
                base_url = self.base_urls['masstamilan']
                
            search_url = f"{base_url}/?s={quote_plus(query)}"
            logger.debug(f"Searching URL: {search_url}")
            
            # Add random delay to avoid being blocked
            time.sleep(random.uniform(0.5, 1.5))
            
            response = self.session.get(search_url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            
            # Look for song links with multiple selectors
            selectors = [
                'a[href*="/songs/"]',
                'a[href*="/movie/"]', 
                'a[href*="/album/"]',
                '.entry-title a',
                '.post-title a',
                'h2 a',
                'h3 a'
            ]
            
            for selector in selectors:
                links = soup.select(selector)
                for link in links:
                    href = link.get('href')
                    if href and any(keyword in href.lower() for keyword in ['/songs/', '/movie/', '/album/']):
                        full_url = urljoin(base_url, href)
                        title = link.get_text(strip=True)
                        
                        if title and len(title) > 5:  # Filter out empty or very short titles
                            results.append({
                                'url': full_url,
                                'title': title,
                                'source': 'masstamilan_direct'
                            })
            
            logger.debug(f"Direct search found {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Direct search failed for {query}: {str(e)}")
            return []
    
    def _search_masstamilan_selenium(self, query):
        """Search using Selenium for dynamic content"""
        driver = None
        try:
            driver = self.get_driver()
            if not driver:
                return []
            
            search_url = f"{self.base_urls['masstamilan']}/?s={quote_plus(query)}"
            driver.get(search_url)
            
            # Wait for content to load
            time.sleep(3)
            
            results = []
            
            # Find song links
            links = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/songs/"], a[href*="/movie/"], a[href*="/album/"]')
            
            for link in links:
                try:
                    href = link.get_attribute('href')
                    title = link.text.strip()
                    if href and title and len(title) > 5:
                        results.append({
                            'url': href,
                            'title': title,
                            'source': 'masstamilan'
                        })
                except:
                    continue
            
            return results
            
        except Exception as e:
            logger.error(f"Selenium search failed: {str(e)}")
            return []
        finally:
            if driver:
                driver.quit()
    
    def get_download_links(self, song_page_url):
        """Extract download links from a song page"""
        try:
            logger.info(f"Extracting download links from: {song_page_url}")
            
            response = self.session.get(song_page_url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            download_links = []
            
            # Look for direct MP3 links
            for link in soup.find_all('a', href=True):
                href = link['href']
                if href.endswith('.mp3') or 'download' in href.lower():
                    download_links.append(href)
            
            # Look for embedded audio elements
            for audio in soup.find_all('audio'):
                src = audio.get('src')
                if src and src.endswith('.mp3'):
                    download_links.append(src)
            
            # Look for JavaScript-generated links
            script_tags = soup.find_all('script')
            for script in script_tags:
                if script.string:
                    # Extract URLs from JavaScript
                    urls = re.findall(r'https?://[^\s"\']+\.mp3', script.string)
                    download_links.extend(urls)
            
            # Clean and validate links
            valid_links = []
            for link in download_links:
                if link.startswith('http') and link.endswith('.mp3'):
                    valid_links.append(link)
                elif link.startswith('/'):
                    full_link = urljoin(song_page_url, link)
                    valid_links.append(full_link)
            
            # Remove duplicates
            unique_links = list(dict.fromkeys(valid_links))
            
            logger.info(f"Found {len(unique_links)} download links")
            return unique_links
            
        except Exception as e:
            logger.error(f"Error extracting download links: {str(e)}")
            return []
    
    def get_download_links_selenium(self, song_page_url):
        """Get download links using Selenium for JavaScript-heavy pages"""
        driver = None
        try:
            driver = self.get_driver()
            if not driver:
                return []
            
            driver.get(song_page_url)
            time.sleep(5)  # Wait for JavaScript to load
            
            download_links = []
            
            # Look for download buttons or links
            download_elements = driver.find_elements(By.CSS_SELECTOR, 
                'a[href$=".mp3"], button[onclick*="download"], .download-link, .download-btn')
            
            for element in download_elements:
                try:
                    href = element.get_attribute('href')
                    onclick = element.get_attribute('onclick')
                    
                    if href and href.endswith('.mp3'):
                        download_links.append(href)
                    elif onclick:
                        # Extract URL from onclick JavaScript
                        urls = re.findall(r'https?://[^\s"\']+\.mp3', onclick)
                        download_links.extend(urls)
                except:
                    continue
            
            return list(dict.fromkeys(download_links))
            
        except Exception as e:
            logger.error(f"Selenium download link extraction failed: {str(e)}")
            return []
        finally:
            if driver:
                driver.quit()
    
    def validate_download_link(self, url):
        """Validate if a download link is working"""
        try:
            response = self.session.head(url, timeout=10)
            content_type = response.headers.get('content-type', '').lower()
            
            return (response.status_code == 200 and 
                   ('audio' in content_type or 'mpeg' in content_type))
        except:
            return False
