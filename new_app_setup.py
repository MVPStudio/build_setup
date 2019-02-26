import yaml
import sys
import os
import subprocess
import shutil
from shutil import copyfile
import argparse
import tempfile
from github import Github
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from google.cloud import storage


def main():

    base_path = os.path.abspath(os.path.dirname(__file__))

    parser = argparse.ArgumentParser(description='Usage: python3 '
                                     'new_app_setup.py <Team name> '
                                     '<List of users>')

    parser.add_argument('team_name', type=str,
                        help='Team name')

    parser.add_argument('group_user', type=str, help='An email address that '
                        'will be used for the entire group as a whole.')

    parser.add_argument('-LOU', '--list_of_users',
                        required=False,
                        help='A list of the users for this team.')

    parser.add_argument('-RAM', '--RAM', type=int, required=False,
                        help='How many gigabytes of RAM your team is '
                        'requesting, the deault is 2GB.')

    parser.add_argument('-CPU', '--CPU', type=int, required=False,
                        help="How much CPU your team is requesting, the "
                        "default is one.")

    args = parser.parse_args()

    team_name = args.team_name.replace(" ", "-").replace("_", "-").lower()

    filename = team_name+".yml"

    yml_namespace_file = create_kubernetes_namespace_yml(filename, team_name)

    create_kubernetes_namespace(filename, team_name)

    # create_bucket(team_name)

    config_file = get_congif_yml_file(team_name)

    path_to_congif_file = os.path.join(base_path, config_file)

    if args.list_of_users is not None:
        send_config_email_to_users(team_name, args.list_of_users, config_file)


def create_kubernetes_namespace_yml(filename, team_name):
    '''
    QUESTION: This is only creating their namespace yml right
    now and that is all I am creating later. I am assuming I should
    create another yml for each team to be for their pods which is
    going to hold the spec information we have set above--correct?
    '''
    tag = "Hack_For_A_Cause_2019"

    yml_file_kubernetes_data = dict(

        kind='Namespace',
        apiVersion='v1',
        metadata=dict(
            name=team_name,
            labels=dict(
                name=tag
                )
            )
        )

    with open(filename, 'w') as outfile:
        yaml.dump(yml_file_kubernetes_data, outfile, default_flow_style=False)

    print("The YAML file for {} was created and was "
          "saved as {}".format(team_name, filename))

    return yml_file_kubernetes_data


def create_kubernetes_namespace(filename, team_name):
    subprocess.call(['kubectl', 'create', '-f', filename])

    print("The Kubernetes namespace {} was "
          "created.".format(team_name))


def create_bucket(team_name):
    pass
    # export PROJECT_ID=$(gcloud config get-value team_name)
    # storage_client = storage.Client()
    # bucket = storage_client.create_bucket(team_name)

    # print("Bucket {} was created.".format(bucket.name))


def get_congif_yml_file(team_name):
    config_filename = team_name+'_config_file.yml'

    terminal_command = ['kubectl', 'config', 'view']

    with open(config_filename, 'w') as outfile:
        subprocess.call(terminal_command, stdout=outfile)

    print("The config file for {} was created and "
          "saved as {}".format(team_name, config_filename))
    return config_filename


def send_config_email_to_users(team_name, list_of_users, config_filename):
    '''
    Note: This code is going to change to reflect which email address we
    would be sending this from. This successfully sends emails to GMAIL
    and UOREGON accounts, I have not tried to send to any
    other emails.
    '''
    # QUESTION: What email address do you want me to have these
    # config files send from?
    MVP_email_address = 'abkelley97@gmail.com'

    # This line will be the actual one used to reflect the password
    # for whatever email we send from.
    # MVP_email_address_password = os.environ.get
    #                               ('MVP_EMAIL_ADDRESS_PASSWORD')

    # TEMP for my testing right now:
    MVP_email_address_password = os.environ[str('PROF_EMAIL_PASS')]

    email_contents_subject = ("Kubernetes config file for "
                              "Team " + team_name + " at Hack For A Cause")

    email_contents_body = ("Hi there,\nAttached to this email is your "
                           "Kubernetes configuration file for your team "
                           +team_name+".\nThanks, \nMVP Stuido")

    msg = MIMEMultipart()
    msg['From'] = MVP_email_address
    msg['Subject'] = email_contents_subject

    msg.attach(MIMEText(email_contents_body, 'plain'))

    attachment = open(config_filename, "rb")

    # Allows us to upload the attachment
    part = MIMEBase('application', 'octet-stream')
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', "attachment; filename= " +
                    config_filename)

    msg.attach(part)  # for the attachment
    text = msg.as_string()
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(MVP_email_address, MVP_email_address_password)

    for user in list_of_users.split(','):
        receiver_email_address = user
        msg['To'] = receiver_email_address
        server.sendmail(MVP_email_address, receiver_email_address, text)

    server.close()


def add_user(filename, group_user):
    '''
    QUESTIONS: I am still unclear after looking into this a good amount how we
    are specifically wanting users added. I see the command to create a
    service account:

    kubectl create sa <user>

    but I do not know how to then only have this user be part of a
    specific namespace/change their permissions. I read a bit about creating
    a policy file, but I am not sure if that is the route we were intending.
    '''
    pass


def create_github_repo(team_name):
    pass
#   g = Github(userName, password)
#   org = g.get_organization('MVPStudio')
#   project_description = ("Team " + team_name + " repo for Hack For A Cause")
#   repo = org.create_repo(team_name, description = project_description)


if __name__ == '__main__':
    main()
