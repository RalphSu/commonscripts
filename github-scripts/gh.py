from github import Github
from github import PullRequest
import datetime

# First create a Github instance:

# using username and password
#g = Github("ralphsu", "sss")

# or using an access token
#g = Github("access_token")

# Github Enterprise with custom hostname

# Then play with your Github objects:
#for repo in g.get_user().get_repos():
#    print(repo.name)

def printPRWarning(g, repo="sherlock/Sherlock2", CREATE_WARNING=15, UPDATE_WARNING=7):
    repo = g.get_repo(repo)
    print(repo.name+" weekly warning prs at " + datetime.datetime.now().strftime("%Y-%m-%d"))
    long_create=[]
    long_no_update=[]
    now = datetime.datetime.now()
    for pr in repo.get_pulls():
        if (now - pr.updated_at).days >= UPDATE_WARNING:
            long_no_update.append(pr)
        elif (now - pr.created_at).days >= CREATE_WARNING:
            long_create.append(pr)

    print('Updated Earlier Than ' , UPDATE_WARNING)
    print(long_no_update)
    print("===")
    print('Created Earlier Than ' , CREATE_WARNING)
    print(long_create)

if __name__ == "__main__" :
    g = Github(base_url="https://github.corp.ebay.com/api/v3", login_or_token="f5c5764444a2d3f7e283e2368c780fc126a4d785")
    printPRWarning(g)
