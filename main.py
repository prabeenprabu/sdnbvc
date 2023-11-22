from flask import render_template, Flask, request, redirect, session, url_for
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.service import Service
# from selenium.webdriver.chrome.options import Options as ChromeOption
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchWindowException

# from webdriver_manager.chrome import ChromeDriverManager
import os

app = Flask(__name__)
app.secret_key = os.urandom(32)


@app.route('/')
@app.route('/home')
@app.route('/index')
def index():
    return render_template("index.html")

@app.route('/check',methods = ["GET","POST"])
def check():
    if request.method == "POST":
        pattern = "^\d{13}$"
        
        #variables we need to store values
        name = ""
        course = ""
        regNo = request.form["regNo"]
        subs = []
        marks = []
        results = []
        grades = []
        
        if re.search(pattern, regNo):
            url = 'http://www.sdnbvc.com/sdnbvc/website2015/htmls/semapr23.aspx'
            

            #customizing the chrome browser
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            # driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=chrome_options)
            driver = webdriver.Chrome(options=chrome_options)
            # -------wait for the webpage load---
            driver.get(url)
            webpage = WebDriverWait(driver, 10)
            
            #getting text box and paste the register number and then load the page
            tb = webpage.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#txtExamno')))
            tb.send_keys(regNo)
            btn = webpage.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#btnsubmit')))
            btn.click()
            
            #wait for the result table
            table = ""
            try:
                table = webpage.until(EC.presence_of_element_located((By.XPATH, '//*[@id="Label1"]/table/tbody')))
            except TimeoutException:      
                driver.quit()          
                return redirect(url_for('index'))
            except NoSuchWindowException:
                driver.quit()          
                return redirect(url_for('index'))
            
            tr = table.find_elements(By.TAG_NAME, 'tr')
                        
            name = ((table.find_element(
                        By.XPATH, '//*[@id="Label1"]/table/tbody/tr[3]/td')).text).split(":")[1]
            course = ((table.find_element(
                        By.XPATH, '//*[@id="Label1"]/table/tbody/tr[4]/td')).text).split(":")[1]
            
            
            #getting subjects, marks, grade & results from the table
            i = 0
            for n in tr:
                if (i >= 5):
                    mark = table.find_element(
                        By.XPATH, '//*[@id="Label1"]/table/tbody/tr[' + str(i+1) + ']/td[4]')
                    marks.append(mark.text)
                    sub = table.find_element(
                        By.XPATH, '//*[@id="Label1"]/table/tbody/tr[' + str(i+1) + ']/td[1]')
                    subs.append((sub.text).split("\n")[1])
                    result = table.find_element(
                        By.XPATH, '//*[@id="Label1"]/table/tbody/tr[' + str(i+1) + ']/td[6]')
                    results.append(result.text)
                    grade = table.find_element(
                        By.XPATH, '//*[@id="Label1"]/table/tbody/tr[' + str(i+1) + ']/td[7]')
                    grades.append(grade.text)
                i += 1
                            
            driver.quit()
            
            #adding variable in the session
            session['name'] = name
            session['regNo'] = regNo
            session['course'] = course
            session['marks'] = marks
            session['subs'] = subs
            session['results'] = results
            session['grades'] = grades
            session['count'] = len(tr)
            
            return redirect(url_for('results'))
        else:
            redirect(url_for('index'))
    else:
        redirect(url_for('index'))


#result page
@app.route('/results')
def results():
    return render_template('results.html',
                    name = session['name'],
                    regNo = session['regNo'],
                    course = session['course'],
                    marks = session['marks'],
                    subjects = session['subs'],
                    grades = session['grades'],
                    res = session['results'],
                    tot = session['count'],
                    )
    
    
if __name__ == "__main__":
    app.run(debug=True)