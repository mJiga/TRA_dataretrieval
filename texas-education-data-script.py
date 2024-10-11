import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

import time

class Script:
    def __init__(self, options):
        """
        Initializes the Script class with options for Selenium WebDriver.

        Args:
            options (dict): A dictionary containing configuration options such as download directory, district, program, and report.
        """
        self.options = options

        # Set up Chrome options for WebDriver
        chrome_options = webdriver.ChromeOptions()
        prefs = {
            "download.default_directory": self.options['download_dir'], # Directory for downloaded files
            "download.prompt_for_download": False, # Do not prompt for downloads
            "directory_upgrade": True, # Allow directory upgrades
            "safebrowsing.enabled": True # Enable safe browsing
        }
        chrome_options.add_experimental_option("prefs", prefs)
        self.driver = webdriver.Chrome(options=chrome_options)

        # Map of programs to their corresponding reports and required parameters
        self.program_report_map = {
            "STAAR 3-8": {
                "Standard Constructed Response Summary": ['administration', 'grade', 'version'],
                "Standard Combined Summary": ['administration', 'subject', 'grade'],
                "Group Summary: Performance Levels & Reporting Categories": ['administration', 'subject', 'grade'],
                "Standard Summary": ['administration', 'subject', 'version', 'grade'],
                "Item Analysis Summary": ['administration', 'grade', 'subject', 'version'],
                "Score Codes Summary": ['administration', 'grade', 'subject']
            },
            "STAAR 3-8 Alternate 2 3-8": {
                'Group Summary': ['administration', 'grade', 'subject'],
                'Score Codes Summary': ['administration', 'grade', 'subject'],
                'Standard Summary': ['administration', 'grade', 'subject'],
            },
            'STAAR Alternate 2 EOC': {
                'Group Summary: Performance Levels': ['administration', 'subject'],
                'Score Codes Summary':['administration', 'subject'],
                'Standard Summary':['administration', 'subject']
            },
            'STAAR Cumulative': {
                'Standard Cummulative Summary': ['administration', 'grade', 'subject']
            },
            'STAAR EOC': {
                'Group Summary: Performance Levels & Reporting Categories': ['administration', 'subject'],
                'Standard Combined Summary': ['administration', 'subject'],
                'Item Analysis Summary': ['administration', 'subject'],
                'Score Codes Summary': ['administration', 'subject'],
                'Standard Constructed Response Summary': ['administration', 'subject', 'version'],
                'Standard Summary': ['administration', 'subject', 'version']
            },
            'TELPAS': {
                'Cluster Summary': ['administration', 'subject', 'cluster'],
                'Standard Summary For Grade': ['administration', 'grade'],
                'Group Summary: Performance Levels': ['administration', 'subject', 'grade'],
                'Score Codes Summary': ['administration', 'grade', 'subject'],
                'Standard Summary For Cluster': ['administration', 'cluster']
            },
            'TELPAS Alternate': {
                'Group Summary: Performance Levels': ['administration', 'subject', 'grade'],
                'Score Codes Summary': ['administration', 'grade'],
                'Standard Summary': ['administration', 'grade']
            }
        }

    def run(self):
        
        """
        Executes the main script logic for downloading reports.

        This includes navigating to the website, selecting district, program, and report,
        handling dynamic parameters, and initiating the download.
        """
        try:
            # Navigate to the website
            self.driver.get("https://txresearchportal.com/selections")
            print("Navigation to https://txresearchportal.com/selections successful.")

            # Dynamically select based on user-provided options
            self.select_district(self.options['district'])
            self.select_program(self.options['program'])
            
            # Dynamically select report based on options
            self.select_report(self.options['report'])
            
            # Dynamically handle parameters based on the selected report
            self.handle_dynamic_parameters(self.options['report'], self.options['program'], self.options)

            # Trigger the download process
            self.download()

        finally:
            # Ensure the browser is closed after the operation
            time.sleep(5)  # Wait for the download to complete
            self.driver.quit()

    def handle_dynamic_parameters(self, report, program, options):
        """
        Handles the dynamic selection of parameters based on the selected report and program.

        Args:
            report (str): The selected report.
            program (str): The selected program.
            options (dict): The options containing parameter values.
        """
        if program in self.program_report_map and report in self.program_report_map[program]:
            required_params = self.program_report_map[program][report]

            # Iterate through required parameters and invoke respective selection methods
            for param in required_params:

                if param in options:
                    method = getattr(self, f"select_{param}", None) # Call the selection method with the option value

                    if method:
                        method(options[param])
                    else:
                        print(f"Selection method for {param} not defined.")
                else:
                    print(f"Parameter {param} not provided for {program}.")

    def select_district(self, district):
        """
        Selects the specified district from the input field and clicks the checkbox.

        Args:
            district (str): The name of the district to select.
        """

        # Locate the district search input and enter the district name
        search_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Enter a Campus or District Name or CDC code']"))
        )

        search_input.send_keys(district)
        search_input.send_keys(Keys.RETURN)
        
        # Find and click the first checkbox corresponding to the district
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
        """
        Selects the specified report from the available options.

        Args:
            report (str): The name of the report to select.
        """
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

    def select_administration(self, administrations):
        """
        Selects the specified administration from the options.

        Args:
            administration (str): The administration value to select.
        """
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
                            time.sleep(1)
                    elif input_type == "radio":
                        # For radio buttons, always click to ensure selection
                        admin_option.click()
                        time.sleep(1)
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
        """
        Selects the specified grade from the options.

        Args:
            grade (str): The grade value to select.
        """
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
                            time.sleep(1)
                    elif input_type == "radio":
                        # For radio buttons, always click to ensure selection
                        admin_option.click()
                        time.sleep(1)
                    else:
                        print(f"Unexpected input type for {grade}: {input_type}")
                        continue

                    print(f"Selected administration: {grade} successfully")
                    time.sleep(1)  # Wait for any potential updates after selection
                    
                except Exception as e:
                    print(f"Error selecting {grade}")
                    
        except Exception as e:
            print(f"Error in select_administrations: {str(e)}")

    # DOES NOT WORK WITH 'STAAR' AS OF NOWS
    def select_version(self, version):
        """
        Selects the specified version from the options.

        Args:
            subject (str): The version value to select.
        """
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
        """
        Selects the specified subject from the options.

        Args:
            subject (str): The version subject to select.
        """
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
                            time.sleep(1)
                    elif input_type == "radio":
                        # For radio buttons, always click to ensure selection
                        admin_option.click()
                        time.sleep(1)
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
        """
        Selects the specified cluster from the options.

        Args:
            subject (str): The cluster value to select.
        """
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
                            time.sleep(1)
                    elif input_type == "radio":
                        # For radio buttons, always click to ensure selection
                        admin_option.click()
                        time.sleep(1)
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
        """
        Initiates the download of the selected report.
        """
        try:
            # Find the download button (use the class name from your example)
            download_button = self.driver.find_element(By.CLASS_NAME, "MuiRequestButton-root")

            # Click the download button
            download_button.click()
            time.sleep(3) 
            print('File downloaded succesfully')

        except Exception as e:
            print(f"Error downloading file: {e}")

if __name__ == "__main__":
    options = {
        'district': 'Austin ISD',
        'program': 'STAAR Alternate 2 EOC',
        'report': 'Standard Summary',
        'administration': ['Spring 2023', 'Spring 2015', 'Spring 2022', 'Spring 2016', 'Spring 2021', 'Spring 2017'],
        'subject': ['English I'],
        'grade': [],
        'version': '',
        'cluster': [],
        'download_dir': os.path.join(os.getcwd(), 'reports')
    }

script = Script(options)
script.run()