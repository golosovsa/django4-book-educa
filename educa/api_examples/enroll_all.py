import requests

username = 'grm'
password = ''
base_url = 'http://127.0.0.1:8000/api/'

r = requests.get(f'{base_url}courses/')
courses = r.json()

available_courses = ', '.join([course['title'] for course in courses])
print(f'Available courses: {available_courses}')

for course in  courses:
    course_pk = course['pk']
    course_title = course['title']
    r = requests.post(f'{base_url}courses/{course_pk}/enroll/', auth=(username, password))
    if r.status_code == 200:
        print(f'Successfully enrolled in {course_title}')
