from requests import post, get, delete

print(get('http://127.0.0.1:5000/api/v2/users/1').json())
# OK
print(get('http://127.0.0.1:5000/api/v2/users').json())
# OK
print(get('http://127.0.0.1:5000/api/v2/users/999').json())
# User 999 not found
print(post('http://127.0.0.1:5000/api/v2/users').json())
# Missing required parameter in the JSON body or the post body or the query string
print(post('http://127.0.0.1:5000/api/v2/users',
           json={'surname': 'Попов',
                 'name': 'Петр',
                 'age': '40',
                 'position': 'зам',
                 'speciality': 'Спец по безопасности',
                 'address': 'модуль_5',
                 'email': 'popov@mars.org'}).json())
# OK
print(delete('http://127.0.0.1:5000/api/v2/users/999').json())
# 'User 999 not found
print(delete('http://127.0.0.1:5000/api/v2/users/2').json())
# OK
