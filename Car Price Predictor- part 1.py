#!/usr/bin/env python
# coding: utf-8

# ###dvir amitay 318602638 
# #github - https://github.com/dviramitay/dviramitay/blob/main/Project%20-%20part%201.ipynb

# In[7]:


#ניקוי הדאטה מכותרת הרכב

def clean_text(text):
    cleaned_text = text.replace('\xa0', '  ')
    cleaned_text = cleaned_text.replace('\n', ' ')
    cleaned_text = ' '.join(cleaned_text.split())
    parts = cleaned_text.split()
    
    km = ""
    hand = ""
    price = ""
    for i in range(len(parts)):
        if 'ק"מ' in parts[i]:
            km = parts[i-1].replace('K', '000') + ' ' + parts[i]
        elif 'יד' in parts[i]:
            hand = parts[i] + ' ' + parts[i-1]
        elif '₪' in parts[i]:
            price = parts[i-1].replace(',', '')
    
    return [hand, km, price]
    return cleaned_text


# In[8]:


#ייבוא כותרות כל הרכבים

def get_cars_headline(keywords):
    car_list = list()
    import requests
    from bs4 import BeautifulSoup
    page_index=1
    while page_index<10:
        url = "https://www.ad.co.il/car?sp261=13895&pageindex="+str(page_index) 
        response = requests.get(url)
        if not response.status_code == 200:
            print ("not 200")
            return None
        try:
            hyundai_cars = BeautifulSoup(response.content, 'html.parser')
            cars = hyundai_cars.find_all('div',{'class':'card-body p-md-3'})
            for car in cars:
                car_link = car.find('a').get('href')
                car_name = car.find('a').get_text().split()
                if len(car_name)>=2:
                    make=car_name[0]
                    model=car_name[1]
                else:
                    make=car_name[0]
                    model=""
                try:
                    car_description = clean_text(car.find('div',{'class':'d-flex justify-content-between'}).get_text())
                except:
                    car_description = ""
                if make == keywords:
                    car_list.append((make,model,car_link,car_description)) 
        except:
            return None
        page_index += 1
    return car_list  
print(get_cars_headline("יונדאי"))


# In[9]:


#ייבוא התוכן של רכב ספציפי על פי קישור לעמוד 

def get_car_info(car_link):
    car_dict = dict()
    import requests
    from bs4 import BeautifulSoup
    import re
    try:
        response = requests.get(car_link)
        if not response.status_code == 200:
            return car_dict
        result_page = BeautifulSoup(response.content, 'html.parser')

        # איסוף מידע
        info_list = []
        for info in result_page.find_all('table', class_='table table-sm mb-4'):
            rows = info.find_all('tr')
            for row in rows:
                cells = row.find_all('td')
                for cell in cells:
                    text = cell.get_text(strip=True)
                    if text:
                        info_list.append(text)

        for info in result_page.find_all('div', class_='d-flex flex-row align-items-center justify-content-center flex-wrap'):
            text = info.get_text(strip=True)
            if "תאריך יצירה" in text:
                match = re.search(r"תאריך יצירה:\s*(\d{2}/\d{2}/\d{4})", text)
                if match:
                    car_dict["תאריך יצירה"] = match.group(1)
            if "תאריך הקפצה אחרון" in text:
                match = re.search(r"תאריך הקפצה אחרון:\s*(\d{2}/\d{2}/\d{4})", text)
                if match:
                    car_dict["תאריך הקפצה"] = match.group(1)

        # יצירת מילון ממפתח וערך בלולאה
        for i in range(0, len(info_list) - 1, 2):
            key = info_list[i]
            value = info_list[i + 1]
            car_dict[key] = value

        # איסוף תמונות
        img_list = []
        for img in result_page.find_all('img', class_='desktop-thumbnail bg-video'):
            img_src = img.get('src')
            if img_src:
                img_list.append(img_src)
        car_dict['מספר תמונות'] = len(img_list)
        
        # תיאור
        describe = result_page.find('p', {'class': 'text-word-break'})
        if describe:
            car_dict['תיאור'] = describe.get_text(strip=True)
        
        return car_dict
    except Exception as e:
        print(f"An error occurred: {e}")
        return car_dict

# דוגמה לשימוש בפונקציה
car_link = 'https://www.ad.co.il/ad/16166775'
car_info = get_car_info(car_link)
print(car_info)


# In[14]:


#פונקציה לסידור המילון 
  
from datetime import datetime

def fix_data(car_dict):
    # להמיר את הערכים לסוגי נתונים המתאימים
    if 'שנה' in car_dict:
        car_dict['שנה'] = int(car_dict['שנה'])
    
    if 'יד' in car_dict:
        car_dict['יד'] = int(car_dict['יד'])
    
    if 'נפח' in car_dict:
        car_dict['נפח'] = int(car_dict['נפח'].replace(',', ''))
    
    if 'מחיר' in car_dict and car_dict['מחיר'] != 'N/A':
        try:
            car_dict['מחיר'] = float(car_dict['מחיר'])
        except ValueError:
            car_dict['מחיר'] = 0.0  
    
    if 'מספר תמונות' in car_dict:
        car_dict['מספר תמונות'] = int(car_dict['מספר תמונות'])
    
    # להמיר את הערכים של תאריכים אם קיימים
    if 'תאריך יצירה' in car_dict:
        car_dict['תאריך יצירה'] = datetime.strptime(car_dict['תאריך יצירה'], '%d/%m/%Y')
    
    if 'תאריך הקפצה' in car_dict:
        car_dict['תאריך הקפצה'] = datetime.strptime(car_dict['תאריך הקפצה'], '%d/%m/%Y')
    
    # חישוב ההפרש של "טסט עד" מהתאריך של היום
    today = datetime.today()
    if 'טסט עד' in car_dict:
        test_date = datetime.strptime(car_dict['טסט עד'], '%m/%Y')
        months_diff = (test_date.year - today.year) * 12 + test_date.month - today.month
        car_dict['טסט עד'] = months_diff
    
    # להמיר את הערך של ק"מ
    if 'ק"מ' in car_dict:
        car_dict['ק"מ'] = int(car_dict['ק"מ'].replace(',', ''))
    
    return car_dict


# In[17]:


#יצירת מילון עם כל הרכבים

def get_all_cars(keywords):
    results = list()
    all_cars = get_cars_headline(keywords)
    for car in all_cars:
        car_dict = {}
        car_dict['יצרן']= car[0]
        car_dict['דגם']= car[1]
        try:
            car_dict['מחיר'] = car[3][2]
        except IndexError:
            car_dict['מחיר'] = 'N/A'
        a = get_car_info('https://www.ad.co.il'+car[2])
        car_dict.update(a)
        car_dict = fix_data(car_dict)
        
        results.append(car_dict)
    return(results)
hyundai_cars = get_all_cars("יונדאי")
hyundai_cars


# In[19]:


import pandas as pd
df=pd.DataFrame(hyundai_cars)
df = df[df['שנה'] > 2013]
df


# In[21]:


df.to_csv('hyundai_cars.csv', index=False, encoding='utf-8-sig')


# In[ ]:




