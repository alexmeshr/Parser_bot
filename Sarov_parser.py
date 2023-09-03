from bs4 import BeautifulSoup
import requests
import os

def parse_msu_website(pdf_path = "./pdf_files", logging=False):
    if not os.path.exists(pdf_path):
        os.makedirs(pdf_path)

    base_url = "https://sarov.msu.ru"
    raspisanie_url = base_url+"/raspisanie"
    response = requests.get(raspisanie_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    links = soup.find_all('a')
    i = 0
    for link in links:
        if ('.pdf' in link.get('href', [])):
            i += 1
            if logging:
                print("Downloading file: ", i)
            response = requests.get(base_url+link.get('href'))
            pdf = open(pdf_path+"/file_" + str(i) + ".pdf", 'wb')
            pdf.write(response.content)
            pdf.close()
            if logging:
                print("File ", i, " downloaded")

    if logging:
        print("All PDF files downloaded")

if __name__ == "__main__":
    parse_msu_website(logging=True)