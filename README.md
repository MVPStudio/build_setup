# build_setup

New App Setup   

```
python3 new_app_setup.py --team_name current-team-name
```

This command will create a gcloud servie account, and a Kubernetes namespace for your team. Your kubernetes namespace will be given a rolebinding so you will have complete access to your specific namespace. 


After the script is ran, the team will need to have google SDK installed on their machine. We will send the team their credentials in a json file which they will need to include in the following command:

```
gcloud auth activate-service-account [SERVICE ACCOUNT EMAIL] --key-file=./current_team_name_gcloud_serviceaccount_key.json
```

Once the team has been authenticated, they will be able to access their Kubernetes namespace, and they will need to run this configuration command:

```
kubectl config set-context gke_mvpstudio_us-west1_main --namespace=current-team-name
```


Build Tag Push 

The next steps would be to deploy their Travis CI build, which will then run the build_tag_push.sh which calls build_tag_push.py to create their DockerHub repository within the MVPStudio organization.

Permissions Note:

In order for someone to run this script, they will need to have the DevOps role linked to their gcloud account, and they will need to be role-binded with cluster-admin permissions within Kubernetes. 
TOOO: automate this with the script 
``` 
new_devops_user_setup.py
```

Future implementation:

Automate the Travis CI build, remove permissions from someone so they will be unable to run this script, and to delete unused resources within GCloud, Kubernetes, and DockerHub.