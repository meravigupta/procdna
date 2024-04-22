import re
import time
import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

excel_file_path = 'li_scrape_data.xlsx'

# Function to clean and format strings
def prettify_string(input_string, num=False):
    # Remove leading and trailing whitespaces
    input_string = input_string.strip()
    # Remove extra whitespaces
    input_string = re.sub(r'\s+', ' ', input_string)
    # Remove special characters
    input_string = re.sub(r'[^\w\s]', '', input_string)
    
    if num:
        # Extract numbers followed by "mo" or "yr" from the string
        match = re.search(r'\b(\d+(?:mo|yr|d))\b', input_string)
        # If a match is found, return it
        if match:
            return match.group(1)
        else:
            numbers = re.findall(r'\d+', input_string)
            if numbers:
                return int(numbers[0])
            else:
                return input_string
    else:
        return input_string

class Linkedin():

    # Method to extract data from a LinkedIn profile
    def getData(self, profile_url):
        # Initialize a Chrome webdriver
        driver = webdriver.Chrome()
        driver.get('https://www.linkedin.com/login')
        
        # Find and populate the username field
        elementID = driver.find_element('id', 'username')
        elementID.send_keys("Enter your mail id here")
        
        # Find and populate the password field
        elementID = driver.find_element('id', 'password')
        elementID.send_keys("Enter your password here")
        
        # Click on the login button
        driver.find_element(By.XPATH, "//*[@type='submit']").click()
        time.sleep(3)
        
        # *********** Search Result *************** #
        profile_info = []
        profile_details = {}
        driver.get(profile_url)
        time.sleep(3)
        
        # Scroll the page to load more content
        start = time.time()
        initialScroll = 0
        finalScroll = 700
        driver.execute_script(f"window.scrollTo({initialScroll}, {finalScroll})")
        time.sleep(5)
        end = time.time()
        
        # Find and click on the link to show all posts
        link_show_all_post = driver.find_element(By.XPATH, "/html/body/div[5]/div[3]/div/div/div[2]/div/div/main/section[3]/footer/a").get_attribute('href')
        if link_show_all_post:
            driver.get(link_show_all_post)
            start = time.time()
            initialScroll = 0
            finalScroll = 1000
            while True:
                driver.execute_script(f"window.scrollTo({initialScroll}, {finalScroll})")
                initialScroll = finalScroll
                finalScroll += 1000
                time.sleep(3)
                end = time.time()
                if round(end - start) > 120:
                    break
            
            # Parse the HTML source of the page
            src = driver.page_source
            soup = BeautifulSoup(src, 'lxml')
            user_name = soup.find("span", {"class": "visually-hidden"})
            if user_name:
                user_name = prettify_string(user_name.text)
                
            # Find all post tags
            all_post_tags = soup.find_all("li", {"class": "profile-creator-shared-feed-update__container"})
            all_post_details = []
            print(len(all_post_tags))
            count = 0
            for post_tag in all_post_tags:
                count +=1
                post_details = {}
                post_date = post_tag.find("a", {"class": "app-aware-link update-components-actor__sub-description-link"})
                if post_date:
                    post_date = prettify_string(post_date.text, num=True)
                    post_details["time_since_post"] = post_date
                post_content = post_tag.find("div", {"class": "feed-shared-update-v2__description-wrapper mr2"})
                if post_content:
                    post_content = prettify_string(post_content.text)
                    post_details["post_content"] = post_content
                number_of_likes = post_tag.find("li", {"class": "social-details-social-counts__item social-details-social-counts__reactions social-details-social-counts__reactions--left-aligned"})
                if number_of_likes:
                    number_of_likes = prettify_string(number_of_likes.text, num=True)
                    post_details["post_likes_reactions"] = number_of_likes
                number_of_comments = post_tag.find("li", {"class": "social-details-social-counts__item social-details-social-counts__comments social-details-social-counts__item--right-aligned"})
                if number_of_comments:
                    number_of_comments = prettify_string(number_of_comments.text, num=True)
                    post_details["post_comments_count"] = number_of_comments
                if post_details:
                    all_post_details.append(post_details)

            profile_details[f"{user_name} post info"] = all_post_details
        df = pd.DataFrame(all_post_details)
        df.to_excel(excel_file_path, index=False)
        print("######## Total post count ########", count)
        print(profile_details)
        driver.quit()

    # Method to validate a URL
    def validate_url(self, url):
        # Regular expression pattern for URL validation
        url_pattern = re.compile(
            r'^(?:http|ftp)s?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
            r'linkedin|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)

        if re.match(url_pattern, url):
            return True
        else:
            return False

    # Method to start the LinkedIn data extraction process
    def start(self):
        profile_url = input("Enter the LinkedIn Profile URL : ")
        if self.validate_url(profile_url):
            self.getData(profile_url)
        else:
            print("Please Enter Valid URL!!")

# Main block
if __name__ == "__main__":
    obJH = Linkedin()
    obJH.start()
