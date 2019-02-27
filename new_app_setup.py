import yaml
import sys
import os
import subprocess
import shutil
import array
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
                        'requesting, the deault is 2G.')

    parser.add_argument('-CPU', '--CPU', type=int, required=False,
                        help="How much CPU your team is requesting, the "
                        "default is one.")

    args = parser.parse_args()

    team_name = args.team_name.replace(" ", "-").replace("_", "-").lower()

    namespace_filename = team_name+"_namespace.yml"

    pods_filename = team_name+"_pods.yml"

    create_kubernetes_namespace_yml(namespace_filename, team_name)

    create_kubernetes(namespace_filename, team_name, "namespace")

    if args.RAM is not None:
        ram_requested = args.RAM
    else:
        ram_requested = '2G'  # default

    if args.CPU is not None:
        cpu_requested = args.CPU
    else:
        cpu_requested = '1'  # default

    create_kubernetes_pods_yml(pods_filename, team_name, ram_requested,
                               cpu_requested)

    create_kubernetes(pods_filename, team_name, "pods")

    config_file = get_congif_yml_file(team_name)

    path_to_congif_file = os.path.join(base_path, config_file)

    send_config_email_to_users(team_name, args.group_user, config_file)

    if args.list_of_users is not None:
        send_config_email_to_users(team_name, args.list_of_users, config_file)


def create_kubernetes_namespace_yml(namespace_filename, team_name):

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

    with open(namespace_filename, 'w') as outfile:
        yaml.dump(yml_file_kubernetes_data, outfile, default_flow_style=False)

    print("The YAML file for {} was created and was "
          "saved as {}".format(team_name, namespace_filename))

    return yml_file_kubernetes_data


def create_kubernetes_pods_yml(pods_filename, team_name, ram_requested,
                               cpu_requested):
    yml_file_kubernetes_data = dict(
        kind='Pod',
        apiVersion='v1',
        metadata=dict(
            name=team_name,
            namespace=team_name,
            ),
        spec=dict(
                containers=dict(
                    name=team_name,  # QUESTION HERE -> see below
                    resources=dict(
                        limits=dict(
                            cpu="1",
                            memory="2G"
                        ),
                        requests=dict(
                            cpu=cpu_requested,
                            memory=ram_requested,
                        )
                    )
                )
            )
        )
# QUESTION: When running, I am getting the warning:

# "error: error validating "test-team-name_pods.yml": error validating
# data: ValidationError(Pod.spec.containers): invalid type for
# io.k8s.api.core.v1.PodSpec.containers: got "map", expected "array";
# if you choose to ignore these errors, turn validation off with
# --validate=false
# and I know that is because name does not have the hyphen indicating an array
# in front of it, but I cannot seem to figure out how to do this...
# anything I'm missing?

    with open(pods_filename, 'w') as outfile:
        yaml.dump(yml_file_kubernetes_data, outfile, default_flow_style=False)

    print("The YAML file for {} pods were created and was "
          "saved as {}".format(team_name, pods_filename))

    return yml_file_kubernetes_data


def create_kubernetes(filename, team_name, type_of_create):
    subprocess.call(['kubectl', 'create', '-f', filename])

    print("The Kubernetes {} for {} was "
          "created.".format(type_of_create, team_name))


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


def send_config_email_to_users(team_name, email_to, config_filename):
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
                           "Kubernetes configuration file for your team " +
                           team_name + ".\nThanks, \nMVP Stuido")

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

    if type(email_to) is list:
        for user in email_to.split(','):
            receiver_email_address = user
            msg['To'] = receiver_email_address
            server.sendmail(MVP_email_address, receiver_email_address, text)
            print ("The config file for {} has successfully been sent "
                   "to {}".format(team_name, user))

    else:
        receiver_email_address = email_to
        msg['To'] = receiver_email_address
        server.sendmail(MVP_email_address, receiver_email_address, text)
        print ("The config file for {} has successfully been sent "
               "to {}".format(team_name, email_to))

    server.close()


def add_users(filename, group_user, list_of_users):
    '''
    QUESTIONS: I am still unclear after looking into this a good amount how we
    are specifically wanting users added. I don't know how to have each user be
    part of a specific namespace/change their permissions. I read a bit about
    creating a policy file, but I am not sure if that is the route we were
    intending.
    '''
    subprocess.check_call(['kubectl', 'create', 'sa', group_user])

    print("A Kubernetes service account for {} has been created under "
          "{}".format(group_user, team_name))

    # QUESTION: Did we still want to add additional users for the group
    # if they provide us a list of them?
    for user in list_of_users.split(','):
        subprocess.check_call(['kubectl', 'create', 'sa', user])
        print("A Kubernetes service account for {} has been created "
              "under {}".format(user, team_name))

if __name__ == '__main__':
    main()
