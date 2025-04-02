import requests
import json
import uuid
from retrying import retry
from bs4 import BeautifulSoup

headers = {
    'Accept': '*/*',
    'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
}

def map_country_code(dealer_country_code):
    if dealer_country_code == 'DE':
        dealer_country = 'Germany'
    elif dealer_country_code == 'NL':
        dealer_country = 'Netherlands'
    elif dealer_country_code == 'LU':
        dealer_country = 'Luxembourg'
    elif dealer_country_code == 'IT':
        dealer_country = 'Italy'
    elif dealer_country_code == 'FR':
        dealer_country = 'France'
    elif dealer_country_code == 'ES':
        dealer_country = 'Spain'
    elif dealer_country_code == 'BE':
        dealer_country = 'Belgium'
    elif dealer_country_code == 'AT':
        dealer_country = 'Austria'
    else:
        dealer_country = 'Europe'
    return dealer_country

def flush_to_disk(data):
    id = uuid.uuid4()
    with open(f'{id}_dealer_data.json', 'a', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
        #file.write('\n')

def get_homepage(src):
    soup = BeautifulSoup(src, 'lxml')
    dealer_impressum = soup.find_all('div', class_='dp-section__text')
    for item in dealer_impressum:
        try:
            item_href = item.find('a').get('href')
        except:
            item_href = 'None'
        if item_href[0] == 'm':
            dealer_href = 'http://' + item_href.split('@')[1]
            return dealer_href
        else:
            return item_href

def get_car_brands():
    car_brand = ''
    car_brands_dump = []
    print('Please select the car brands for which information about dealerships should be collected (press enter if you selected or dont want to select\n1. Mercedes-Benz\n2. Volkswagen\n3. BMW\n4. Audi\n5. Ford\n6. Opel\n7. Skoda\n8. Porsche\n9. Toyota\n10. Renault')
    while(True):
        car_num = input()
        if car_num == '1':
            car_brand = 'Mercedes-Benz'
        elif car_num == '2':
            car_brand = 'Volkswagen'
        elif car_num == '3':
            car_brand = 'BMW'
        elif car_num == '4':
            car_brand = 'Audi'
        elif car_num == '5':
            car_brand = 'Ford'
        elif car_num == '6':
            car_brand = 'Opel'
        elif car_num == '7':
            car_brand = 'Skoda'
        elif car_num == '8':
            car_brand = 'Porsche'
        elif car_num == '9':
            car_brand = 'Toyota'
        elif car_num == '10':
            car_brand = 'Renault'
        elif car_num == '':
            break
        else:
            print('Invalid number!')
        car_brands_dump.append(car_brand)

    car_brands = '%2C'.join(car_brands_dump)
    return car_brands

def get_amount_of_dealers():
    amount_of_dealers = input('Please enter an amount of leads to get data from (default amount is 1000)')
    if amount_of_dealers == '':
        amount_of_dealers = 1000
    return amount_of_dealers

@retry(wait_fixed=100, stop_max_attempt_number=3)
def get_dealers(car_brands, i, size_of_page):
    response = requests.get(
        url=f'https://www.autoscout24.de/dealer-search/api/?country=DE&companyName=&services=&makes={car_brands}&pageIndex={i}&size={size_of_page}&sortBy=best',
        headers=headers)
    return response

@retry(wait_fixed=100, stop_max_attempt_number=3)
def get_dealer_details(dealer_link):
    dealer_link_impressum = (f'https://www.autoscout24.de/haendler/{dealer_link}/impressum')
    src = requests.get(dealer_link_impressum, headers=headers).text
    return src

def collect_dealers_data(amount_of_dealers, car_brands):
    leads = []
    size_of_page = 10
    i = 1
    j = 1
    flush_interval = 100
    while i <= int (amount_of_dealers) / size_of_page or i % size_of_page != 0:
        try:
            response = get_dealers(car_brands, i, size_of_page)
            results = response.json()["results"]

            for dealer in results:
                if j >= int (amount_of_dealers) + 1:
                    break
                dealer_link = dealer.get("slug")
                src = get_dealer_details(dealer_link)
                soup = BeautifulSoup(src, 'lxml')
                json_data = soup.find('script', attrs={'id': '__NEXT_DATA__'}).text
                next_data = json.loads(json_data)
                dealer_info_page = next_data['props']['pageProps']['dealerInfoPage']
                dealer_country_code = (dealer_info_page['customerAddress']['country'])
                dealer_country = map_country_code(dealer_country_code)
                dealer_name = (dealer_info_page['customerName'])
                dealer_zipcode = (dealer_info_page['customerAddress']['zipCode'])
                dealer_city = (dealer_info_page['customerAddress']['city'])
                dealer_street = (dealer_info_page['customerAddress']['street'])
                dealer_phone_number = (dealer_info_page['callPhoneNumbers'])
                dealer_homepage = (dealer_info_page['homepageUrl'])
                contact_person = (dealer_info_page['contactPersons'])

                if dealer_homepage == None:
                    dealer_homepage = get_homepage(src)

                dealer_data = {
                    'name': dealer_name, 'country': dealer_country, 'zipCode': dealer_zipcode, 'city': dealer_city,
                    'street': dealer_street, 'phoneNumber': dealer_phone_number, 'homepage': dealer_homepage,
                    'contactPersons': contact_person
                }

                leads.append(dealer_data)

                print(f'{j}. {dealer_name} is processed!')
                j = j + 1

                if j % flush_interval == 0 or j >= int (amount_of_dealers) + 1:
                    flush_to_disk(leads)
                    leads.clear()

        except Exception as e:
            print(f"Error processing page {i}: {e}")
            continue

        i = i + 1

def main():
    amount_of_dealers = get_amount_of_dealers()
    car_brands = get_car_brands()
    collect_dealers_data(amount_of_dealers, car_brands)


if __name__ == '__main__':
    main()