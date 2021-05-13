from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
import time, csv, pandas as pd

try:
    #UPDATE REQUIRED
    driver = webdriver.Chrome('ENTER PATH FOR CHROME WEBDRIVER')
    driver.get('https://www.indeed.com/')
    wait = WebDriverWait(driver, 10)
    element = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@class='gnav-LoggedOutAccountLink']")))
    driver.find_element_by_class_name('gnav-LoggedOutAccountLink').find_element_by_class_name('gnav-LoggedOutAccountLink-signIn').click()

    #UPDATE REQUIRED
    driver.find_element_by_id('login-email-input').send_keys('ENTER YOUR USERNAME')
    driver.find_element_by_id('login-password-input').send_keys('ENTER YOUR PASSWORD')

    driver.find_element_by_id('login-submit-button').click()
    element = wait.until(EC.presence_of_element_located((By.ID, "text-input-what")))

    #UPDATE REQUIRED
    driver.find_element_by_id('text-input-what').send_keys('ENTER REQUIRED JOB FUNCTION')
    driver.find_element_by_id('text-input-where').send_keys(Keys.CONTROL + "a")
    driver.find_element_by_id('text-input-where').send_keys(Keys.DELETE)
	
    #UPDATE REQUIRED
    driver.find_element_by_id('text-input-where').send_keys("ENTER LOCATION")
    driver.find_element_by_class_name('icl-WhatWhere-buttonWrapper').find_element_by_class_name('icl-WhatWhere-button').click()
    element = wait.until(EC.presence_of_element_located((By.ID, "pageContent")))

    links = []
    for _ in range(7):
        try:
            page_table = driver.find_element_by_id('pageContent')
            page_rows = page_table.find_element_by_id('resultsCol')
            for divs in page_rows.find_elements_by_class_name('jobsearch-SerpJobCard'):
                links.append(divs.find_element_by_tag_name('a').get_attribute('href'))
            driver.find_element_by_class_name('pagination-list').find_element(By.CSS_SELECTOR, '[aria-label="Next"]').click()
        except Exception as e:
            print(e)
            continue

    #UPDATE REQUIRED
    previous = pd.read_csv('ENTER PATH AND FILENAME TO SAVE GATHERED JD')
    checker = previous['Links'].iloc[:].value_counts().index
    final_links = [i for i in links if i not in checker]

    if final_links:
        wrt_links = pd.DataFrame(final_links, columns = ['Links'])
        wrt_links['Status'] = 'Written'
        #UPDATE REQUIRED
        wrt_links.to_csv('ENTER PREVIOUSLY ENTERED PATH AND FILENAME', mode = 'a')

    #UPDATE REQUIRED
    previous = pd.read_csv('ENTER PREVIOUSLY ENTERED PATH AND FILENAME')
    checker = previous['Links'][previous['Status'].iloc[:]=='Check & Apply']
    #UPDATE REQUIRED
	'''ENTER ALL THE NECESSARY DETAILS:
    FLAG_WORDS - WORDS THAT ARE CLEARLY A NO-NO FOR YOU
    CHECK_WORDS - TECHNOLOGY/FIELD/SECTOR OF INTEREST
    '''
    flag_words = ['Sponsorship', 'Citizen', 'US', 'U.S.']
    check_words = ['Tableau', 'SQL', 'ETL', 'Analytics']
    for num, link in checker.items():
        try:
            driver.get(link)
            element = wait.until(EC.presence_of_element_located((By.XPATH,"html/body")))
            time.sleep(5)
            description = driver.find_element_by_class_name('jobsearch-JobComponent-description')
            threshold = [i for i in flag_words if i in description.text]
            #UPDATE REQUIRED
            '''
            UPDATE THE THRESHOLD PERCENTAGE OR VALUE (0.25 and 0.5 RESPECTIVELY) BASED ON YOUR NEED
            '''
            if len(threshold)/len(flag_words) < 0.25:
            # If Block Start for Description Check
                check_thresh = [i for i in check_words if i in description.text]
                if len(check_thresh)/len(check_words) > 0.5:
                    try:
                        if driver.find_element_by_class_name('jobsearch-IndeedApplyButton-buttonWrapper').find_element_by_tag_name('button').text:
                            previous.loc[previous['Links'] == link, 'Status'] = 'Check & Apply'
                    except:
                        try:
                            if driver.find_element_by_id('applyButtonLinkContainer').find_element_by_tag_name('a').text:
                                previous.loc[previous['Links'] == link, 'Status'] = 'Apply on company website'
                        except Exception as e:
                            print(link, e)
                            pass
                else:
                    # print('Description did not cross the threshold for the checks')
                    previous.loc[previous['Links'] == link, 'Status'] = 'Check Technology'
                    continue
            # If block ends for Description Check
            else:
                previous.loc[previous['Links'] == link, 'Status'] = 'Authorization Required'
                continue
        except Exception as e:
            print(e)
            time.sleep(2)
            continue
finally:
    previous.drop('Unnamed: 0', axis=1)
    #UPDATE REQUIRED
    previous.to_csv('ENTER PREVIOUSLY ENTERED PATH AND FILENAME')
    time.sleep(20)
    driver.close()
