import json

f = open('example_video_response.json')

data = json.load(f)

list_of_video_links = []

for item in data['videos']['video_files']:
    height = item['height']
    width = item['width']
    print(height)
    print(width)
