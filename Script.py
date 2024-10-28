import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
import time
import threading
from queue import Queue
import time
from typing import Dict, List

class DownloadWorker(threading.Thread):
    def __init__(self, task_queue: Queue, download_dir: str):
        """
        Initialize a worker thread for downloading reports.
        
        Args:
            task_queue (Queue): Queue containing download tasks
            download_dir (str): Base directory for downloads
        """
        threading.Thread.__init__(self)
        self.task_queue = task_queue
        self.download_dir = download_dir

    def run(self):
        while True:
            try:
                # Get task from queue
                options = self.task_queue.get()
                if options is None:  # Poison pill to stop thread
                    break
                    
                # # Create thread-specific download directory
                # thread_dir = os.path.join(
                #     self.download_dir, 
                #     f"thread_{threading.current_thread().name}"
                # )
                # os.makedirs(thread_dir, exist_ok=True)
                # options['download_dir'] = thread_dir
                
                # Create new Script instance and run
                script = Script(options)
                try:
                    script.run()
                finally:
                    script.driver.quit()
                    
            except Exception as e:
                print(f"Error in worker thread {self.name}: {e}")
            finally:
                self.task_queue.task_done()

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
            "download.default_directory": os.path.join(os.getcwd(), 'downloads'), # Directory for downloaded files
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

            # Apply filters
            self.apply_filters()

            # Trigger the download process
            self.download(self.options['district'], self.options['administration'])

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
        Selects the specified district by calling the helper _search function.
        Args:
            district (list[str]): The names of the districts to select.
        """
        try:
            search_again = False
            for dis in district:
                try:
                    print(f"\nProcessing district: {dis}")
                    
                    # If not the first district, click the new search button
                    if search_again:
                        print("Clicking new search button to return to search page...")
                        new_search_button = WebDriverWait(self.driver, 10).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, 
                                "div.MuiGrid-container button.MuiLink-button[aria-label='Search Again']"))
                        )
                        
                        # Scroll parent div into view first
                        parent_div = self.driver.find_element(By.CSS_SELECTOR, "div.MuiGrid-container")
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", parent_div)
                        time.sleep(1)
                        new_search_button.click()
                        time.sleep(2)  # Wait for page to load
                    
                    # Search for and select the current district
                    self._search(dis)
                    search_again = True
                    
                except Exception as e:
                    print(f"Error processing district '{dis}': {str(e)}")
                    # Continue with next district even if current one fails
                    continue
            
            print("All districts processed successfully.")

        except Exception as e:
            print(f"An unexpected error occurred while processing districts: {str(e)}")
            print("Last known action: " + self.driver.current_url)

        print("District selection completed.")

    def _search(self, dis):
        """
        Selects the specified district by typing the name, clicking search, and selecting the first checkbox in the results table.
        Args:
            dis (str): The name of the district
        """
        # Locate and clear the search input
        print("Locating search input...")
        search_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Enter a Campus or District Name or CDC code']"))
        )
        search_input.clear()
        print("Search input cleared.")
        
        # Type the district name
        search_input.send_keys(dis)
        print(f"Typed district name: {dis}")
        time.sleep(1)  # Short pause after typing
        
        # Click the search button
        print("Locating search button...")
        search_button_selector = ("button.MuiButtonBase-root.MuiButton-root.MuiButton-contained.MuiButton-containedInherit."
                                "MuiButton-sizeMedium.MuiButton-containedSizeMedium.MuiButton-colorInherit[type='submit']")
        search_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, search_button_selector))
        )
        print("Search button found. Attempting to click...")
        search_button.click()
        print("Search button clicked.")
        
        # Wait for the results table to appear
        print("Waiting for results table...")
        table_selector = "div.MuiTableContainer-root.selections-table.selections-div"
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, table_selector))
        )
        print("Results table found.")
        
        # Find the first checkbox within the results table
        print("Locating first checkbox in results...")
        checkbox_selector = f"{table_selector} input.PrivateSwitchBase-input[type='checkbox']"
        checkbox = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, checkbox_selector))
        )
        print("First checkbox found. Scrolling into view...")
        
        # Scroll the checkbox into view
        self.driver.execute_script("arguments[0].scrollIntoView(true);", checkbox)
        time.sleep(1)  # Wait for the scroll to complete
        
        # Click the checkbox
        print("Attempting to click checkbox...")
        checkbox.click()
        print(f"First checkbox for '{dis}' search clicked successfully.")

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

    def apply_filters(self):
        """
        Applies filters for the selected report.
        """
        try:
            # Find the View Selections button using the ID
            view_selections = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "selectionsSubmitButton"))
            )
            view_selections.click()

            # Wait and click the Breakdown button
            breakdown_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Breakdown')]"))
            )
            breakdown_button.click()

            # Wait for dialog to be visible and find checkboxes by their label text
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Breakdown by Demographic')]"))
            )

            # Find and click Ethnicity checkbox
            ethnicity_checkbox = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//label[normalize-space()='Ethnicity']/input[@type='checkbox'] | //label[normalize-space()='Ethnicity']"))
            )
            if not ethnicity_checkbox.is_selected():
                ethnicity_checkbox.click()

            # Find and click Economically Disadvantaged checkbox
            econ_checkbox = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//label[normalize-space()='Economically Disadvantaged']/input[@type='checkbox'] | //label[normalize-space()='Economically Disadvantaged']"))
            )
            if not econ_checkbox.is_selected():
                econ_checkbox.click()

            # Click the Apply button
            apply_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[text()='Apply']"))
            )
            apply_button.click()

        except Exception as e:
            print(f"Error applying filters: {e}")

    def download(self, name, admin):
        """
        Initiates the download of the selected report.
        """
        try:
            # Click Download button
            download_button = WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located((By.XPATH, "//button[contains(text(), 'Download')]"))
            )
            download_button.click()
            time.sleep(2)  # Wait for modal

            # Rename file
            input_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 
                    "input.MuiInputBase-input.MuiOutlinedInput-input.MuiInputBase-inputSizeSmall"))
            )
            input_field.send_keys(Keys.CONTROL + "a")
            input_field.send_keys(Keys.DELETE)
            date = ', '.join(admin)
            input_field.send_keys(f'{name}_{date}')

            # Click dropdown and select CSV
            dropdown = self.driver.find_element(By.CSS_SELECTOR, "div[role='button'][aria-haspopup='listbox']")
            dropdown.click()
            time.sleep(1)
            
            csv_option = self.driver.find_element(By.CSS_SELECTOR, "li[data-value='csv']")
            csv_option.click()
            time.sleep(1)

            # Click final download button
            download_button = self.driver.find_element(By.XPATH, "//button[text()='DOWNLOAD']")
            download_button.click()
            time.sleep(3)

            print('File downloaded successfully')
        except Exception as e:
            print(f"Error downloading file: {e}")

def run_queries(queries: List[Dict], num_threads: int = 3):
        
        """
        Download multiple reports concurrently.
        
        Args:
            queries (List[Dict]): List of queries to process
            num_threads (int): Number of concurrent download threads
        """
        # Create base download directory
        base_download_dir = os.path.join(os.getcwd(), 'downloads')
        os.makedirs(base_download_dir, exist_ok=True)
        
        # Create task queue
        task_queue = Queue()
        
        # Create and start worker threads
        workers = []
        for i in range(min(num_threads, len(queries))):
            worker = DownloadWorker(task_queue, base_download_dir)
            worker.daemon = True
            worker.start()
            workers.append(worker)
        
        # Add all queries to the task queue
        for query in queries:
            task_queue.put(query)
        
        # Add poison pills to stop workers
        for _ in range(len(workers)):
            task_queue.put(None)
        
        # Wait for all tasks to complete
        task_queue.join()
        
        # Wait for all threads to finish
        for worker in workers:
            worker.join()

import csv
def load_queries():
    """
    Function that reads an input csv file and loads a querie.

    Returns:
        List[dict]: A list of dictionaries containing query data.
    """

    with open('my3.csv', mode='r') as file:
        queries = []

        csv_reader = csv.reader(file)

        # Get the header row
        header = next(csv_reader)

        # Loop through the rows
        for row in csv_reader:
            district = row[0].split(';') if row[0] else []
            if not district:
                continue
            program = row[1]
            report = row[2]
        
            # Convert semicolon-separated strings into lists
            administration = row[3].split(';') if row[3] else []
            subject = row[4].split(';') if row[4] else []
            grade = row[5].split(';') if row[5] else []
            version = row[6] if row[6] else ''
            cluster = row[7].split(';') if row[7] else []
            
            # Create the dictionary
            query = {
                'district': district,
                'program': program,
                'report': report,
                'administration': administration,
                'subject': subject,
                'grade': grade,
                'version': version,
                'cluster': cluster
            }

            # Append the query
            queries.append(query)
            print(f'Query {len(queries)} loaded: {query}')

        return queries

from Processing import processing

if __name__ == "__main__":
    queries = load_queries()
    run_queries(queries, 1)
    # DATA CLEANING STARTING...
    processing()