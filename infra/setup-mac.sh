# install helm
brew install helm

# install k3d, 为创建轻量级 K8s 集群
wget -q -O - https://raw.githubusercontent.com/k3d-io/k3d/main/install.sh | bash

# create k3s, 为创建轻量级 K8s 集群
k3d cluster create mycluster

# show k8s nodes
kubectl get nodes
