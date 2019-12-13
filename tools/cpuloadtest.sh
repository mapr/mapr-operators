#!/usr/bin/env bash

cspace=<Name of a cspace>
clustername=<Name of a drill clouster>
pods=$1

for i in `seq 0 $pods`
do
  kubectl exec ${clustername}-drillbit-${i} --namespace=${cspace} -- /usr/bin/stress -c 3 &
done
