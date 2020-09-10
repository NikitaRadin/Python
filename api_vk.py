import requests
import datetime


def calc_age(uid):
    token = '4e76e48c4e76e48c4e76e48c054e05a4c644e764e76e48c115745ce6fc1a402c90996df'
    id = requests.get(f'https://api.vk.com/method/users.get?v=5.71&'
                      f'access_token={token}&user_ids={uid}').json()['response'][0]['id']
    friends = requests.get(f'https://api.vk.com/method/friends.get?v=5.71&'
                           f'access_token={token}&user_id={id}&fields=bdate').json()['response']['items']
    distribution_dictionary = {}
    year = datetime.datetime.now().year
    for friend in list(filter(lambda x: 'bdate' in x and len(x['bdate'].split('.')) == 3, friends)):
        age = year - int(friend['bdate'].split('.')[2])
        if age in distribution_dictionary:
            distribution_dictionary[age] += 1
        else:
            distribution_dictionary[age] = 1
    return sorted([(x, distribution_dictionary[x]) for x in distribution_dictionary], key=lambda x: (-x[1], x[0]))


if __name__ == '__main__':
    res = calc_age('reigning')
    print(res)
