import json 
import os
import time
from datetime import datetime, timedelta

def convert_to_seconds(months=0, weeks=0, days=0, hours=0, minutes=0):
    total_days = (months * 30) + (weeks * 7) + days
    total_hours = (total_days * 24) + hours
    total_minutes = (total_hours * 60) + minutes
    total_seconds = total_minutes * 60
    return total_seconds

def convert_to_json(seconds):
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    weeks, days = divmod(days, 7)
    months = days // 30

    data = {
        "months": int(months),
        "weeks": int(weeks),
        "days": int(days),
        "hours": int(hours),
        "minutes": int(minutes)
    }

    json_data = json.dumps(data)
    return json_data

def permission_to_publish(url):
    with open(os.path.join(os.getcwd(), 'data.json'), 'r', encoding="UTF-8") as f:
        data = json.loads(f.read())

    detected = False
    for item in data:
        if item['url'] == url:
            detected = True
            publication_date = datetime.fromisoformat(item['latest_publication_date'])
            publication_interval = int(item['publication_interval'])
            next_publication_time = publication_date + timedelta(seconds=publication_interval)
            current_time = datetime.now()

            next_publication_time_str = next_publication_time.isoformat()

            if current_time >= next_publication_time:
                print("You can publish now.")
                return json.dumps({"bool": True, 'next_publication_time': next_publication_time_str})
            else:
                print("You cannot publish yet. Next publication time:", next_publication_time_str)
                return json.dumps({"bool": False, 'next_publication_time': next_publication_time_str})

    if not detected:
        return json.dumps({"bool": False, 'next_publication_time': False})

def add_url_images(url, url_image):
    with open(os.path.join(os.getcwd(), 'data.json'), 'r', encoding="UTF-8") as f:
        data = json.loads(f.read())
    
    sended = False
    for item in data:
        if item['url'] == url:
            sended = True
            if len(item['url_images']) > 0:
                for link in item['url_images']:
                    if link == url_image:
                        return False
                item['url_images'].append(url_image)
            else:
                item['url_images'].append(url_image)
            with open(os.path.join(os.getcwd(), 'data.json'), 'w', encoding="UTF-8") as f:
                json.dump(data, f, indent=2)

            return True
        
    if sended == False:
        return False

def write_json(url, date_publication, publication_interval):
    with open(os.path.join(os.getcwd(), 'data.json'), 'r', encoding="UTF-8") as f:
        data = json.loads(f.read())
    # DATE
    time_string = date_publication.isoformat()
    check_published = json.loads(permission_to_publish(url))
    next_publication_time = check_published['next_publication_time']

    obj = {
        "url": url,
        "latest_publication_date": time_string,
        "publication_interval": publication_interval,
        "next_publication_time": next_publication_time,
        "url_images": []
    }

    if len(data) == 0:
        print('first obj added')
        data.append(obj)
        with open(os.path.join(os.getcwd(), 'data.json'), 'w', encoding="UTF-8") as f:
            json.dump(data, f, indent=2)

        return time_string
    else:
        detected = False
        for item in data:
            if item['url'] == url:
                detected = True
                if check_published['bool']:
                    item['latest_publication_date'] = time_string
                    item['next_publication_time'] = next_publication_time
                    with open(os.path.join(os.getcwd(), 'data.json'), 'w', encoding="UTF-8") as f:
                        json.dump(data, f, indent=2)
                    print('You can publish')
                    return time_string
                else:
                    if check_published['next_publication_time'] == False:
                        print("Does not have the following publication, because this site is not in the database")
                    else:
                        print("No time to publish, the next publication will be: ", check_published)

                    return False


        if detected == False:
            print('added')
            data.append(obj)
            with open(os.path.join(os.getcwd(), 'data.json'), 'w', encoding="UTF-8") as f:
                json.dump(data, f, indent=2)

            return time_string

def new_url(url):
    # Check if it's okay to publish now
    # Function for recording data
    with open(os.path.join(os.getcwd(), 'env.json'), 'r', encoding="UTF-8") as f:
        data = json.loads(f.read())
    dp = data['PUBLICATION_INTERVAL']
    write_return = write_json(url, datetime.now(), convert_to_seconds( dp['months'], dp['weeks'], dp['days'], dp['hours'], dp['minutes']))
    if write_return != False:
        publication(url, write_return)

def publication(url, date):
    print('Published, time:', date)
    
def core():
    while True:
        try:
            with open(os.path.join(os.getcwd(), 'data.json'), 'r', encoding="UTF-8") as f:
                data_json = json.loads(f.read())

            with open(os.path.join(os.getcwd(), 'env.json'), 'r', encoding="UTF-8") as f:
                data = json.loads(f.read())
            dp = data['PUBLICATION_INTERVAL']

            for blog in data_json:
                time.sleep(2)
                print( blog['url'])
                write_return = write_json(blog['url'], datetime.now(), convert_to_seconds( dp['months'], dp['weeks'], dp['days'], dp['hours'], dp['minutes']))
                if write_return != False:
                    publication(blog['url'], write_return)

            time.sleep(2)
        except Exception as e:
            print('Error: ', e)
            continue

if __name__ == "__main__":
    # The main core, which checks if it is possible to publish, and if it is, issues a command to publish
    core()

    # Adding a link to the database
    # new_url('https://google.com/')

    # # Add images
    # url_image = "https://www.freepik.com/free-photo/white-t-shirts-with-copy-space-gray-background_15667327.htm#&position=1&from_view=popular"
    # add_url_images(url, url_image)
