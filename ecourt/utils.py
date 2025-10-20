import time
import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime

class ECourtsScraper:
    def __init__(self, headless=True, verbose=False):
        self.base_url = "https://services.ecourts.gov.in/ecourtindia_v6/?p=cause_list/"
        self.driver = None
        self.headless = headless
        self.verbose = verbose
        
    def log(self, message):
        """Print message if verbose mode is enabled"""
        if self.verbose:
            print(f"[INFO] {message}")
        
    def setup_driver(self, download_path=None):
        """Setup Chrome driver with options"""
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        
        if download_path:
            prefs = {
                "download.default_directory": download_path,
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "plugins.always_open_pdf_externally": True
            }
            chrome_options.add_experimental_option("prefs", prefs)
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.log("Chrome driver initialized")
        
    def close_driver(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()
            self.log("Chrome driver closed")
            
    def get_states(self):
        """Fetch all available states"""
        try:
            self.setup_driver()
            self.log("Fetching states...")
            self.driver.get("https://services.ecourts.gov.in/ecourtindia_v6/?p=cause_list/")
            time.sleep(2)
            
            state_select = Select(WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "sess_state_code"))
            ))
            
            states = []
            for option in state_select.options:
                if option.get_attribute('value'):
                    states.append({
                        'value': option.get_attribute('value'),
                        'text': option.text
                    })
            
            self.log(f"Found {len(states)} states")
            return states
        except Exception as e:
            self.log(f"Error fetching states: {e}")
            return []
        finally:
            self.close_driver()
    
    def get_districts(self, state_code):
        """Fetch districts for a given state"""
        try:
            self.setup_driver()
            self.log(f"Fetching districts for state code: {state_code}")
            self.driver.get(self.base_url)
            time.sleep(2)
            
            state_select = Select(WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.ID, "sess_state_code"))
            ))
            state_select.select_by_value(state_code)
            time.sleep(2)
            
            district_select = Select(WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.ID, "sess_dist_code"))
            ))
            
            districts = []
            for option in district_select.options:
                if option.get_attribute('value'):
                    districts.append({
                        'value': option.get_attribute('value'),
                        'text': option.text
                    })
            
            self.log(f"Found {len(districts)} districts")
            return districts
        except Exception as e:
            self.log(f"Error fetching districts: {e}")
            return []
        finally:
            self.close_driver()
    
    def get_court_complexes(self, state_code, district_code):
        """Fetch court complexes for a given state and district"""
        try:
            self.setup_driver()
            self.log(f"Fetching court complexes...")
            self.driver.get(self.base_url)
            time.sleep(2)
            
            state_select = Select(WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.ID, "sess_state_code"))
            ))
            state_select.select_by_value(state_code)
            time.sleep(2)
            
            district_select = Select(WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.ID, "sess_dist_code"))
            ))
            district_select.select_by_value(district_code)
            time.sleep(2)
            
            complex_select = Select(WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.ID, "court_complex_code"))
            ))
            
            complexes = []
            for option in complex_select.options:
                if option.get_attribute('value'):
                    complexes.append({
                        'value': option.get_attribute('value'),
                        'text': option.text
                    })
            
            self.log(f"Found {len(complexes)} court complexes")
            return complexes
        except Exception as e:
            self.log(f"Error fetching court complexes: {e}")
            return []
        finally:
            self.close_driver()
    
    def get_courts(self, state_code, district_code, complex_code):
        """Fetch courts for a given state, district, and complex"""
        try:
            self.setup_driver()
            self.log(f"Fetching courts...")
            self.driver.get(self.base_url)
            time.sleep(2)
            
            state_select = Select(WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.ID, "sess_state_code"))
            ))
            state_select.select_by_value(state_code)
            time.sleep(2)
            
            district_select = Select(WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.ID, "sess_dist_code"))
            ))
            district_select.select_by_value(district_code)
            time.sleep(2)
            
            complex_select = Select(WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.ID, "court_complex_code"))
            ))
            complex_select.select_by_value(complex_code)
            time.sleep(2)
            
            court_select = Select(WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "court_code"))
            ))
            
            courts = []
            for option in court_select.options:
                if option.get_attribute('value'):
                    courts.append({
                        'value': option.get_attribute('value'),
                        'text': option.text
                    })
            
            self.log(f"Found {len(courts)} courts")
            return courts
        except Exception as e:
            self.log(f"Error fetching courts: {e}")
            return []
        finally:
            self.close_driver()
    
    def search_case(self, state_code, district_code, complex_code, 
                   cnr=None, case_type=None, case_number=None, case_year=None):
        """Search for a specific case and check if it's listed today or tomorrow"""
        try:
            self.setup_driver()
            self.log(f"Searching for case...")
            self.driver.get(self.base_url)
            time.sleep(2)
            
            # Select state, district, complex
            state_select = Select(WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.ID, "sess_state_code"))
            ))
            state_select.select_by_value(state_code)
            time.sleep(2)
            
            district_select = Select(WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.ID, "sess_dist_code"))
            ))
            district_select.select_by_value(district_code)
            time.sleep(2)
            
            complex_select = Select(WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.ID, "court_complex_code"))
            ))
            complex_select.select_by_value(complex_code)
            time.sleep(2)
            
            # Search by CNR or Case details
            if cnr:
                cnr_input = self.driver.find_element(By.ID, "cnr_number")
                cnr_input.send_keys(cnr)
            else:
                if case_type:
                    case_type_select = Select(self.driver.find_element(By.ID, "case_type"))
                    case_type_select.select_by_visible_text(case_type)
                if case_number:
                    case_no_input = self.driver.find_element(By.ID, "case_no")
                    case_no_input.send_keys(case_number)
                if case_year:
                    case_year_input = self.driver.find_element(By.ID, "case_year")
                    case_year_input.send_keys(case_year)
            
            # Submit search
            submit_btn = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            submit_btn.click()
            time.sleep(3)
            
            # Extract case information
            try:
                case_info = {
                    'found': True,
                    'serial_number': None,
                    'court_name': None,
                    'date': None,
                    'listed_today': False,
                    'listed_tomorrow': False
                }
                
                # Try to find case details in the results table
                results_table = self.driver.find_element(By.CLASS_NAME, "case-status-table")
                rows = results_table.find_elements(By.TAG_NAME, "tr")
                
                for row in rows[1:]:  # Skip header
                    cols = row.find_elements(By.TAG_NAME, "td")
                    if len(cols) >= 3:
                        case_info['serial_number'] = cols[0].text
                        case_info['court_name'] = cols[1].text
                        case_info['date'] = cols[2].text
                        
                        # Check if listed today or tomorrow
                        from datetime import datetime, timedelta
                        today = datetime.now().strftime("%d-%m-%Y")
                        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%d-%m-%Y")
                        
                        if today in cols[2].text:
                            case_info['listed_today'] = True
                        if tomorrow in cols[2].text:
                            case_info['listed_tomorrow'] = True
                        break
                
                return case_info
            except:
                return {'found': False, 'message': 'Case not found in cause list'}
                
        except Exception as e:
            self.log(f"Error searching case: {e}")
            return {'found': False, 'error': str(e)}
        finally:
            self.close_driver()
    
    def download_cause_list(self, state_code, district_code, complex_code, 
                          court_code, date_str, download_path):
        """Download cause list PDF for specified parameters"""
        try:
            self.setup_driver(download_path)
            self.log(f"Downloading cause list for date: {date_str}")
            self.driver.get(self.base_url)
            time.sleep(2)
            
            state_select = Select(WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "sess_state_code"))
            ))
            state_select.select_by_value(state_code)
            time.sleep(2)
            
            district_select = Select(WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "sess_dist_code"))
            ))
            district_select.select_by_value(district_code)
            time.sleep(2)
            
            complex_select = Select(WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "court_complex_code"))
            ))
            complex_select.select_by_value(complex_code)
            time.sleep(2)
            
            court_select = Select(WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "court_code"))
            ))
            court_select.select_by_value(court_code)
            time.sleep(2)
            
            date_input = self.driver.find_element(By.ID, "date_from")
            date_input.clear()
            date_input.send_keys(date_str)
            time.sleep(1)
            
            submit_btn = self.driver.find_element(By.XPATH, "//button[@type='submit' or contains(text(), 'Go')]")
            submit_btn.click()
            time.sleep(5)
            
            try:
                pdf_link = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '.pdf') or contains(text(), 'View') or contains(text(), 'Download')]"))
                )
                pdf_link.click()
                time.sleep(5)
                
                self.log("Cause list downloaded successfully")
                return True, "Cause list downloaded successfully"
            except:
                self.log("No cause list found for the specified date")
                return False, "No cause list found for the specified date"
                
        except Exception as e:
            self.log(f"Error downloading cause list: {str(e)}")
            return False, f"Error downloading cause list: {str(e)}"
        finally:
            self.close_driver()
    
    def download_all_courts_cause_list(self, state_code, district_code, 
                                      complex_code, date_str, download_path):
        """Download cause lists for all courts in a complex"""
        results = []
        courts = self.get_courts(state_code, district_code, complex_code)
        
        self.log(f"Downloading cause lists for {len(courts)} courts...")
        
        for i, court in enumerate(courts, 1):
            court_code = court['value']
            court_name = court['text']
            
            self.log(f"[{i}/{len(courts)}] Processing: {court_name}")
            
            success, message = self.download_cause_list(
                state_code, district_code, complex_code, 
                court_code, date_str, download_path
            )
            
            results.append({
                'court_code': court_code,
                'court_name': court_name,
                'success': success,
                'message': message
            })
            
            time.sleep(2)
        
        return results