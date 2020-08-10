from configobj import ConfigObj
import yaml
import json
import requests
import sys

oauth = input("Access Token: ")
repo_urls = sys.argv
repo_urls.pop(0)

github_url = 'https://api.github.com'

headers = {'Accept': 'application/vnd.github.luke-cage-preview+json'}
if oauth is not None:
    headers['Authorization'] = 'token ' + oauth
else:
    raise RuntimeError('No OAuth token entered')

#list of user's repos
repos = requests.get(github_url + '/user/repos',
    headers = headers)
repos.raise_for_status()
repos = repos.json()

#parse settings file
with open('settings.yml', 'r') as stream:
    config = yaml.safe_load(stream)

repo_settings = None
label_settings = None
milestone_settings = None
collaborators_settings = None
teams_settings = None
branches_settings = None

if 'repository' in config.keys():
    repo_settings = config['repository']
if 'labels' in config.keys():
    label_settings = config['labels']
if 'milestones' in config.keys():
    milestone_settings = config['milestones']
if 'collaborators' in config.keys():
    collaborators_settings = config['collaborators']
if 'teams' in config.keys():
    teams_settings = config['teams']
if 'branches' in config.keys():
    branches_settings = config['branches']
    
for repo_url in repo_urls:
    print('Updating Repo ' + repo_url)

    owner = None
    repo_name = None

    #find repo id and user
    for repo in repos:
        if repo['html_url'] == repo_url:
            owner = repo['owner']['login']
            repo_name = repo['name']
            break
    else:
        print('Repository ' + repo_url + ' Not Found. Skipping')
        continue
    
    #update repository
    if repo_settings:
        requests.patch(f'{github_url}/repos/{owner}/{repo_name}',
            data=json.dumps(repo_settings, indent=2), headers=headers)

    #update labels
    if label_settings:
        for label in label_settings:
            label_url = f'{github_url}/repos/{owner}/{repo_name}/labels'
            if 'oldname' in label.keys():
                if 'name' in label.keys():
                    label['new_name'] = label.pop('name')
                requests.patch(label_url + '/' + label['oldname'], data=json.dumps(label, indent=2), headers=headers)
            else:
                label_exist = requests.get(label_url + '/' + label['name'], headers=headers)
                if label_exist.status_code == 200:
                    requests.patch(label_url + '/' + label['name'], data=json.dumps(label, indent=2), headers=headers)
                else:
                    requests.post(label_url, data=json.dumps(label, indent=2), headers=headers)
    
    #update milestones
    if milestone_settings:
        for milestone in milestone_settings:
            requests.post(github_url + '/repos/' + owner + '/' + repo_name + '/milestones',
                data=json.dumps(milestone, indent=2), headers=headers)
    
    #update collaborators
    if collaborators_settings:
        for user in collaborators_settings:
            requests.put(f'{github_url}/repos/{owner}/{repo_name}/collaborators/{user['username']}'',
                data = json.dumps({'permission': user['permission']}, indent=2), headers=headers)
    
    #update teams
    if teams_settings:
        for team in teams_settings:
            org = team['org']
            team_list = requests.get(f'{github_url}/orgs/{org}/teams', headers=headers)
            if team_list.status_code != requests.codes.ok:
                print('Cannot update team ' + team + '. Skipping.\nFor necessary permissions and repository configuration see https://developer.github.com/v3/teams/#add-or-update-team-repository-permissions')
                teams_settings.remove(team)
                break
            team_list = team_list.json()
            for item in team_list:
                if item['name'] == team['name']:
                    team_slug = item['slug']
                    requests.put(f'{github_url}/orgs/{org}/teams/{team_slug}/repos/{owner}/{repo_name}',
                        data = json.dumps({'permission': team['permission']}, indent=2), headers=headers)
                    break

    #update branches
    if branches_settings:
        for branch in branches_settings:
            r = requests.put(f'{github_url}/repos/{owner}/{repo_name}/branches/{branch['name']}/protection',
                data = json.dumps(branch['protection'], indent=2), headers=headers).json()