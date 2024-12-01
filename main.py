import requests
import json
from bs4 import BeautifulSoup

headers = {
    'Accept': '*/*',
    'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
}

def get_homepage(dealer_link):
    req = requests.get(f'https://www.autoscout24.de/haendler/{dealer_link}/impressum', headers=headers)
    src = req.text
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



def collect_data():
    dump = []
    amount_of_dealers = input('enter an amount of dealers')
    if amount_of_dealers == '':
        amount_of_dealers = 1000
    car_brands = input('enter car-brands')
    car_brands_split = car_brands.split(' ')
    car_brands =  '%2C'.join(car_brands_split)
    i = 1
    j = 1
    while i <= int (amount_of_dealers) / 10 or i % 10 != 0:

        response = requests.get(
            url=f'https://www.autoscout24.de/dealer-search/api/?country=DE&companyName=&services=&makes={car_brands}&pageIndex={i}&size=10&sortBy=best',
            headers=headers)

        results = response.json()["results"]
        for dealer in results:
            if j >= int (amount_of_dealers) + 1:
                break
            dealer_link = dealer.get("slug")
            dealer_link_about = (f'https://www.autoscout24.de/haendler/{dealer_link}/ueber-uns')
            src = requests.get(dealer_link_about, headers=headers).text
            soup = BeautifulSoup(src, 'lxml')
            json_data = soup.find('script', attrs={'id': '__NEXT_DATA__'}).text
            data = json.loads(json_data)
            with open('next_data.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            with open('next_data.json', 'r', encoding='utf-8') as file:
                next_data = json.load(file)
            dealer_country = (next_data['props']['pageProps']['dealerInfoPage']['customerAddress']['country'])
            if dealer_country == 'DE':
                dealer_country = 'Germany'
            elif dealer_country == 'NL':
                dealer_country = 'Netherlands'
            elif dealer_country == 'LU':
                dealer_country = 'Luxembourg'
            elif dealer_country == 'IT':
                dealer_country = 'Italy'
            elif dealer_country == 'FR':
                dealer_country = 'France'
            elif dealer_country == 'ES':
                dealer_country = 'Spain'
            elif dealer_country == 'BE':
                dealer_country = 'Belgium'
            elif dealer_country == 'AT':
               dealer_country = 'Austria'
            else:
                dealer_country = 'Europe'
            dealer_name = (next_data['props']['pageProps']['dealerInfoPage']['customerName'])
            dealer_zipcode = (next_data['props']['pageProps']['dealerInfoPage']['customerAddress']['zipCode'])
            dealer_city = (next_data['props']['pageProps']['dealerInfoPage']['customerAddress']['city'])
            dealer_street = (next_data['props']['pageProps']['dealerInfoPage']['customerAddress']['street'])
            dealer_phone_number = (next_data['props']['pageProps']['dealerInfoPage']['callPhoneNumbers'])
            dealer_homepage = (next_data['props']['pageProps']['dealerInfoPage']['homepageUrl'])
            contact_person = (next_data['props']['pageProps']['dealerInfoPage']['contactPersons'])

            if dealer_homepage == None:
                dealer_homepage = get_homepage(dealer_link)
            print (dealer_homepage)

            dealer_data = {
                'name': dealer_name, 'country': dealer_country, 'zipCode': dealer_zipcode, 'city': dealer_city,
                'street': dealer_street, 'phoneNumber': dealer_phone_number, 'homepage': dealer_homepage,
                'contactPersons': contact_person
            }

            dump += [dealer_data]

            print(f'{j}. {dealer_name} is processed!')
            j = j + 1
        i = i + 1

    with open('dealer_data.json', 'w', encoding='utf-8') as file:
        json.dump(dump, file, indent=4, ensure_ascii=False)


def main():
    collect_data()


if __name__ == '__main__':
    main()