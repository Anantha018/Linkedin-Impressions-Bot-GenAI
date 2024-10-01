import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
import random
from selenium.webdriver.common.action_chains import ActionChains
from urllib.parse import urlparse, urlunparse

CONNECTIONS_PAGE = "https://www.linkedin.com/search/results/people/"
HOME_PAGE = "https://www.linkedin.com/feed/"
my_connection_profiles_urls = []
temp_profiles_urls = []
all_profiles_urls = []

class LinkedInBot:
    def __init__(self):
        self.driver = None
        options = webdriver.ChromeOptions()
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        # Connect to the existing Chrome session
        options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        # Maximize the window
        options.add_argument("--start-maximized")

        options.add_argument("--disable-blink-features=AutomationControlled")
        
        self.driver = webdriver.Chrome(options=options)
       
    def get_profiles(self):
        return WebDriverWait(self.driver, 20).until(
            EC.presence_of_all_elements_located((By.XPATH, ".//span[@class='entity-result__title-line entity-result__title-line--2-lines ']//a[@class='app-aware-link ' and @href]"))
        )
    
    def iterate_all_the_user_connected_profiles_urls(self):
        first_degree_connections_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, ".//button[@aria-label='1st']"))
        )
        
        if first_degree_connections_button.is_displayed():
            self.driver.execute_script("window.scrollBy(0, 800);")
            time.sleep(3)
            self.driver.execute_script("window.scrollBy(0, -800);")
            all_profiles = self.get_profiles()
            
            for profile in all_profiles:
                profile_url = profile.get_attribute('href')
                if profile_url not in my_connection_profiles_urls:
                    my_connection_profiles_urls.append(profile_url)
    
    def iterate_all_the_profiles_urls(self):
        third_degree_button = WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.XPATH, ".//button[@aria-label='3rd+']"))
        )
        
        if third_degree_button.is_displayed():
            self.driver.execute_script("window.scrollBy(0, 800);")
            time.sleep(3)
            self.driver.execute_script("window.scrollBy(0, -800);")
            time.sleep(3)
            all_profiles = self.get_profiles()
            
            for profile in all_profiles:
                temp_profiles_urls.append(profile.get_attribute('href'))
            
    def search_user_entered_job_titles(self, titles_and_counts):
        try:
            self.driver.get(HOME_PAGE)
            for title, profiles_count in titles_and_counts.items():
                print(f"Searching for: {title}")
                self.driver.get(HOME_PAGE)
                search_box = WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, ".//input[@aria-label='Search']"))
                )
                time.sleep(3)
                temp_profiles_urls.clear()  # Clear before each search
                
                search_box.clear()
                search_box.send_keys(f"{title} @People")
                time.sleep(2)
                search_box.send_keys(Keys.ENTER)
                time.sleep(2)
                
                try:
                    select_people_1 = WebDriverWait(self.driver, 20).until(
                        EC.presence_of_element_located((By.XPATH, ".//button[text()='People']"))
                    )
                    select_people_1.click()
                
                except Exception:
                    print("Skipping people filter...")
                
                try:
                    no_results_found_page = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, ".//section//h2[contains(@class,'ember-view artdeco-empty-state__headline artdeco-empty-state')]"))
                    )
                    if no_results_found_page.is_displayed():
                        print(f"No results found for: {title}")
                        continue
                
                except TimeoutException:
                    third_degree_button = WebDriverWait(self.driver, 20).until(
                        EC.presence_of_element_located((By.XPATH, ".//button[@aria-label='3rd+']"))
                    )
                    
                    third_degree_button.click()
                    
                    # if third_degree_button.is_displayed():
                    current_profile_count = 0
                    while current_profile_count < profiles_count:
                        self.iterate_all_the_profiles_urls()
                        all_profiles_urls.extend(temp_profiles_urls)  # Add profiles to the main list
                        
                        # Scroll to the bottom to make sure the "Next" button is visible
                        self.driver.execute_script("window.scrollBy(0, 800);")
                        time.sleep(3)
                        # Try to find and click the "Next" button
                        try:
                            next_page = WebDriverWait(self.driver, 15).until(
                                EC.element_to_be_clickable((By.XPATH, ".//button[@aria-label='Next']"))
                            )
                            next_page.click()
                            current_profile_count += len(temp_profiles_urls)
                            temp_profiles_urls.clear()  # Clear after each page
                            time.sleep(3)
                        except TimeoutException as e:
                            print("Next button not found or another error:", str(e))
                            break
            
            all_unique_profiles_urls = set()

            for item in all_profiles_urls:
                if item not in all_unique_profiles_urls:
                    all_profiles_urls.append(item)
                    all_unique_profiles_urls.add(item)
            self.go_to_profiles(all_unique_profiles_urls)  # Process all profiles collected
                
        except Exception as e:
            print("An error occurred:", str(e))
  
    def simulate_mouse_hover(self, element):
        """Simulate mouse movement to hover over an element."""
        actions = ActionChains(self.driver)
        actions.move_to_element(element).perform()
        time.sleep(random.uniform(1, 3))  # Random delay between 1 to 3 seconds
    
    def go_to_profiles(self, connection_profiles):
            
        profile_count = 1
        max_profiles = 10

        for profile in connection_profiles:
            try:
                # Parse the URL
                parsed_url = urlparse(profile)
                
                # Rebuild the base URL without query parameters
                base_url = urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, '', '', ''))
                
                # Append "/recent-activity/comments/" to the base URL
                modified_url = base_url + "/recent-activity/comments/"
                self.driver.get(modified_url)
                print(f"Navigating to profile: {modified_url}") 
                # href="https://www.linkedin.com/in/gadivella-sri-486b05328/recent-activity/comments/"                 
                time.sleep(random.uniform(3, 5))
                self.driver.execute_script(f"window.scrollBy(0, 300);")
                
                
                 # Check for the empty page indicator
                try:
                    empty_page = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, ".//p[@class='artdeco-empty-state__message' and text()='Content you post, share, react to, or comment on will be displayed here.']"))
                    )
                    if empty_page.is_displayed():
                        print(f"No comments or posts found for this profile: {profile}")
                        continue  # Skip to the next profile if no activity is found

                except TimeoutException:
                    # If no empty page indicator is found, proceed with the script
                    print(f"Content found for profile: {profile}")
                
                # Try to find and interact with the "Like" button
                try:
                    # Locate the button that is currently not pressed
                    like_button = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, "(.//button[@aria-pressed='false'])[6]"))
                    )

                    # If we found the button that is not liked, we can click it to like it
                    like_button.click()
                    print(f"Liked comment for profile: {profile}")
                    continue

                except TimeoutException:
                    print(f"'Like' button not found for profile: {profile}")

                # Check if the button is liked, if it exists
                try:
                    # Locate the button that is currently pressed (i.e., liked)
                    liked_button = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, "(.//button[@aria-pressed='true'])[6]"))
                    )

                    # If the button is liked, click it to unlike
                    liked_button.click()  # Unlike the button
                    print(f"Unliked comment for profile: {profile}")
                    time.sleep(1)  # Wait for the action to complete

                    # Click it again to like it back
                    liked_button.click()
                    print(f"Liked comment for profile: {profile} again")

                except TimeoutException:
                    print(f"Liked button not found or not liked for profile: {profile}")
                    continue  # Skip to the next profile if 'Liked' button not found

                time.sleep(3)
                profile_count += 1


                # If the profile count reaches the maximum, take a break
                if profile_count >= max_profiles:
                    print(f"Processed {max_profiles} profiles, taking a break...")
                    time.sleep(random.uniform(10, 20))  # Random break duration

                    # Go back to the home page to refresh
                    self.driver.get(HOME_PAGE)
                    time.sleep(random.uniform(5, 10))

                    # Scroll down the home page to simulate activity
                    for i in range(1, 4):
                        self.driver.execute_script(f"window.scrollBy(0, 800 * {i});")
                        time.sleep(random.uniform(2, 4))  # Random delay between scrolls

                        # Try liking a post
                        try:
                            like_post = WebDriverWait(self.driver, 5).until(
                                EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='React Like']"))
                            )
                            self.simulate_mouse_hover(like_post)  # Hover over the like button
                            like_post.click()
                            print("Liked a post.")
                            time.sleep(random.uniform(3, 5))  # Wait after liking
                        except TimeoutException:
                            print("No like button found or timeout occurred. Continuing to the next scroll.")

                    # # Reset the profile count to continue processing
                    profile_count = 0

            except Exception as e:
                print(f"An error occurred while processing {profile}: {str(e)}")    

    def simulate_random_scroll(self):
        """Simulate random scrolling behavior to make bot movements more human-like."""
        scroll_pause = random.uniform(1, 3)
        for _ in range(random.randint(1, 3)):
            scroll_amount = random.randint(300, 1000)
            self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
            time.sleep(scroll_pause)
    
    def iterate_through_pages(self):
        try:
            while True:
                # Iterate through profiles on the current page
                self.iterate_all_the_user_connected_profiles_urls()

                # Scroll to the bottom to make sure the "Next" button is visible
                self.driver.execute_script("window.scrollBy(0, 800);")
                time.sleep(3)
                # Try to find and click the "Next" button
                try:
                    next_page = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, ".//button[@aria-label='Next']"))
                    )
                    next_page.click()
                    time.sleep(3)
                    
                except TimeoutException:
                    print("Reached the last page or 'Next' button not found.")
                    for i in my_connection_profiles_urls:
                        print(i)
                    print(len(my_connection_profiles_urls))
                    self.go_to_profiles(my_connection_profiles_urls)
                    break  # Exit the loop when there is no "Next" button

        except Exception as e:
            print("An error occurred:", str(e))
         
    def go_to_connections_page(self):
        self.driver.get(CONNECTIONS_PAGE)
        try:
            try:
                no_results_found_page = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, ".//section//h2[contains(@class,'ember-view artdeco-empty-state__headline artdeco-empty-state')]"))
                )
                if no_results_found_page.is_displayed():
                   return 
            except:
                first_degree_connections_button = WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, ".//button[@aria-label='1st']"))
                )
                first_degree_connections_button.click()
                time.sleep(3)
                self.iterate_through_pages()
            
        except TimeoutException as e:
            print("Element not found or timeout occurred:", str(e))

    def quit(self):
        try:
            # Quit the WebDriver and close the browser window
            self.driver.quit()
            # A message box after this
        except Exception as e:
            print(f"An error occurred while trying to quit the driver: {e}")
              
if __name__ == "__main__":
    pass
    # bot = LinkedInBot()
    # bot.go_to_connections_page()
    # titles_and_counts = {
    # "Senior Software Engineer": 10,
    # "data scientist": 20
    # }
    # bot.search_user_entered_job_titles(titles_and_counts)

# For windows = "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\chrome-profile"
#or --> & "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\chrome-profile"
# In terminal or powershell 

# For MAC os = /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222&
#!/bin/bash

# Commands to install tkinter:
# pyinstaller --windowed --add-data "Images;Images" --add-data ".env;." --add-data "linkedin_bot.py;." --add-data "get_job_titles.py;." --add-data "job_titles.py;." --hidden-import="PIL" --hidden-import="dotenv" --hidden-import="ttkbootstrap" --add-binary "C:/Python312/tcl/tcl8.6;./tcl/tcl8.6" --add-binary
#  "C:/Python312/tcl/tk8.6;./tcl/tk8.6" get_job_titles.py

# pyinstaller --windowed --add-data "Images;Images" --add-data ".env;." --add-data "linkedin_bot.py;." --add-data "get_job_titles.py;." --add-data "job_titles.py;." --hidden-import="PIL" --hidden-import="dotenv" --hidden-import="ttkbootstrap" --add-binary "C:/Python312/tcl/tcl8.6;./tcl/tcl8.6" --add-binary "C:/Python312/tcl/tk8.6;./tcl/tk8.6" home_screen.py