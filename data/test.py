from requests import post, get, delete
from datetime import datetime

print(get('http://127.0.0.1:5000/api/v2/jobs/1').json())
# OK
print(get('http://127.0.0.1:5000/api/v2/jobs').json())
# OK
print(get('http://127.0.0.1:5000/api/v2/jobs/999').json())
# User 999 not found
print(post('http://127.0.0.1:5000/api/v2/jobs').json())
# Missing required parameter in the JSON body or the post body or the query string
print(post('http://127.0.0.1:5000/api/v2/jobs',
           json={'team_leader': 1,
                 'jod': 'Work on Mars',
                 'work_size': 500,
                 'collaborators': '1, 2, 3, 4, 5, 6, 7, 8, 9',
                 'start_date': datetime.now(),
                 'end_date': '31.12.9999',
                 'hazard_category': 3,
                 'is_finished': False}).json())
# OK
print(delete('http://127.0.0.1:5000/api/v2/jobs/999').json())
# 'User 999 not found
print(delete('http://127.0.0.1:5000/api/v2/jobs/2').json())
# OK
