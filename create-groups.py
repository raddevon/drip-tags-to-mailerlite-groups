import os
import pandas
import requests
from dotenv import load_dotenv

load_dotenv()
mailerlite_key = os.getenv("MAILERLITE_KEY")


def get_groups():
    url = "https://api.mailerlite.com/api/v2/groups"
    headers = {
        "Accept": "application/json",
        "X-MailerLite-ApiKey": mailerlite_key
    }
    response = requests.get(url, headers=headers)
    return response.json()


def build_group_names_list(groups):
    group_names = {group['name'] for group in groups}
    return group_names


def find_group(group_name, groups):
    return next(group for group in groups if group["name"] == group_name)


def people_csv_to_dataframe():
    with open('people.csv', 'r') as people_csv:
        people = pandas.read_csv(people_csv, converters={
                                 'tags': lambda tag_list: tag_list.split(',') if tag_list else []})
    return people


def get_all_tag_names_from_dataframe(dataframe):
    return set(dataframe.tags.sum())


def create_group(group_name):
    url = "https://api.mailerlite.com/api/v2/groups"
    payload = {"name": group_name}
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "X-MailerLite-ApiKey": mailerlite_key
    }
    requests.post(url, json=payload, headers=headers)
    print(f'Created "{group_name}"')


def create_groups(group_names):
    created_count = 0
    for group_name in group_names:
        create_group(group_name)
        created_count += 1
    print(f'Created {created_count} groups')


def build_group_memberships_map(group_names, people_dataframe):
    group_memberships = {}
    for group_name in group_names:
        group_mask = people_dataframe.tags.apply(
            lambda tag_list: group_name in tag_list)
        people_in_group = people_dataframe[group_mask]
        group_memberships[group_name] = people_in_group['email'].tolist()
    return group_memberships


def add_users_to_group(group_id, email_addresses):
    url = f"https://api.mailerlite.com/api/v2/groups/{group_id}/subscribers/import"
    payload = {
        "subscribers": [{"email": email_address} for email_address in email_addresses],
        "resubscribe": False,
        "autoresponders": False,
        "return_status": False
    }
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "X-MailerLite-ApiKey": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiI0IiwianRpIjoiMmNiMDIyZWYzNTMyYzFiNTZlZjE5NjkxMWRmNjNlMDI0MWE0ZmQ5Y2E5YWFjMDYxMjg1YzBlZjM0NzkyYjkzYmYxNDkxMDQ1N2FkYmM2ZDYiLCJpYXQiOjE2NTY4NjkyMDkuNTAwMjMyLCJuYmYiOjE2NTY4NjkyMDkuNTAwMjM0LCJleHAiOjQ4MTI1NDI4MDkuNDk1NjU0LCJzdWIiOiIxMTM2NDYiLCJzY29wZXMiOltdfQ.dUIoPd2IxIx3FAcnUlBUVfvKvUWHLN14lS0Jcidg4cDuwQ-rqYYI8zZd-NMONUqxma5lx0rptVLhntMjDmZddEZNrsJb3NjPit5-OPm-x3YnPdlmWbZxbTmsw1PfU8-zxtnGMg_eHpjsMjVRhwjFVdf_SpRPGT0yN1YR9w2qXZkXP3lkeWs5SiRYAkgnAxeYHyBjUkhwgkoMGtq88RxB3eGrcnquEQxzrK0Hhjqm6BYaBnv5YtVsnQb8dKfrjR8sUS8K6CkJMmffs5Zj7ebO9ztfpw8DgSjYTmFVE2e2cs0wBiXnVqLTLwa2qNxVKrr7AdjUAwCejU8hMo2v2IZYCN0dAPWuBcS-MFKdIu8V4S8IcUgrZZwwCz-FYGGgGBrkXaOAeDKOVAeJd1eK_mLXFG7VPO1i8R88bUPHnaTY560r74aPu5JymdP3sZfJZQi2bsOLjW5tO17FRi5nEAR2ObcoJZeMlS11-H9sBWIhnyDCtgdmMrFQ7IFxoGBAH3XgyBBt-XK63hhbT46fPuwFKDvAuQrX4J18luXE4_WuZRDtgSaXkPOOoClr1F2vQezUF0dkux_Mlulblkaj1Usb4UvhDXo3FaMFo6Df1r0gSscC3tCfpWazmcDDsfNubnCzf300sl07iSMgd-u-GSc7jFlb-9MkDqqZyFLy8zak5_E"
    }
    response = requests.post(url, json=payload, headers=headers)


def add_users_to_groups(groups, group_memberships):
    for group_name, email_address in group_memberships.items():
        subscriber_email_addresses = group_memberships[group_name]
        if not subscriber_email_addresses:
            print(f'No subscribers to add to "{group_name}"')
            continue
        try:
            group_id = find_group(group_name, groups)['id']
        except AttributeError:
            print(f'The group "{group_name}" was not found')
            continue
        print(
            f'Adding {len(subscriber_email_addresses)} subscribers to "{group_name}"')
        add_users_to_group(group_id, subscriber_email_addresses)


existing_groups = get_groups()
existing_group_names = build_group_names_list(existing_groups)
people_dataframe = people_csv_to_dataframe()
all_tag_names = get_all_tag_names_from_dataframe(people_dataframe)
new_group_names = all_tag_names - existing_group_names
create_groups(new_group_names)
group_memberships = build_group_memberships_map(
    all_tag_names, people_dataframe)
add_users_to_groups(existing_groups, group_memberships)
