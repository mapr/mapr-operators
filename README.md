# Introduction

This repository contains the code needed to install and use the various operators for MapR products. It currently contains the bootstrap code and examples for the MapR Kubernetes Ecosystem 1.0. These operators include:

* CSpace Operator - An operator used to create CSpace to run compute applications against MapR
* Spark Operator - An operator used to launch Spark jobs
* Drill Operator - An operator used to create Drill clusters

# Directories  

* Bootstrap - Contains code to install operators in your Kubernetes environment
* Examples - Example Custom Resources for the MapR Operators
* Tools - Various scripts to simplify working with the MapR Operators

# Documentation  

[MapR Kubernetes Ecosystem](https://mapr.com/docs/home/PersistentStorage/mdfk_fc_overview.html)

# MapR Kubernetes Ecosystem 1.0 Release Notes   

These notes describe the first release of the MapR Kubernetes Ecosystem.
You may also be interested in the [Kubernetes Release Notes](https://kubernetes.io/docs/setup/release/notes/)

### Version:
1.0                            

### Release Date:
December 2019                        

### MapR Version Interoperability     
Compatible with MapR 5.2.2, 6.0.1, and 6.1.0

### Kubernetes Compatibility
Kubernetes 1.13, 1.14, 1.15, and 1.16.  
*Kubernetes alpha features are not supported.

### OpenShift Compatibility      
4.1

### CSI Driver Compatibility          
Version 1.0. For more information, see MapR Container Storage Interface (CSI) [Storage Plugin Release Notes](https://mapr.com/docs/home/CSIdriver/csi_driver_1.0_release_notes.html)

### Supported Operators  
MapR Drill 1.15 and 1.16
MapR Spark 2.4.4

## Documentation  
MapR Kubernetes Ecosystem Overview

## Related Resources  
[Kubernetes Data Fabric-CSI](https://mapr.com/solutions/data-fabric/kubernetes/)


## New in this Release  
This first release of the MapR Kubernetes Ecosystem includes Spark and Drill operators that run in a Kubernetes environment and leverage data stored on a cloud-based or on-premise MapR Data Platform.

## Patches  
None.

## Limitations  
Note the following limitations:
All nodes in the Kubernetes cluster must use the same Linux OS.

For CSI  -
The Basic POSIX client package is included by default when you install the MapR Container Storage Interface (CSI) Storage Plugin.  
The Platinum POSIX client can be enabled by specifying a parameter in the Pod spec for CSI. Only the FUSE-based POSIX client is supported. NFSv3 and NFSv4 are not supported.

## Known Issues   
Note the following known issues:
MapR Kubernetes Ecosystem containers currently run as the root user.  
K8S-1060: Spark driver attempts to connect to ZooKeeper via hostname lookup. If the Kubernetes cluster cannot DNS resolve the MapR storage cluster, even if IP addresses are used in the configmap, the Spark driver fails with exceptions. Workaround: Kubernetes pods must be able to resolve the external ZooKeeper URL. For more information, see https://kubernetes.io/docs/tasks/administer-cluster/dns-custom-nameservers/.

## Resolved Issues   
None

Copyright 2019 MapR Technologies, Inc., All Rights Reserved
https://mapr.com/legal/eula/
