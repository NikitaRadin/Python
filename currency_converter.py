from decimal import Decimal
from bs4 import BeautifulSoup


def convert(amount, cur_from, cur_to, date, requests):
    amount = Decimal(str(amount))
    response = requests.get('https://www.cbr.ru/scripts/XML_daily.asp', params={'date_req': date})
    soup = BeautifulSoup(response.content, 'xml')
    nominal_from = int(soup.find('CharCode', text=cur_from).find_next_sibling('Nominal').string)
    rate_from = Decimal(str(soup.find('CharCode', text=cur_from).find_next_sibling('Value').string).replace(',', '.'))
    nominal_to = int(soup.find('CharCode', text=cur_to).find_next_sibling('Nominal').string)
    rate_to = Decimal(str(soup.find('CharCode', text=cur_to).find_next_sibling('Value').string).replace(',', '.'))
    return (amount * (rate_from / nominal_from) / (rate_to / nominal_to)).quantize(Decimal('0.0000'))
