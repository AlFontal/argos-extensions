import os
import base64
import requests
import datetime
import pandas as pd

exclude_list = []

AVATARS = {
    'Gitlab': 'https://cdn.icon-icons.com/icons2/2415/PNG/32/gitlab_original_logo_icon_146503.png',
    'Github': 'https://cdn.icon-icons.com/icons2/936/PNG/32/github-logo_icon-icons.com_73546.png'
}

ISSUES_EXTENSION = {'Gitlab': '/-/issues', 'Github': '/issues'}

GITLAB_PAGES_ROOT = 'https://alfontal.gitlab.io'  # Replace with own Gitlab pages root.
USERNAME = 'AlFontal'  # Replace with GitHub's username
home_dir = os.path.expanduser('~')

# You should generate and save tokens with read access to your user and repos and then
# place them in ~/.dotfiles/.gitlab_token (or anywhere else, just change the directory here)
with open(f'{home_dir}/.dotfiles/.gitlab_token', 'r') as fh:
    gitlab_token = fh.read().strip()

with open(f'{home_dir}/.dotfiles/.github_token', 'r') as fh:
    github_token = fh.read().strip()

# We define header to be able to use both Gitlab and Github's APIs with authentication
headers = {'Gitlab': {'Authorization': f'Bearer {gitlab_token}'},
           'Github': {'Authorization': f'token {github_token}'}
           }

# Save the responses in json
gitlab_response = requests.get(f'https://gitlab.com/api/v4/users/{USERNAME}/projects',
                               headers=headers['Gitlab']).json()

github_response = requests.get('https://api.github.com/user/repos',
                               headers=headers['Github']).json()

# There is no direct way to fetch whether a Gitlab project has pages (or I don't know it)
# This seems to work although it's a bit hacky.

gitlab_pages = {}
for repo in gitlab_response:
    jobs_response = requests.get(f'https://gitlab.com/api/v4/projects/{repo["id"]}/jobs',
                                 headers=headers['Gitlab']).json()
    if 'pages' in [j['name'] for j in jobs_response]:
        gitlab_pages[repo['name']] = f'{GITLAB_PAGES_ROOT}/{repo["name"]}'

github_df = pd.DataFrame(github_response)
gitlab_df = pd.DataFrame(gitlab_response)

# I just want to show repos with activity during the last year
date_threshold = (datetime.datetime.now() - pd.to_timedelta('1 Y')).strftime('%Y-%m-%d')

gitlab_df = (gitlab_df
             [['name', 'web_url', 'last_activity_at', 'open_issues_count']]
             .rename(columns={'web_url': 'url', 'last_activity_at': 'updated_at',
                              'open_issues_count': 'open_issues'})
             .assign(homepage=gitlab_df.name.map(gitlab_pages).fillna(''))
             .assign(source='Gitlab')
             )

github_df = (github_df
             [['name', 'html_url', 'homepage', 'updated_at', 'open_issues']]
             .rename(columns={'html_url': 'url'})
             .assign(source='Github')
             )

repos_df = (pd.concat([gitlab_df, github_df])
            .sort_values('updated_at', ascending=False)
            .loc[lambda dd: pd.to_datetime(dd.updated_at) >= date_threshold]
    )

print('Repos')
print('---')
for _, repo in repos_df.iterrows():
    if repo['name'] not in exclude_list:
        issues_count = f"({repo['open_issues']})" if repo['open_issues'] else ''
        avatar = base64.b64encode(requests.get(AVATARS[repo['source']]).content).decode()
        print(f'<b>{repo["name"]}</b> | image={avatar} imageWidth=22')
        print(f'--Repository | href={repo["url"]}')
        print(f'--Issues {issues_count} | href={repo["url"]}{ISSUES_EXTENSION[repo["source"]]}')
        if repo['homepage']:
            print(f'--Homepage | href={repo["homepage"]}')