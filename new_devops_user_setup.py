# TODO: implement

'''
    create user in gcloud with correct devops role
    create clusterrolebinding of cluster-admin

kind: ClusterRoleBinding
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: name-admin-binding
subjects:
- kind: User
  name: name@mvpstudio.org
  apiGroup: rbac.authorization.k8s.io
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: cluster-admin
'''