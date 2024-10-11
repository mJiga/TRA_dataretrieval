from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, TimeoutException

import time

class Script:
    def __init__(self, options):
        chrome_options = webdriver.ChromeOptions()
        prefs = {
            "download.default_directory": "/Users/gjimenezga/Desktop/RA/dataAutomation",
            "download.prompt_for_download": False,
            "directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        chrome_options.add_experimental_option("prefs", prefs)
        self.driver = webdriver.Chrome(options=chrome_options)
        self.options = options
        
    def run(self):
        try:
            # Navigate to the website
            self.driver.get("https://txresearchportal.com/selections")
            print("Navigation to https://txresearchportal.com/selections successful.")
            
            # Call the district function
            self.select_district(self.options['district'])

            # Call the program function
            self.select_program(self.options['program'])
            
            # Call the report function
            self.select_report(self.options['report'])

            # Call the administration function
            self.select_administrations(self.options['administrations'])

            # Standard Constructed Response Summary
            # if self.check_if_grade_section():
            #     self.select_grade(self.options['grades'])
            #     self.select_version(self.options['version'])
            # else:
                # group summary, standard comined summary: subject - grade
            # self.select_subject(self.options['subjects'])
            # self.select_grade(self.options['grades'])
            self.select_subject(options['subjects'])
            self.select_cluster((options['clusters']))    
            self.download()
            # else:
                # standard summary: subject - version - grade

            '''
            STAAR 3-8 - Report:
                        Standard Constructed Response Summary: admin - grade - version
                        group summary, standard combined summary: admin - subject - grade
                        standard summary: admin - subject - version - grade
                        item analysis summary: admin - grade - subject - version
                        score codes summary: - admin - grade - subject
            
            STAAR 3-8 - Alternate 2 3-8 - Report: Group Summary: Performance Levels, Score Codes, Standard Summary - Admin - grade - subject

            STAAR Alternate 2 EOC - Report: Group Summary: Performance Levels, Score Codes Summary, Standard Summary - Admin - Subject

            STAAR Cumulative - Report: Standard Cummulative Summary - Admin - Grade - Subject

            STAAR EOC - Report:
                        Group Summary, Standard Combined Summary, item analysis summary, score codes summary - admin - subject
                        standard constructed response summary, standard summary - subject - version

            TELPAS - Report:
                     Cluster summary - admin - subject - cluster
                     standard summary for grade, group summary: performance levels - admin - grade
                     score codes summary - admin - grade - subject  
                     standard summary for cluster - admin - cluster

            TELPAS Alternate - Report:
                            Group Summary: Performance Levels - admin - subject - grade
                            Score codes summary, standard summary - admin - grade




            '''

        finally:
            # Close the browser
            time.sleep(5)
            self.driver.quit()

    def select_district(self, district):
        # Search and select district
        search_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Enter a Campus or District Name or CDC code']"))
        )
        search_input.send_keys(district)
        search_input.send_keys(Keys.RETURN)
        
        # Find the first checkbox
        checkbox_selector = "span.MuiButtonBase-root.MuiCheckbox-root[aria-label^='Select district']"
        first_checkbox = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, checkbox_selector))
        )

        # Scroll the checkbox into view
        self.driver.execute_script("arguments[0].scrollIntoView(true);", first_checkbox)
        time.sleep(1)  # Wait for the scroll to complete

        # Click the checkbox
        first_checkbox.click()
        print(f"{district} clicked successfully.")

    def select_program(self, program):
        try:
            # Find the 'Select the Program' section 
            program_section = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//h4[contains(text(), 'Select the Program')]"))
            )
            
            # Scroll the 'Select the Program' section into view
            self.driver.execute_script("arguments[0].scrollIntoView(true);", program_section)
            time.sleep(1)  # Wait for the scroll to complete

            # Select programs' main grid
            main_container = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.MuiGrid-root.MuiGrid-container.MuiGrid-spacing-xs-3"))
            )

            radio_label = main_container.find_element(By.XPATH, f".//label[contains(@class, 'MuiFormControlLabel-root') and contains(., '{program}')]")
            radio_input = radio_label.find_element(By.CSS_SELECTOR, "input[type='radio']")
            self.driver.execute_script("arguments[0].click();", radio_input)
            print(f"Selected program: {program} successfully")
        except Exception as e:
            print(f"Error selecting program: {e}")

    def select_report(self, report):
        try:
            # Wait for the report container to be present
            report_container = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.MuiContainer-root.MuiContainer-maxWidthLg"))
            )

            # Scroll the container into view
            self.driver.execute_script("arguments[0].scrollIntoView(true);", report_container)
            time.sleep(2)  # Wait for any animations to complete

            try:
                # Method 1: Using XPath
                radio_label = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, f"//label[contains(@class, 'MuiFormControlLabel-root') and contains(., '{report}')]"))
                )
            except:
                print("XPath method failed, trying CSS selector")
                # Method 2: Using CSS selector
                radio_label = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, f"label.MuiFormControlLabel-root:contains('{report}')"))
                )

            # Click the label
            self.driver.execute_script("arguments[0].click();", radio_label)
            print(f"Selected report: {report} successfully")

        except Exception as e:
            print(f"Error selecting report '{report}': {str(e)}")

    def select_administrations(self, administrations):
        try:
            # Find the 'Select the Administrations' section
            administrations_section = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//h4[contains(text(), 'Select the Administration')]"))
            )
            
            # Scroll the 'Select the Administrations' section into view
            self.driver.execute_script("arguments[0].scrollIntoView(true);", administrations_section)
            time.sleep(2)  # Wait for the scroll to complete and any dynamic content to load

            # Select administrations' main container
            administrations_container = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.MuiContainer-root.MuiContainer-maxWidthLg"))
            )

            for administration in administrations:
                try:
                    # Wait for the specific administration option to be clickable
                    admin_option = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, f"//label[contains(@class, 'MuiFormControlLabel-root') and contains(., '{administration}')]"))
                    )
                    
                    # Check if it's a checkbox or radio button
                    input_element = admin_option.find_element(By.CSS_SELECTOR, "input")
                    input_type = input_element.get_attribute("type")
                    
                    if input_type == "checkbox":
                        # For checkboxes, only click if not already checked
                        if not input_element.is_selected():
                            admin_option.click()
                    elif input_type == "radio":
                        # For radio buttons, always click to ensure selection
                        admin_option.click()
                    else:
                        print(f"Unexpected input type for {administration}: {input_type}")
                        continue

                    print(f"Selected administration: {administration} successfully")
                    time.sleep(1)  # Wait for any potential updates after selection
                    
                except Exception as e:
                    print(f"Error selecting {administration}")
                    
        except Exception as e:
            print(f"Error in select_administrations: {str(e)}")

    def select_grade(self, grades):
        try:
            # Find the 'Select the Grades' section
            grade_section = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//h4[contains(text(), 'Select the Administration')]"))
            )

            # Scroll the 'Select the Grades' section into view
            self.driver.execute_script("arguments[0].scrollIntoView(true);", grade_section)
            time.sleep(2)  # Wait for the scroll to complete and any dynamic content to load

            # Select Grades' main container
            grades_container = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.MuiContainer-root.MuiContainer-maxWidthLg"))
            )

            for grade in grades:
                try:
                    # Wait for the specific grade option to be clickable
                    admin_option = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, f"//label[contains(@class, 'MuiFormControlLabel-root') and contains(., '{grade}')]"))
                    )
                    
                    # Check if it's a checkbox or radio button
                    input_element = admin_option.find_element(By.CSS_SELECTOR, "input")
                    input_type = input_element.get_attribute("type")
                    
                    if input_type == "checkbox":
                        # For checkboxes, only click if not already checked
                        if not input_element.is_selected():
                            admin_option.click()
                    elif input_type == "radio":
                        # For radio buttons, always click to ensure selection
                        admin_option.click()
                    else:
                        print(f"Unexpected input type for {grade}: {input_type}")
                        continue

                    print(f"Selected administration: {grade} successfully")
                    time.sleep(1)  # Wait for any potential updates after selection
                    
                except Exception as e:
                    print(f"Error selecting {grade}")
                    
        except Exception as e:
            print(f"Error in select_administrations: {str(e)}")

    # DOES NOT WORK WITH 'STAAR'
    def select_version(self, version):
        try:
            # Find the 'Select the Administrations' section
            version_section = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//h4[contains(text(), 'Select a Version')]"))
            )

            # Scroll the 'Select the Version' section into view
            self.driver.execute_script("arguments[0].scrollIntoView(true);", version_section)
            time.sleep(2)  # Wait for the scroll to complete and any dynamic content to load

            # Select versions' main container
            version_container = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.MuiContainer-root.MuiContainer-maxWidthLg"))
            )

            try:
                # Wait for the specific version option to be clickable
                version_option = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, f"//label[contains(@class, 'MuiFormControlLabel-root') and contains(., '{version}')]"))
                )
                
                # Click option
                version_option.click()

                print(f"Selected {version} successfully")
                time.sleep(1)  # Wait for any potential updates after selection
                
            except Exception as e:
                print(f"Error selecting {version}: {str(e)}")
                    
        except Exception as e:
            print(f"Error in select_version: {str(e)}")

    def select_subject(self, subjects):
        try:
            # Find the 'Select the Grades' section
            subject_section = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//h4[contains(text(), 'Select a Subject')]"))
            )

            # Scroll the 'Select the Grades' section into view
            self.driver.execute_script("arguments[0].scrollIntoView(true);", subject_section)
            time.sleep(2)  # Wait for the scroll to complete and any dynamic content to load

            # Select Grades' main container
            subject_cointainer = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.MuiContainer-root.MuiContainer-maxWidthLg"))
            )

            for subject in subjects:
                try:
                    # Wait for the specific grade option to be clickable
                    admin_option = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, f"//label[contains(@class, 'MuiFormControlLabel-root') and contains(., '{subject}')]"))
                    )
                    
                    # Check if it's a checkbox or radio button
                    input_element = admin_option.find_element(By.CSS_SELECTOR, "input")
                    input_type = input_element.get_attribute("type")
                    
                    if input_type == "checkbox":
                        # For checkboxes, only click if not already checked
                        if not input_element.is_selected():
                            admin_option.click()
                    elif input_type == "radio":
                        # For radio buttons, always click to ensure selection
                        admin_option.click()
                    else:
                        print(f"Unexpected input type for {subject}: {input_type}")
                        continue

                    print(f"Selected subject: {subject} successfully")
                    time.sleep(1)  # Wait for any potential updates after selection
                    
                except Exception as e:
                    print(f"Error selecting {subject}")
                    
        except Exception as e:
            print(f"Error in select_administrations: {str(e)}")


    def select_cluster(self, clusters):
        try:
            # Find the 'Select the Cluster' section
            cluster_section = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//h4[contains(text(), 'Select a Subject')]"))
            )

            # Scroll the 'Select the Cluster' section into view
            self.driver.execute_script("arguments[0].scrollIntoView(true);", cluster_section)
            time.sleep(2)  # Wait for the scroll to complete and any dynamic content to load

            # Select Grades' main container
            subject_cointainer = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.MuiContainer-root.MuiContainer-maxWidthLg"))
            )

            for cluster in clusters:
                try:
                    # Wait for the specific Cluster option to be clickable
                    admin_option = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, f"//label[contains(@class, 'MuiFormControlLabel-root') and contains(., '{cluster}')]"))
                    )
                    
                    # Check if it's a checkbox or radio button
                    input_element = admin_option.find_element(By.CSS_SELECTOR, "input")
                    input_type = input_element.get_attribute("type")
                    
                    if input_type == "checkbox":
                        # For checkboxes, only click if not already checked
                        if not input_element.is_selected():
                            admin_option.click()
                    elif input_type == "radio":
                        # For radio buttons, always click to ensure selection
                        admin_option.click()
                    else:
                        print(f"Unexpected input type for {cluster}: {input_type}")
                        continue

                    print(f"Selected cluster: {cluster} successfully")
                    time.sleep(1)  # Wait for any potential updates after selection
                    
                except Exception as e:
                    print(f"Error selecting {cluster}")
                    
        except Exception as e:
            print(f"Error in select_clusters: {str(e)}")

    def download(self):
        try:
            # Find the download button (use the class name from your example)
            download_button = self.driver.find_element(By.CLASS_NAME, "MuiRequestButton-root")

            # Click the download button
            download_button.click()
            print('File downloaded succesfully')

        except Exception as e:
            print(f"Error downloading file: {e}")

# Usage
options = {
    'district': 'Austin ISD',
    'program': 'TELPAS',
    'report': 'Cluster Summary',
    'administrations': ['March 2024'],
    'subjects': ['Listening'],
    'grades': ['Grade 3'],
    'version': 'STAAR Spanish',
    'clusters': ['Grade K-2']
}

script = Script(options)
script.run()
