# Hack for a Cause 2019 Team Steps for MVPStudio Implementation:

Step 1) Download/install gcloud. It is preferable that you do not login after you install it, but if you do, you will need to switch accounts.

---
Step 2) We will create a gcloud service account for your team, and a DockerHUb repository within out MVPStudio organization, a Kubernetes namespace, role for your team and binding for the gcloud service account limits the access so each team can only run commands against their own namespace. We will then provide you with your gcloud information via a json file.

---
Step 3) Run the following command:

``` gcloud auth activate-service-account team-name@mvpstudio.iam.gserviceaccount.com --key-file=/path/to/team-name_gcloud_serviceaccount_key.json ```

---

Step 4) Setup your kube config with the following command:

``` gcloud beta container clusters get-credentials main --region us-west1 --project mvpstudio ```

---

Step 5) Install kubectl:

``` gcloud components install kubectl ```

---

- Step 6) Set your default namespace for your team:

``` kubectl config set-context gke_mvpstudio_us-west1_main --namespace=team-name ```

---

Step 7) Create your Dockerfile in your repository root

---

Step 8) Create your CircleCI configuration in a subdirectory named .circleci/config.yml in your repository. 

- Here is an example:
https://github.com/Hack4Eugene/mvp-testing/blob/master/.circleci/config.yml

---

Step 9) Create the directory .mvpstudio and have your .config.yml and runit.yml in it. 

- Here is an example:
https://github.com/Hack4Eugene/mvp-testing/tree/master/.mvpstudio 
(please edit your files to have your team-name replace "mvp-testing")

You can check your build status here:
https://circleci.com/gh/Hack4Eugene/team-name

---

Step 10) Run the following command to deploy:

```kubectl apply -f ```

- Note: You will need to modify your git hash which you can find as a tag for your docker image, which you can access here:
https://hub.docker.com/r/mvpstudio/team-name

---