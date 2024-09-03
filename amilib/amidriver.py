import time
from io import StringIO
from pathlib import Path

from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.remote.webelement import WebElement

from amilib.file_lib import FileLib
from amilib.util import Util

"""This is a problem in PyCharm
see https://stackoverflow.com/questions/64618538/cant-find-webdriver-manager-module-in-pycharm
"""

"""behaves differently in pytest and PyCharm"""
"""I unnstalled 4.0.1 and installed 4.0.0
also rm -rf .idea and restart Pycharm
"""
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException

import lxml.etree as ET

URL = "url"
XPATH = "xpath"
OUTFILE = "out_file"

logger = Util.get_logger(__name__)


class AmiDriver:
    """
    create and wrap a Chrome headless browser
    Author Ayush Garg, modified Peter Murray-Rust
    """

    def __init__(self, sleep=3):
        """
        creates a Chrome WebDriver instance with specified options and settings.
        """
        options = webdriver.ChromeOptions()
        options.page_load_strategy = "none"
        chrome_path = ChromeDriverManager().install()
        chrome_service = Service(chrome_path)
        self.web_driver = Chrome(options=options, service=chrome_service)
        self.lxml_root_elem = None
        self.sleep = sleep

    def set_sleep(self, sleep):
        if sleep is None or sleep < 1:
            logger.error(f"sleep must be >= 1")
            return
        if sleep > 20:
            logger.error(f"sleep must be <= 20")
            sleep = 20
        self.sleep = sleep

#    class AmiDriver:

    def quit(self):
        """quite the web_driver"""
        logger.debug("Quitting the driver...")
        self.web_driver.quit()
        logger.debug("DONE")

    def safe_click_element(self, element):
        """
        attempt to click on a web element
        in a safe manner, handling potential exceptions and using different strategies if necessary.

        a web browser. It allows you to navigate to web pages, interact with elements on the page, and
        perform various actions
        :param element: the web element to click on. It can be any
        valid web element object, such as an instance of `WebElement` class in Selenium
        :param sleep: time to wait
        """
        assert type(element) is WebElement, f"should be WebElement found {type(element)}"
        try:
            # Wait for the element to be clickable
            WebDriverWait(self, self.sleep).until(
                EC.element_to_be_clickable((By.XPATH, element.get_attribute("outerHTML")))
            )
            logger.debug(f"waiting... {self.sleep}")
            element.click()
        except ElementClickInterceptedException:
            # If the element is not clickable, scroll to it and try again
            self.web_driver.execute_script("arguments[0].scrollIntoView();", element)
            element.click()
        except Exception:
            # If it still doesn't work, use JavaScript to click on the element
            self.web_driver.execute_script("arguments[0].click();", element)

    #    class AmiDriver:

    def get_page_source(self, url):
        """
        returns the page source code.

        :param url: The URL of the webpage you want to retrieve the source code from
        :param sleep: sleep time
        :return: the page source of the website after the driver navigates to the specified URL.
        """
        logger.debug(f"Fetching page source from URL: {url}")
        self.web_driver.get(url)
        time.sleep(self.sleep)
        return self.web_driver.page_source

    def click_xpath_list(self, xpath_list):
        if not xpath_list or type(xpath_list) is not list:
            logger.debug(f"no xpath_list {xpath_list}")
            return
        logger.debug(f"Clicking xpaths...{xpath_list}")
        for xpath in xpath_list:
            logger.debug(f"xpath: {xpath}")
            self.click_xpath(xpath)

    #    class AmiDriver:

    def click_xpath(self, xpath):
        """
        find clickable elemnts by xpath and click them
        :param xpath: xpath to click
        :param sleep: wait until click has been executed
        """
        logger.debug(f">>>>before click {xpath} => {self.get_lxml_element_count()}")
        # elements = self.get_lxml_root().xpath(xpath)
        elements = self.web_driver.find_elements(
            By.XPATH,
            xpath,
        )
        logger.debug(f"click found WebElements {len(elements)}")
        for element in elements:
            self.safe_click_element(element)
            logger.debug(f"sleep {self.sleep}")
            time.sleep(self.sleep)  # Wait for the section to expand
        logger.debug(f"<<<<element count after = {self.get_lxml_element_count()}")

    def get_lxml_element_count(self):
        elements = self.get_lxml_root_elem().xpath("//*")
        return len(elements)

    #    class AmiDriver:

    def download_expand_save(self, url, xpath_list, html_out, level=99, sleep=3, pretty_print=True):
        """
        Toplevel convenience class

        :param url: to download
        :param xpath_list: ordered list of Xpaths to click
        :param html_out: file to write
        :param level: number of levels to desend (default = 99)
        :param sleep: seconds to sleep between download (default 3)
        """
        if url is None:
            logger.debug(f"no url given")
            return
        html_source = self.get_page_source(url)
        if xpath_list is None:
            logger.debug(f"no xpath_list specified")
        else:
            self.click_xpath_list(xpath_list[:level])

        if html_out is None:
            logger.debug(f"no output html")
            return
        logger.debug(f"writing ... {html_out}")

    #    class AmiDriver:

    def write_html(self, html_out, html_elem=None, pretty_print=True, debug=False):
        """
        convenience method to write HTML
        :param out_html: output file
        :param html_elem: elem to write, if none uses driver.root_elem
        :param pretty_print: pretty_print (default True)
        :param debug: writes name of file
        """
        if html_elem is None:
            html_elem = self.get_lxml_root_elem()
        ss = ET.tostring(html_elem, pretty_print=pretty_print)
        if debug:
            logger.debug(f"writing {html_out}")

        Path(html_out).parent.mkdir(exist_ok=True, parents=True)
        with open(html_out, 'wb') as f:
            f.write(ss)

    #    class AmiDriver:

    def execute_instruction_dict(self, gloss_dict, keys=None):
        keys = gloss_dict.keys() if not keys else keys
        for key in keys:
            _dict = gloss_dict.get(key)
            if _dict is None:
                logger.debug(f"cannot find key {key}")
                continue
            self.download_expand_save(_dict.get(URL), _dict.get(XPATH), _dict.get(OUTFILE))

    #    class AmiDriver:

    def get_lxml_root_elem(self):
        """Convenience method to query the web_driver DOM
        :param xpath: to query the dom
        :return: elements in Dom satisfying xpath (may be empty list)
        """
        if self.lxml_root_elem is None:
            data = self.web_driver.page_source
            doc = ET.parse(StringIO(data), ET.HTMLParser())
            self.lxml_root_elem = doc.xpath("/*")[0]
            logger.debug(f"elements in lxml_root: {len(self.lxml_root_elem.xpath('//*'))}")
        return self.lxml_root_elem

    #    class AmiDriver:

    def run_from_dict(self, outfile, dikt, declutter=None, keys=None, debug=True):
        """
        reads doc names from dict and creates HTML

        :param outfile: file to write
        :param control: control dict
        :param declutter: elements to remove (default DECLUTTER_BASIC)
        :param keys: list of control keys (default = all)

        """
        self.execute_instruction_dict(dikt, keys=keys)
        root = self.get_lxml_root_elem()
        self.write_html(outfile, pretty_print=True, debug=debug)
        assert Path(outfile).exists(), f"{outfile} should exist"

    #    class AmiDriver:

    def download_and_save(self, outfile, chap, wg, wg_url):
        ch_url = wg_url + f"chapter/{chap}"
        wg_dict = {
            f"wg{wg}_{chap}":
                {
                    URL: ch_url,
                    XPATH: None,  # no expansiom
                    # OUTFILE: spm_outfile_gatsby2 # dont think this gets written
                },
        }
        keys = wg_dict.keys()
        self.run_from_dict(outfile, wg_dict)
        root_elem = self.lxml_root_elem
        self.quit()
        return root_elem



