import os
import re
import requests
from bs4 import BeautifulSoup
originalDirectory = os.getcwd()
print('[1] - MP')
print('[2] - MPI')
print('[3] - PC')
print('[4] - PSI')
print('[5] - TSI')
try:
    user_input = input("Please enter the number equivalent to the filiere you want: ")
    FILIERE = int(user_input) - 1
except ValueError:
    print("not a valid filiere/number")
# PageToScrape = requests.get('https://www.concours-centrale-supelec.fr/CentraleSupelec')
# soup = BeautifulSoup(PageToScrape.text, "html.parser")
YearlyLinks = []
def check_string(string, url):
    # Regular expression pattern to match name.pdf format
    pdf_pattern = r'^[a-zA-Z0-9]+\.(pdf)$'
    
    # Regular expression pattern to match ../.. format
    path_pattern = r'^\.\./\.\..*'
    
    if re.match(pdf_pattern, string):
        return url + string
    if re.match(path_pattern, string):
        return url + string[len("../../"):]
    else:
        return string

def download_pdf(link, save_path, new_name):
    """
    Downloads a PDF from the given link and saves it with the provided name.

    Args:
    link (str): URL of the PDF.
    save_path (str): Path where the PDF will be saved.
    new_name (str): Desired name for the downloaded PDF.
    """
    try:
        response = requests.get(link)
        if response.status_code == 200:
            # Construct the full path with the new name
            new_path = os.path.join(save_path,new_name +'.pdf')
            with open(new_path, 'wb') as file:
                file.write(response.content)
            print(f"PDF downloaded from {link} and saved as {new_path}")
        else:
            print(f"Failed to download PDF from {link}. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error occurred while downloading PDF from {link}: {str(e)}")

def create_folder_with_subfolders(name,subfolder_names):
    # Create the main folder
    main_folder_path = os.path.join(os.path.dirname(__file__), name)
    os.makedirs(main_folder_path, exist_ok=True)

    # Subfolders name must be a string array!

    # Create subfolders inside the main folder
    for subfolder_name in subfolder_names:
        subfolder_path = os.path.join(main_folder_path, subfolder_name)
        os.makedirs(subfolder_path, exist_ok=True)

    print(f"Folder '{name}' with subfolders created successfully.")

def getYearlyLinks():
   
    PageToScrape = requests.get('https://www.concours-centrale-supelec.fr/CentraleSupelec')
    soup = BeautifulSoup(PageToScrape.text, "html.parser")
    # Find all <tr> elements
    tr_elements = soup.find_all('tr')

    # Iterate over each <tr> element
    for tr in tr_elements:
        # Find all <td> elements inside the current <tr> element
        td_elements = tr.find_all('td')
        # Iterate over each <td> element
        if len(td_elements) >= 5:
            fifth_td_element = td_elements[FILIERE]  
            #CHANGE THE INDEX TO CHANGE THE FILIERE      
            # Find all <a> tags inside the current <td> element
            a_tags = td_elements[3].find_all('a')
            # Check if there are any <a> tags
            if a_tags:
                # Get the last <a> tag
                last_a_tag = a_tags[-1]
                YearlyLinks.append(last_a_tag["href"]+'/')
                

def GetEpreuvesNamesAndLinks(url):
    PageToScrape = requests.get(url)
    soup = BeautifulSoup(PageToScrape.text, "html.parser")
    SubjectsNames = []
    LinksToEpreuvesAndNames = []

    # Keyword to search for
    keyword = 'Rédaction'
    # Find all <ul> elements
    ul_elements = soup.find_all('ul')

    first_lis =[]
    # Iterate over each <ul> element
    for ul in ul_elements:
        # Check if the keyword is in the text of the <ul> element
        
        if keyword in ul.get_text():
            
            #print("Found <ul> element containing the keyword:", keyword )
            #print(ul)
            first_lis = ul.find_all('li', recursive=False)
            for i in first_lis:
                SubjectsNames.append(i.contents[0].text)
            
            for i in first_lis:
                temp = []
                for a in i.find_all('a', href = True):
                    
                    finalizedAs = i.find_all(a)
                    # print(a['href'])
                    # print(a.text)
                    temp.append(check_string(a['href'],url))
                    temp.append(a.text)   
                # print(temp)  
                LinksToEpreuvesAndNames.append(temp.copy())
                temp.clear()
    h1_tag = soup.find('h1')
    Year = re.findall(r'\d+', h1_tag.text)         
    #SubjectsNames includes things such as redaction, info, S2i, second array provides more info about the forementioned Topics
    return Year, SubjectsNames, LinksToEpreuvesAndNames


getYearlyLinks()
YearlyLinks.pop(0)
for i in YearlyLinks:
    theYear , theSubjectNames, TheLinksToEpreuvesAndNames = GetEpreuvesNamesAndLinks(i)
    create_folder_with_subfolders('CCS-' + theYear[0], theSubjectNames)
    for j in range(len(theSubjectNames)):
        subjectpath = 'CCS-'+ theYear[0] +'/'+ theSubjectNames[j]
        os.chdir(subjectpath)
        for k in range(len(TheLinksToEpreuvesAndNames[j])):
            if TheLinksToEpreuvesAndNames[j][k].startswith('http'):              
                download_pdf(TheLinksToEpreuvesAndNames[j][k], originalDirectory +'/'+ subjectpath,TheLinksToEpreuvesAndNames[j][k+1] )
            else:
                print(k)
        os.chdir(originalDirectory)