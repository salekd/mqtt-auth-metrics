#!/bin/bash -x
cowsay "Install PostgreSQL"

export NAMESPACE=default

name=postgresql
repo=stable
chart=postgresql
version=6.2.0
values=postgresql-values.yaml

helm fetch $repo/$chart --version $version --untar
diff $values $chart/values-production.yaml

helm install $repo/$chart --name $name --version $version \
  --values $values \
  --namespace $NAMESPACE --debug \
  --tiller-namespace $TILLER_NAMESPACE
