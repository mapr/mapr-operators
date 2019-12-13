import os

from common.const import Constants
from common.file_utils import FileUtils
from common.mapr_logger.log import Log
from common.os_command import OSCommand
from mapr_exceptions.ex import NotFoundException


class K8SOperations(object):
    KUBECTL_APPLY = "kubectl apply -f"
    OC_APPLY = "oc apply -f"
    KUBECTL_DELETE = "kubectl delete -f"
    OC_DELETE = "oc delete -f"
    KUBECTL_GET = "kubectl get"
    KUBECTL_LABEL_NODE = "kubectl label node --overwrite {0} \"{1}={2}\""

    def __init__(self, prompts, base_dir):
        self._prompts = prompts
        self.username = Constants.USERNAME
        self.password = Constants.PASSWORD
        self.groupname = Constants.GROUPNAME
        self.userid = Constants.USERID
        self.groupid = Constants.GROUPID
        self.mysql_user = Constants.MYSQL_USER
        self.mysql_pass = Constants.MYSQL_PASS
        self.ldapadmin_user = Constants.LDAPADMIN_USER
        self.ldapadmin_pass = Constants.LDAPADMIN_PASS
        self.ldapbind_user = Constants.LDAPBIND_USER
        self.ldapbind_pass = Constants.LDAPBIND_PASS
        self.is_openshift = False
        # need to parameterize these and move prereqs out of the old bootstrapper
        self.prereq_dir = os.path.abspath(os.path.join(base_dir, "../prereqs"))
        self.csi_dir = os.path.abspath(os.path.join(self.prereq_dir, "csi"))
        self.drill_dir = os.path.abspath(os.path.join(self.prereq_dir, "drill"))
        self.external_dir = os.path.abspath(os.path.join(self.prereq_dir, "external"))
        self.spark_dir = os.path.abspath(os.path.join(self.prereq_dir, "spark"))
        self.system_cspace_dir = os.path.abspath(os.path.join(self.prereq_dir, "system-cspace"))
        self.config_cspaces_dir = os.path.abspath(os.path.join(self.prereq_dir, "configuration-cspaces"))
        self.system_cluster_dir = os.path.abspath(os.path.join(self.prereq_dir, "system-cluster"))
        self.config_clusters_dir = os.path.abspath(os.path.join(self.prereq_dir, "configuration-clusters"))
        self.bootstrap_dir = os.path.abspath(os.path.join(self.prereq_dir, "bootstrap"))
        #self.ingress_dir = os.path.abspath(os.path.join(self.prereq_dir, "ingress"))
        #self.kubeflow_dir = os.path.abspath(os.path.join(self.prereq_dir, "kubeflow"))
        #self.ui_dir = os.path.abspath(os.path.join(self.prereq_dir, "ui"))
        if not os.path.exists(self.prereq_dir):
            raise NotFoundException(self.prereq_dir)
        self.yamls = dict()
        self.load_yaml_dict()

    @staticmethod
    def _run(cmd):
        response, status = OSCommand.run2(cmd)
        if status != 0:
            Log.error("Could not run {0}: {1}:{2}".format(cmd, str(status), response))
            return False
        return True

    @staticmethod
    def _run_and_return_response(cmd, print_error=True):
        response, status = OSCommand.run2(cmd)
        if status != 0:
            if print_error:
                Log.error("Could not run {0}: {1}:{2}".format(cmd, str(status), response))
            return None
        return response

    @staticmethod
    def check_exists(adir, ayaml):
        abs_file = os.path.join(adir, ayaml)
        if not os.path.exists(abs_file) or not os.path.isfile(abs_file):
            raise NotFoundException("{0} must exist and must be a file".format(abs_file))

        return abs_file

    def load_yaml_dict(self):
        self.yamls["configuration-cspaceterminal-cm"] = self.check_exists(self.config_cspaces_dir, "configuration-cspaceterminal-cm.yaml")
        self.yamls["configuration-hivemeta-cm"] = self.check_exists(self.config_cspaces_dir, "configuration-hivemeta-cm.yaml")
        self.yamls["configuration-psp-cspace"] = self.check_exists(self.config_cspaces_dir, "configuration-psp-cspace.yaml")
        self.yamls["configuration-role-cspace"] = self.check_exists(self.config_cspaces_dir, "configuration-role-cspace.yaml")
        self.yamls["configuration-role-cspace-terminal"] = self.check_exists(self.config_cspaces_dir, "configuration-role-cspace-terminal.yaml")
        self.yamls["configuration-role-cspace-user"] = self.check_exists(self.config_cspaces_dir, "configuration-role-cspace-user.yaml")
        self.yamls["configuration-sparkhistory-cm"] = self.check_exists(self.config_cspaces_dir, "configuration-sparkhistory-cm.yaml")
        self.yamls["configuration-namespace"] = self.check_exists(self.config_cspaces_dir, "configuration-namespace.yaml")
        self.yamls["configuration-ldapclient-cm"] = self.check_exists(self.config_cspaces_dir, "configuration-ldapclient-cm.yaml")
        self.yamls["configuration-sssdsecret"] = self.check_exists(self.config_cspaces_dir, "configuration-sssdsecret.yaml")
        self.yamls["csi-attacher-cr"] = self.check_exists(self.csi_dir, "csi-attacher-cr.yaml")
        self.yamls["csi-attacher-crb"] = self.check_exists(self.csi_dir, "csi-attacher-crb.yaml")
        self.yamls["csi-nodeplugin"] = self.check_exists(self.csi_dir, "csi-deploy-nodeplugin.yaml")
        self.yamls["csi-openshift-nodeplugin"] = self.check_exists(self.csi_dir, "csi-deploy-openshift-nodeplugin.yaml")
        self.yamls["csi-openshift-provisioner"] = self.check_exists(self.csi_dir, "csi-deploy-openshift-provisioner.yaml")
        self.yamls["csi-provisioner"] = self.check_exists(self.csi_dir, "csi-deploy-provisioner.yaml")
        self.yamls["csi-imagepullsecret"] = self.check_exists(self.csi_dir, "csi-imagepullsecret.yaml")
        self.yamls["csi-namespace"] = self.check_exists(self.csi_dir, "csi-namespace.yaml")
        self.yamls["csi-nodeplugin-cr"] = self.check_exists(self.csi_dir, "csi-nodeplugin-cr.yaml")
        self.yamls["csi-nodeplugin-crb"] = self.check_exists(self.csi_dir, "csi-nodeplugin-crb.yaml")
        self.yamls["csi-nodeplugin-sa"] = self.check_exists(self.csi_dir, "csi-nodeplugin-sa.yaml")
        self.yamls["csi-provisioner-cr"] = self.check_exists(self.csi_dir, "csi-provisioner-cr.yaml")
        self.yamls["csi-provisioner-crb"] = self.check_exists(self.csi_dir, "csi-provisioner-crb.yaml")
        self.yamls["csi-provisioner-sa"] = self.check_exists(self.csi_dir, "csi-provisioner-sa.yaml")
        self.yamls["csi-scc"] = self.check_exists(self.csi_dir, "csi-scc.yaml")
        self.yamls["drill-cr"] = self.check_exists(self.drill_dir, "drill-cr.yaml")
        self.yamls["drill-crb"] = self.check_exists(self.drill_dir, "drill-crb.yaml")
        self.yamls["drill-crd"] = self.check_exists(self.drill_dir, "drill-crd.yaml")
        self.yamls["drill-drilloperator"] = self.check_exists(self.drill_dir, "drill-deploy-drilloperator.yaml")
        self.yamls["drill-imagepullsecret"] = self.check_exists(self.drill_dir, "drill-imagepullsecret.yaml")
        self.yamls["drill-namespace"] = self.check_exists(self.drill_dir, "drill-namespace.yaml")
        self.yamls["drill-rb"] = self.check_exists(self.drill_dir, "drill-rb.yaml")
        self.yamls["drill-role"] = self.check_exists(self.drill_dir, "drill-role.yaml")
        self.yamls["drill-sa"] = self.check_exists(self.drill_dir, "drill-sa.yaml")
        self.yamls["drill-scc"] = self.check_exists(self.drill_dir, "drill-scc.yaml")
        self.yamls["external-namespace"] = self.check_exists(self.external_dir, "external-namespace.yaml")
        self.yamls["spark-cr"] = self.check_exists(self.spark_dir, "spark-cr.yaml")
        self.yamls["spark-crb"] = self.check_exists(self.spark_dir, "spark-crb.yaml")
        self.yamls["spark-crd-sparkapplication"] = self.check_exists(self.spark_dir, "spark-crd-sparkapplication.yaml")
        self.yamls["spark-crd-sparkscheduledapplication"] = self.check_exists(self.spark_dir, "spark-crd-sparkscheduledapplication.yaml")
        self.yamls["spark-sparkoperator"] = self.check_exists(self.spark_dir, "spark-deploy-sparkoperator.yaml")
        self.yamls["spark-imagepullsecret"] = self.check_exists(self.spark_dir, "spark-imagepullsecret.yaml")
        self.yamls["spark-job"] = self.check_exists(self.spark_dir, "spark-job-sparkoperator.yaml")
        self.yamls["spark-namespace"] = self.check_exists(self.spark_dir, "spark-namespace.yaml")
        self.yamls["spark-sa"] = self.check_exists(self.spark_dir, "spark-sa.yaml")
        self.yamls["spark-scc"] = self.check_exists(self.spark_dir, "spark-scc.yaml")
        self.yamls["spark-svc"] = self.check_exists(self.spark_dir, "spark-svc-sparkoperator.yaml")
        self.yamls["system-cr-cspace"] = self.check_exists(self.system_cspace_dir, "system-cr-cspace.yaml")
        self.yamls["system-crb-cspace"] = self.check_exists(self.system_cspace_dir, "system-crb-cspace.yaml")
        self.yamls["system-cr-pv"] = self.check_exists(self.system_cspace_dir, "system-cr-pv.yaml")
        self.yamls["system-crd-cspace"] = self.check_exists(self.system_cspace_dir, "system-crd-cspaceoperator.yaml")
        self.yamls["system-cspaceoperator"] = self.check_exists(self.system_cspace_dir, "system-deploy-cspaceoperator.yaml")
        self.yamls["system-cspaceoperator-openshift"] = self.check_exists(self.system_cspace_dir, "system-deploy-cspaceoperator-openshift.yaml")
        self.yamls["system-imagepullsecret"] = self.check_exists(self.system_cspace_dir, "system-imagepullsecret.yaml")
        self.yamls["system-namespace"] = self.check_exists(self.system_cspace_dir, "system-namespace.yaml")
        self.yamls["system-priorityclass-admin"] = self.check_exists(self.system_cspace_dir, "system-priorityclass-admin.yaml")
        self.yamls["system-priorityclass-clusterservices"] = self.check_exists(self.system_cspace_dir, "system-priorityclass-clusterservices.yaml")
        self.yamls["system-priorityclass-compute"] = self.check_exists(self.system_cspace_dir, "system-priorityclass-compute.yaml")
        self.yamls["system-priorityclass-critical"] = self.check_exists(self.system_cspace_dir, "system-priorityclass-critical.yaml")
        self.yamls["system-priorityclass-gateways"] = self.check_exists(self.system_cspace_dir, "system-priorityclass-gateways.yaml")
        self.yamls["system-priorityclass-metrics"] = self.check_exists(self.system_cspace_dir, "system-priorityclass-metrics.yaml")
        self.yamls["system-priorityclass-mfs"] = self.check_exists(self.system_cspace_dir, "system-priorityclass-mfs.yaml")
        self.yamls["system-priorityclass-cspaceservices"] = self.check_exists(self.system_cspace_dir, "system-priorityclass-cspaceservices.yaml")
        self.yamls["system-sa-cspace"] = self.check_exists(self.system_cspace_dir, "system-sa-cspace.yaml")
        self.yamls["system-scc-cspace"] = self.check_exists(self.system_cspace_dir, "system-scc-cspace.yaml")
        self.yamls["system-storageclass-hdd"] = self.check_exists(self.system_cspace_dir, "system-storageclass-hdd.yaml")
        self.yamls["system-storageclass-nvme"] = self.check_exists(self.system_cspace_dir, "system-storageclass-nvme.yaml")
        self.yamls["system-storageclass-ssd"] = self.check_exists(self.system_cspace_dir, "system-storageclass-ssd.yaml")
        self.yamls["system-cr-cluster"] = self.check_exists(self.system_cluster_dir, "system-cr-cluster.yaml")
        self.yamls["system-crb-cluster"] = self.check_exists(self.system_cluster_dir, "system-crb-cluster.yaml")
        self.yamls["system-crd-cluster"] = self.check_exists(self.system_cluster_dir, "system-crd-clusteroperator.yaml")
        self.yamls["system-clusteroperator"] = self.check_exists(self.system_cluster_dir, "system-deploy-clusteroperator.yaml")
        self.yamls["system-sa-cluster"] = self.check_exists(self.system_cluster_dir, "system-sa-cluster.yaml")
        self.yamls["system-scc-cluster"] = self.check_exists(self.system_cluster_dir, "system-scc-cluster.yaml")
        self.yamls["configuration-admincli-cm"] = self.check_exists(self.config_clusters_dir, "configuration-admincli-cm.yaml")
        self.yamls["configuration-cldb-cm"] = self.check_exists(self.config_clusters_dir, "configuration-cldb-cm.yaml")
        self.yamls["configuration-clusters-hivemeta-cm"] = self.check_exists(self.config_clusters_dir, "configuration-hivemeta-cm.yaml")
        self.yamls["configuration-clusters-ldapclient-cm"] = self.check_exists(self.config_clusters_dir, "configuration-ldapclient-cm.yaml")
        self.yamls["configuration-clusters-namespace"] = self.check_exists(self.config_clusters_dir, "configuration-namespace.yaml")
        self.yamls["configuration-clusters-sssdsecret"] = self.check_exists(self.config_clusters_dir, "configuration-sssdsecret.yaml")
        self.yamls["configuration-collectd-cm"] = self.check_exists(self.config_clusters_dir, "configuration-collectd-cm.yaml")
        self.yamls["configuration-dag-cm"] = self.check_exists(self.config_clusters_dir, "configuration-dag-cm.yaml")
        self.yamls["configuration-elasticsearch-cm"] = self.check_exists(self.config_clusters_dir, "configuration-elasticsearch-cm.yaml")
        self.yamls["configuration-fluentbit-cm"] = self.check_exists(self.config_clusters_dir, "configuration-fluentbit-cm.yaml")
        self.yamls["configuration-grafana-cm"] = self.check_exists(self.config_clusters_dir, "configuration-grafana-cm.yaml")
        self.yamls["configuration-kafkarest-cm"] = self.check_exists(self.config_clusters_dir, "configuration-kafkarest-cm.yaml")
        self.yamls["configuration-kibana-cm"] = self.check_exists(self.config_clusters_dir, "configuration-kibana-cm.yaml")
        self.yamls["configuration-maprgateway-cm"] = self.check_exists(self.config_clusters_dir, "configuration-maprgateway-cm.yaml")
        self.yamls["configuration-mastgateway-cm"] = self.check_exists(self.config_clusters_dir, "configuration-mastgateway-cm.yaml")
        self.yamls["configuration-mfs-cm"] = self.check_exists(self.config_clusters_dir, "configuration-mfs-cm.yaml")
        self.yamls["configuration-nfs-cm"] = self.check_exists(self.config_clusters_dir, "configuration-nfs-cm.yaml")
        self.yamls["configuration-objectstore-cm"] = self.check_exists(self.config_clusters_dir, "configuration-objectstore-cm.yaml")
        self.yamls["configuration-opentsdb-cm"] = self.check_exists(self.config_clusters_dir, "configuration-opentsdb-cm.yaml")
        self.yamls["configuration-psp-cluster"] = self.check_exists(self.config_clusters_dir, "configuration-psp-cluster.yaml")
        self.yamls["configuration-role-cluster"] = self.check_exists(self.config_clusters_dir, "configuration-role-cluster.yaml")
        self.yamls["configuration-role-cluster-user"] = self.check_exists(self.config_clusters_dir, "configuration-role-cluster-user.yaml")
        self.yamls["configuration-webserver-cm"] = self.check_exists(self.config_clusters_dir, "configuration-webserver-cm.yaml")
        self.yamls["configuration-zookeeper-cm"] = self.check_exists(self.config_clusters_dir, "configuration-zookeeper-cm.yaml")
        self.yamls["bootstrap-cr"] = self.check_exists(self.bootstrap_dir, "bootstrap-cr.yaml")
        self.yamls["bootstrap-crb"] = self.check_exists(self.bootstrap_dir, "bootstrap-crb.yaml")
        self.yamls["bootstrap-nodevalidator"] = self.check_exists(self.bootstrap_dir, "bootstrap-deploy-validator.yaml")
        self.yamls["bootstrap-imagepullsecret"] = self.check_exists(self.bootstrap_dir, "bootstrap-imagepullsecret.yaml")
        self.yamls["bootstrap-namespace"] = self.check_exists(self.bootstrap_dir, "bootstrap-namespace.yaml")
        self.yamls["bootstrap-rb"] = self.check_exists(self.bootstrap_dir, "bootstrap-rb.yaml")
        self.yamls["bootstrap-role"] = self.check_exists(self.bootstrap_dir, "bootstrap-role.yaml")
        self.yamls["bootstrap-sa"] = self.check_exists(self.bootstrap_dir, "bootstrap-sa.yaml")
        self.yamls["bootstrap-scc"] = self.check_exists(self.bootstrap_dir, "bootstrap-scc.yaml")
        #self.yamls["ingress-cr"] = self.check_exists(self.ingress_dir, "ingress-cr.yaml")
        #self.yamls["ingress-crb"] = self.check_exists(self.ingress_dir, "ingress-crb.yaml")
        #self.yamls["ingress-ambassador1"] = self.check_exists(self.ingress_dir, "ingress-deploy-ambassador1.yaml")
        #self.yamls["ingress-ambassador2"] = self.check_exists(self.ingress_dir, "ingress-deploy-ambassador2.yaml")
        #self.yamls["ingress-namespace"] = self.check_exists(self.ingress_dir, "ingress-namespace.yaml")
        #self.yamls["ingress-sa"] = self.check_exists(self.ingress_dir, "ingress-sa.yaml")
        #self.yamls["ingress-scc"] = self.check_exists(self.ingress_dir, "ingress-scc.yaml")
        #self.yamls["ingress-secret-tls"] = self.check_exists(self.ingress_dir, "ingress-secret-tls.yaml")
        #self.yamls["ingress-svc-baremetal-http"] = self.check_exists(self.ingress_dir, "ingress-svc-baremetalhttp.yaml")
        #self.yamls["ingress-svc-baremetal-https"] = self.check_exists(self.ingress_dir, "ingress-svc-baremetalhttps.yaml")
        #self.yamls["ingress-svc-cloud"] = self.check_exists(self.ingress_dir, "ingress-svc-cloud.yaml")
        #self.yamls["kubeflow-cr"] = self.check_exists(self.kubeflow_dir, "kubeflow-cr.yaml")
        #self.yamls["kubeflow-crb"] = self.check_exists(self.kubeflow_dir, "kubeflow-crb.yaml")
        #self.yamls["kubeflow-crd-alertmanager"] = self.check_exists(self.kubeflow_dir, "kubeflow-crd-alertmanager.yaml")
        #self.yamls["kubeflow-crd-argo"] = self.check_exists(self.kubeflow_dir, "kubeflow-crd-argo.yaml")
        #self.yamls["kubeflow-crd-kubeflowoperator"] = self.check_exists(self.kubeflow_dir, "kubeflow-crd-kubeflowoperator.yaml")
        #self.yamls["kubeflow-crd-notebook"] = self.check_exists(self.kubeflow_dir, "kubeflow-crd-notebook.yaml")
        #self.yamls["kubeflow-crd-prometheus"] = self.check_exists(self.kubeflow_dir, "kubeflow-crd-prometheus.yaml")
        #self.yamls["kubeflow-crd-prometheusrule"] = self.check_exists(self.kubeflow_dir, "kubeflow-crd-prometheusrule.yaml")
        #self.yamls["kubeflow-crd-pytorch"] = self.check_exists(self.kubeflow_dir, "kubeflow-crd-pytorch.yaml")
        #self.yamls["kubeflow-crd-seldondeployment"] = self.check_exists(self.kubeflow_dir, "kubeflow-crd-seldondeployment.yaml")
        #self.yamls["kubeflow-crd-servicemonitor"] = self.check_exists(self.kubeflow_dir, "kubeflow-crd-servicemonitor.yaml")
        #self.yamls["kubeflow-crd-tfjob"] = self.check_exists(self.kubeflow_dir, "kubeflow-crd-tfjob.yaml")
        #self.yamls["kubeflow-crd-tfserving"] = self.check_exists(self.kubeflow_dir, "kubeflow-crd-tfserving.yaml")
        #self.yamls["kubeflow-crd-zeppelin"] = self.check_exists(self.kubeflow_dir, "kubeflow-crd-zeppelin.yaml")
        #self.yamls["kubeflow-kubeflowoperator"] = self.check_exists(self.kubeflow_dir, "kubeflow-deploy-kubeflowoperator.yaml")
        #self.yamls["kubeflow-imagepullsecret"] = self.check_exists(self.kubeflow_dir, "kubeflow-imagepullsecret.yaml")
        #self.yamls["kubeflow-namespace"] = self.check_exists(self.kubeflow_dir, "kubeflow-namespace.yaml")
        #self.yamls["kubeflow-sa"] = self.check_exists(self.kubeflow_dir, "kubeflow-sa.yaml")
        #self.yamls["ui-cr"] = self.check_exists(self.ui_dir, "ui-cr.yaml")
        #self.yamls["ui-crb"] = self.check_exists(self.ui_dir, "ui-crb.yaml")
        #self.yamls["ui-pas"] = self.check_exists(self.ui_dir, "ui-deploy-pas.yaml")
        #self.yamls["ui-pas-svc"] = self.check_exists(self.ui_dir, "ui-svc-pas.yaml")
        #self.yamls["ui-imagepullsecret"] = self.check_exists(self.ui_dir, "ui-imagepullsecret.yaml")
        #self.yamls["ui-namespace"] = self.check_exists(self.ui_dir, "ui-namespace.yaml")
        #self.yamls["ui-rb"] = self.check_exists(self.ui_dir, "ui-rb.yaml")
        #self.yamls["ui-role"] = self.check_exists(self.ui_dir, "ui-role.yaml")
        #self.yamls["ui-sa"] = self.check_exists(self.ui_dir, "ui-sa.yaml")
        #self.yamls["ui-scc"] = self.check_exists(self.ui_dir, "ui-scc.yaml")
    def check_ready(self):
        print(os.linesep)
        Log.info("We are now ready to install the basic components for running MapR in Kubernetes...", True)
        ready = self._prompts.prompt_boolean("Continue with installation?", True, key_name="CONTINUE_INSTALL")
        if not ready:
            Log.error("User not ready to install system components")
            return False
        return True

    def is_openshift_connected(self):
        """
        This command runs the `oc status` and return if Openshift is connected
        :return: True/False
        """

        cmd = "oc status"
        response = self._run_and_return_response(cmd, False)
        if response is None:
            return False
        elif "warnings" in response.lower():
            return False

        return True

    def get_yaml(self, key):
        # TODO: Need to load up a dict of keys and values to be replaced
        yaml_file = self.yamls.get(key)
        if yaml_file is None:
            raise NotFoundException("The key '{0}' does not have an entry in the yamls dictonary".format(key))

        yaml_file, changed = FileUtils.replace_yaml_value(yaml_file, dict())

        return yaml_file, changed

    def delete_temp_yaml(self, yaml_file):
        pass

    @staticmethod
    def run_get(cmd, print_error=True):
        cmd = "{0} {1}".format(K8SOperations.KUBECTL_GET, cmd)
        response, status = OSCommand.run2(cmd)
        if status != 0:
            if print_error:
                Log.error("Could not run {0}: {1}:{2}".format(cmd, str(status), response))
        return response, status

    @staticmethod
    def run_label_mapr_node(node_name, label, is_mapr_node, print_error=True):
        cmd = K8SOperations.KUBECTL_LABEL_NODE.format(node_name, label, str(is_mapr_node).lower())
        response, status = OSCommand.run2(cmd)
        if status != 0:
            if print_error:
                Log.error("Could not run {0}: {1}:{2}".format(cmd, str(status), response))
        return response, status

    def run_oc_apply(self, key):
        yaml_file, changed = self.get_yaml(key)
        if yaml_file is None:
            raise NotFoundException("The key '{0}' does not have an entry in the yamls dictonary".format(key))

        cmd = "{0} {1}".format(K8SOperations.OC_APPLY, yaml_file)
        result = self._run(cmd)
        if changed:
            self.delete_temp_yaml(yaml_file)

        return result

    def run_oc_delete(self, key):
        yaml_file, changed = self.get_yaml(key)
        if yaml_file is None:
            raise NotFoundException("The key '{0}' does not have an entry in the yamls dictonary".format(key))

        cmd = "{0} {1}".format(K8SOperations.OC_DELETE, yaml_file)
        result = self._run(cmd)
        if changed:
            self.delete_temp_yaml(yaml_file)

        return result

    def run_kubectl_apply(self, key):
        yaml_file, changed = self.get_yaml(key)
        cmd = "{0} {1}".format(K8SOperations.KUBECTL_APPLY, yaml_file)
        result = self._run(cmd)
        if changed:
            self.delete_temp_yaml(yaml_file)

        return result

    def run_kubectl_get(self, get_str):
        cmd = "{0} {1}".format(K8SOperations.KUBECTL_GET, get_str)
        result = self._run(cmd)

        return result

    def run_kubectl_delete(self, key, ignore_not_found=False):
        yaml_file, changed = self.get_yaml(key)
        if yaml_file is None:
            raise NotFoundException("The key '{0}' does not have an entry in the yamls dictonary".format(key))

        if ignore_not_found:
            ignore_not_found_option = "--ignore-not-found"
            cmd = "{0} {1} {2}".format(K8SOperations.KUBECTL_DELETE, yaml_file, ignore_not_found_option)
        else:
            cmd = "{0} {1}".format(K8SOperations.KUBECTL_DELETE, yaml_file)
        result = self._run(cmd)
        if changed:
            self.delete_temp_yaml(yaml_file)

        return result

    def run_kubectl_create_secret(self):
        cmd = 'kubectl create secret generic system-user-secrets -n mapr-system ' \
              '--from-literal="MAPR_USER=' + self.username + '" ' \
              '--from-literal="MAPR_PASSWORD=' + self.password + '" ' \
              '--from-literal="MAPR_GROUP=' + self.groupname + '" ' \
              '--from-literal="MAPR_UID=' + str(self.userid) + '" ' \
              '--from-literal="MAPR_GID=' + str(self.groupid) + '" ' \
              '--from-literal="MYSQL_USER=' + self.mysql_user + '" ' \
              '--from-literal="MYSQL_PASSWORD=' + self.mysql_pass + '" ' \
              '--from-literal="LDAPADMIN_USER=' + self.ldapadmin_user + '" ' \
              '--from-literal="LDAPADMIN_PASSWORD=' + self.ldapadmin_pass + '" ' \
              '--from-literal="LDAPBIND_USER=' + self.ldapbind_user + '" ' \
              '--from-literal="LDAPBIND_PASSWORD=' + self.ldapbind_pass + '"'
        return self._run(cmd)

    def run_kubectl_delete_secret(self):
        cmd = 'kubectl delete secret system-user-secrets -n mapr-system '
        return self._run(cmd)

    def bootstrap_openshift_policy_add(self):
        cmd = 'oc adm policy add-cluster-role-to-user maprbootstrap-cr ' \
              ' system:serviceaccount:mapr-bootstrap:maprbootstrap-sa'
        self._run(cmd)

    def bootstrap_openshift_policy_remove(self):
        cmd = 'oc adm policy remove-cluster-role-from-user maprbootstrap-cr ' \
              ' system:serviceaccount:mapr-bootstrap:maprbootstrap-sa'
        self._run(cmd)

    def csi_openshift_policy_add(self):
        cmd = 'oc adm policy add-cluster-role-to-user csi-nodeplugin-cr ' \
              ' system:serviceaccount:mapr-csi:csi-nodeplugin-sa'
        self._run(cmd)

        cmd = 'oc adm policy add-cluster-role-to-user csi-attacher-cr ' \
              ' system:serviceaccount:mapr-csi:csi-provisioner-sa'
        self._run(cmd)

        cmd = 'oc adm policy add-cluster-role-to-user csi-provisioner-cr ' \
              ' system:serviceaccount:mapr-csi:csi-provisioner-sa'
        self._run(cmd)

    def csi_openshift_policy_remove(self):
        cmd = 'oc adm policy remove-cluster-role-from-user csi-nodeplugin-cr ' \
              ' system:serviceaccount:mapr-csi:csi-nodeplugin-sa'
        self._run(cmd)

        cmd = 'oc adm policy remove-cluster-role-from-user csi-attacher-cr ' \
              ' system:serviceaccount:mapr-csi:csi-provisioner-sa'
        self._run(cmd)

        cmd = 'oc adm policy remove-cluster-role-from-user csi-provisioner-cr ' \
              ' system:serviceaccount:mapr-csi:csi-provisioner-sa'
        self._run(cmd)

    def drill_openshift_policy_add(self):
        cmd = 'oc adm policy add-cluster-role-to-user drilloperator-cr ' \
              ' system:serviceaccount:drill-operator:drilloperator-sa'
        self._run(cmd)

    def drill_openshift_policy_remove(self):
        cmd = 'oc adm policy remove-cluster-role-from-user drilloperator-cr ' \
              ' system:serviceaccount:drill-operator:drilloperator-sa'
        self._run(cmd)

    def ingress_openshift_policy_add(self):
        cmd = 'oc adm policy add-cluster-role-to-user ingress-cr ' \
              ' system:serviceaccount:mapr-ingress:ingress-sa'
        self._run(cmd)

    def ingress_openshift_policy_remove(self):
        cmd = 'oc adm policy remove-cluster-role-from-user ingress-cr ' \
              ' system:serviceaccount:mapr-ingress:ingress-sa'
        self._run(cmd)

    def spark_openshift_policy_add(self):
        cmd = 'oc adm policy add-cluster-role-to-user sparkoperator-cr ' \
              ' system:serviceaccount:spark-operator:sparkoperator-sa'
        self._run(cmd)

    def spark_openshift_policy_remove(self):
        cmd = 'oc adm policy remove-cluster-role-from-user sparkoperator-cr ' \
              ' system:serviceaccount:spark-operator:sparkoperator-sa'
        self._run(cmd)

    def cluster_openshift_policy_add(self):
        cmd = 'oc adm policy add-cluster-role-to-user clusteroperator-cr ' \
              ' system:serviceaccount:mapr-system:clusteroperator-sa'
        self._run(cmd)

    def cluster_openshift_policy_remove(self):
        cmd = 'oc adm policy remove-cluster-role-from-user clusteroperator-cr ' \
              ' system:serviceaccount:mapr-system:clusteroperator-sa'
        self._run(cmd)

    def cspace_openshift_policy_add(self):
        cmd = 'oc adm policy add-cluster-role-to-user cspaceoperator-cr ' \
              ' system:serviceaccount:mapr-system:cspaceoperator-sa'
        self._run(cmd)

    def cspace_openshift_policy_remove(self):
        cmd = 'oc adm policy remove-cluster-role-from-user cspaceoperator-cr ' \
              ' system:serviceaccount:mapr-system:cspaceoperator-sa'
        self._run(cmd)

    def ui_openshift_policy_add(self):
        cmd = 'oc adm policy add-cluster-role-to-user maprui-cr ' \
              ' system:serviceaccount:mapr-ui:maprui-sa'
        self._run(cmd)

    def ui_openshift_policy_remove(self):
        cmd = 'oc adm policy remove-cluster-role-from-user maprui-cr ' \
              ' system:serviceaccount:mapr-ui:maprui-sa'
        self._run(cmd)

    def create_user_secret(self):
        Log.info(os.linesep + "We need to create a secret containing sensitive user information...", True)
        Log.info(os.linesep + "MapR System User is: {0}".format(Constants.USERNAME))
        Log.info(os.linesep + "MapR System User", True)
        Log.info("The MapR system user is the user that is used to start containers in the cluster.", True)
        Log.info("A MapR service ticket is generated for this user on cluster creation", True)

        self.password = self._prompts.prompt("MapR systemuser password", self.password, True, key_name="MAPR_USER")
        # self.groupname = self._prompts.prompt("MapR systemuser group", self.groupname, key_name="MAPR_GROUP")
        # Log.debug("User specified MapR system user groupname: {0}".format(self.groupname))
        # self.userid = self._prompts.prompt_integer("MapR systemuser uid", self.userid, 0, key_name="MAPR_UID")
        # Log.debug("User specified MapR system user userid: {0}".format(self.userid))
        # self.groupid = self._prompts.prompt_integer("MapR systemuser groupid", self.groupid, 0, key_name="MAPR_GID")
        # Log.debug("User specified MapR system group groupid: {0}".format(self.groupid))

        Log.info(os.linesep + "LDAP Admin User", True)
        Log.info("The LDAP admin user is used in the operation of an example OpenLDAP server.", True)
        Log.info("This info will be ignored if you do not use the example LDAP server", True)
        self.ldapadmin_pass = self._prompts.prompt("LDAP admin password", self.ldapadmin_pass, True, key_name="LDAP_PASSWORD")

        Log.info(os.linesep + "LDAP Bind User", True)
        Log.info("The LDAP bind user is used by SSSD to connect to your LDAP server to satisfy PAM requests.", True)
        self.ldapbind_pass = self._prompts.prompt("LDAP bind password", self.ldapbind_pass, True, key_name="LDAP_BIND_PASSWORD")

    def install_bootstrap_components(self):
        Log.info(os.linesep + "Creating Bootstrap Namespace...", True)
        if self.run_kubectl_apply("bootstrap-namespace"):
            Log.info("Created Bootstrap Namespace.")

        Log.info(os.linesep + "Creating Bootstrap Service Account...", True)
        if self.run_kubectl_apply("bootstrap-sa"):
            Log.info("Created Bootstrap Service Account.")

        Log.info(os.linesep + "Creating Bootstrap Cluster Role...", True)
        if self.run_kubectl_apply("bootstrap-cr"):
            Log.info("Created Bootstrap Cluster Role.")

        Log.info(os.linesep + "Creating Bootstrap Role...", True)
        if self.run_kubectl_apply("bootstrap-role"):
            Log.info("Created Bootstrap Role.")

        Log.info(os.linesep + "Creating Bootstrap Cluster Role Binding...", True)
        if self.run_kubectl_apply("bootstrap-crb"):
            Log.info("Created Bootstrap Cluster Role Binding.")

        Log.info(os.linesep + "Creating Bootstrap Role Binding...", True)
        if self.run_kubectl_apply("bootstrap-rb"):
            Log.info("Created Bootstrap Role Binding.")

        if self.is_openshift:
            Log.info(os.linesep + "Creating Bootstrap SCC...", True)
            if self.run_oc_apply("bootstrap-scc"):
                Log.info("Created SCC policy for mapr-bootstrap on Openshift", True)
                self.bootstrap_openshift_policy_add()
                Log.info("Created Bootstrap SCC.")

        Log.info(os.linesep + "Creating secret to pull images for Bootstrap...", True)
        if self.run_kubectl_apply("bootstrap-imagepullsecret"):
            Log.info("Created Bootstrap Pull Secret.")

        Log.info(os.linesep + "Creating Bootstrap Node Validator...", True)
        if self.run_kubectl_apply("bootstrap-nodevalidator"):
            Log.info("Created Bootstrap Node Validator.")

    def uninstall_bootstrap_components(self):
        Log.info(os.linesep + "Deleting Bootstrap Node Validator...", True)
        if self.run_kubectl_delete("bootstrap-nodevalidator"):
            Log.info("Deleted Bootstrap Node Validator.")

        Log.info(os.linesep + "Deleting secret to pull images for Bootstrap...", True)
        if self.run_kubectl_delete("bootstrap-imagepullsecret"):
            Log.info("Deleted Bootstrap Pull Secret.")

        if self.is_openshift:
            Log.info(os.linesep + "Deleting Bootstrap SCC...", True)
            self.bootstrap_openshift_policy_remove()
            if self.run_oc_delete("bootstrap-scc"):
                Log.info("Deleted SCC policy for mapr-bootstrap on Openshift.", True)

        Log.info(os.linesep + "Deleting Bootstrap Role Binding...", True)
        if self.run_kubectl_delete("bootstrap-rb"):
            Log.info("Deleted Bootstrap Role Binding.")

        Log.info(os.linesep + "Deleting Bootstrap Cluster Role Binding...", True)
        if self.run_kubectl_delete("bootstrap-crb", True):
            Log.info("Deleted Bootstrap Cluster Role Binding.")

        Log.info(os.linesep + "Deleting Bootstrap Role...", True)
        if self.run_kubectl_delete("bootstrap-role"):
            Log.info("Deleted Bootstrap Role.")

        Log.info(os.linesep + "Deleting Bootstrap Cluster Role...", True)
        if self.run_kubectl_delete("bootstrap-cr"):
            Log.info("Deleted Bootstrap Cluster Role.")

        Log.info(os.linesep + "Deleting Bootstrap Service Account...", True)
        if self.run_kubectl_delete("bootstrap-sa"):
            Log.info("Deleted Bootstrap Service Account.")

        Log.info(os.linesep + "Deleting Bootstrap Namespace...", True)
        if self.run_kubectl_delete("bootstrap-namespace"):
            Log.info("Deleted Bootstrap Namespace.")

    def install_cspaces_configuration_components(self):
        Log.info(os.linesep + "Creating Configuration Namespace...", True)
        if self.run_kubectl_apply("configuration-namespace"):
            Log.info("Created Configuration Namespace.")

        Log.info(os.linesep + "Creating Configuration Hive Metastore CM...", True)
        if self.run_kubectl_apply("configuration-hivemeta-cm"):
            Log.info("Created Configuration Hive Metastore CM.")

        Log.info(os.linesep + "Creating Configuration LDAP Client CM...", True)
        if self.run_kubectl_apply("configuration-ldapclient-cm"):
            Log.info("Created Configuration LDAP Client CM.")

        Log.info(os.linesep + "Creating Configuration SSSD Secret...", True)
        if self.run_kubectl_apply("configuration-sssdsecret"):
            Log.info("Created Configuration SSSD Secret.")

        Log.info(os.linesep + "Creating Configuration Spark History CM...", True)
        if self.run_kubectl_apply("configuration-sparkhistory-cm"):
            Log.info("Created Configuration Spark History CM.")

        Log.info(os.linesep + "Creating Configuration CSpace Terminal CM...", True)
        if self.run_kubectl_apply("configuration-cspaceterminal-cm"):
            Log.info("Created Configuration CSpace Terminal CM.")

        Log.info(os.linesep + "Creating CSpace Pod Security Policy...", True)
        if self.run_kubectl_apply("configuration-psp-cspace"):
            Log.info("Created CSpace Pod Security Policy.")

        Log.info(os.linesep + "Creating Configuration CSpace Role...", True)
        if self.run_kubectl_apply("configuration-role-cspace"):
            Log.info("Created Configuration CSpace Role.")

        Log.info(os.linesep + "Creating Configuration CSpace Terminal Role...", True)
        if self.run_kubectl_apply("configuration-role-cspace-terminal"):
            Log.info("Created Configuration CSpace Terminal Role.")

        Log.info(os.linesep + "Creating Configuration CSpace User Role...", True)
        if self.run_kubectl_apply("configuration-role-cspace-user"):
            Log.info("Created Configuration CSpace User Role.")

    def uninstall_cspaces_configuration_components(self):
        Log.info(os.linesep + "Deleting Configuration SSSD Secret...", True)
        if self.run_kubectl_delete("configuration-sssdsecret"):
            Log.info("Deleted Configuration SSSD Secret.")

        Log.info(os.linesep + "Deleting Configuration LDAP Client CM...", True)
        if self.run_kubectl_delete("configuration-ldapclient-cm"):
            Log.info("Deleted Configuration LDAP Client CM.")

        Log.info(os.linesep + "Deleting Configuration Hive Meta CM...", True)
        if self.run_kubectl_delete("configuration-hivemeta-cm"):
            Log.info("Deleted Configuration Hive Meta CM.")

        Log.info(os.linesep + "Deleting CSpace Pod Security Policy...", True)
        if self.run_kubectl_delete("configuration-psp-cspace"):
            Log.info("Deleted CSpace Pod Security Policy.")

        Log.info(os.linesep + "Deleting Configuration CSpace Role...", True)
        if self.run_kubectl_delete("configuration-role-cspace"):
            Log.info("Deleted Configuration CSpace Role.")

        Log.info(os.linesep + "Deleting Configuration CSpace Terminal Role...", True)
        if self.run_kubectl_delete("configuration-role-cspace-terminal"):
            Log.info("Deleted Configuration CSpace Terminal Role.")

        Log.info(os.linesep + "Deleting Configuration CSpace User Role...", True)
        if self.run_kubectl_delete("configuration-role-cspace-user"):
            Log.info("Deleted Configuration CSpace User Role.")

        Log.info(os.linesep + "Deleting Configuration Spark History CM...", True)
        if self.run_kubectl_delete("configuration-sparkhistory-cm"):
            Log.info("Deleted Configuration Spark History CM.")

        Log.info(os.linesep + "Deleting Configuration CSpace Terminal CM...", True)
        if self.run_kubectl_delete("configuration-cspaceterminal-cm"):
            Log.info("Deleted Configuration CSpace Terminal CM.")

        Log.info(os.linesep + "Deleting Configuration Namespace...", True)
        if self.run_kubectl_delete("configuration-namespace"):
            Log.info("Deleted Configuration Namespace.")

    def install_clusters_configuration_components(self):
        Log.info(os.linesep + "Creating Configuration Namespace...", True)
        if self.run_kubectl_apply("configuration-clusters-namespace"):
            Log.info("Created Configuration Namespace.")

        Log.info(os.linesep + "Creating Configuration AdminCLI CM...", True)
        if self.run_kubectl_apply("configuration-admincli-cm"):
            Log.info("Created Configuration AdminCLI CM.")

        Log.info(os.linesep + "Creating Configuration CLDB CM...", True)
        if self.run_kubectl_apply("configuration-cldb-cm"):
            Log.info("Created Configuration CLDB CM.")

        Log.info(os.linesep + "Creating Configuration Collectd CM...", True)
        if self.run_kubectl_apply("configuration-collectd-cm"):
            Log.info("Created Configuration Collectd CM.")

        Log.info(os.linesep + "Creating Configuration Data Access Gateway CM...", True)
        if self.run_kubectl_apply("configuration-dag-cm"):
            Log.info("Created Configuration Data Access Gateway CM.")

        Log.info(os.linesep + "Creating Configuration Elastic Search CM...", True)
        if self.run_kubectl_apply("configuration-elasticsearch-cm"):
            Log.info("Created Configuration Elastic Search CM.")

        Log.info(os.linesep + "Creating Configuration Fluentbit CM...", True)
        if self.run_kubectl_apply("configuration-fluentbit-cm"):
            Log.info("Created Configuration Fluentbit CM.")

        Log.info(os.linesep + "Creating Configuration Grafana CM...", True)
        if self.run_kubectl_apply("configuration-grafana-cm"):
            Log.info("Created Configuration Grafana CM.")

        Log.info(os.linesep + "Creating Configuration Kafka Rest Gateway CM...", True)
        if self.run_kubectl_apply("configuration-kafkarest-cm"):
            Log.info("Created Configuration Kafka Rest Gateway CM.")

        Log.info(os.linesep + "Creating Configuration Kibana CM...", True)
        if self.run_kubectl_apply("configuration-kibana-cm"):
            Log.info("Created Configuration Kibana CM.")

        Log.info(os.linesep + "Creating Configuration MapR Gateway CM...", True)
        if self.run_kubectl_apply("configuration-maprgateway-cm"):
            Log.info("Created Configuration Mapr Gateway CM.")

        Log.info(os.linesep + "Creating Configuration Mast Gateway CM...", True)
        if self.run_kubectl_apply("configuration-mastgateway-cm"):
            Log.info("Created Configuration Mast Gateway CM.")

        Log.info(os.linesep + "Creating Configuration MFS CM...", True)
        if self.run_kubectl_apply("configuration-mfs-cm"):
            Log.info("Created Configuration MFS CM.")

        Log.info(os.linesep + "Creating Configuration NFS Server CM...", True)
        if self.run_kubectl_apply("configuration-nfs-cm"):
            Log.info("Created Configuration NFS Server CM.")

        Log.info(os.linesep + "Creating Configuration Objectstore CM...", True)
        if self.run_kubectl_apply("configuration-objectstore-cm"):
            Log.info("Created Configuration Objectstore CM.")

        Log.info(os.linesep + "Creating Configuration OpenTSDB CM...", True)
        if self.run_kubectl_apply("configuration-opentsdb-cm"):
            Log.info("Created Configuration OpenTSDB CM.")

        Log.info(os.linesep + "Creating Configuration Webserver CM...", True)
        if self.run_kubectl_apply("configuration-webserver-cm"):
            Log.info("Created Configuration Webserver CM.")

        Log.info(os.linesep + "Creating Configuration Zookeeper CM...", True)
        if self.run_kubectl_apply("configuration-zookeeper-cm"):
            Log.info("Created Configuration Zookeeper CM.")

        Log.info(os.linesep + "Creating Configuration Cluster Role...", True)
        if self.run_kubectl_apply("configuration-role-cluster"):
            Log.info("Created Configuration Cluster Role.")

        Log.info(os.linesep + "Creating Configuration Cluster User Role...", True)
        if self.run_kubectl_apply("configuration-role-cluster-user"):
            Log.info("Created Configuration Cluster User Role.")

        Log.info(os.linesep + "Creating Cluster Pod Security Policy...", True)
        if self.run_kubectl_apply("configuration-psp-cluster"):
            Log.info("Created Cluster Pod Security Policy.")

        Log.info(os.linesep + "Creating Configuration Hive Metastore CM...", True)
        if self.run_kubectl_apply("configuration-clusters-hivemeta-cm"):
            Log.info("Created Configuration Hive Metastore CM.")

        Log.info(os.linesep + "Creating Configuration LDAP Client CM...", True)
        if self.run_kubectl_apply("configuration-clusters-ldapclient-cm"):
            Log.info("Created Configuration LDAP Client CM.")

        Log.info(os.linesep + "Creating Configuration SSSD Secret...", True)
        if self.run_kubectl_apply("configuration-clusters-sssdsecret"):
            Log.info("Created Configuration SSSD Secret.")

    def uninstall_clusters_configuration_components(self):
        Log.info(os.linesep + "Deleting Configuration SSSD Secret...", True)
        if self.run_kubectl_delete("configuration-clusters-sssdsecret"):
            Log.info("Deleted Configuration SSSD Secret.")

        Log.info(os.linesep + "Deleting Configuration LDAP Client CM...", True)
        if self.run_kubectl_delete("configuration-clusters-ldapclient-cm"):
            Log.info("Deleted Configuration LDAP Client CM.")

        Log.info(os.linesep + "Deleting Configuration Hive Meta CM...", True)
        if self.run_kubectl_delete("configuration-clusters-hivemeta-cm"):
            Log.info("Deleted Configuration Hive Meta CM.")

        Log.info(os.linesep + "Deleting Cluster Pod Security Policy...", True)
        if self.run_kubectl_delete("configuration-psp-cluster"):
            Log.info("Deleted Cluster Pod Security Policy.")

        Log.info(os.linesep + "Deleting Configuration Cluster Role...", True)
        if self.run_kubectl_delete("configuration-role-cluster"):
            Log.info("Deleted Configuration Cluster Role.")

        Log.info(os.linesep + "Deleting Configuration AdminCLI CM...", True)
        if self.run_kubectl_delete("configuration-admincli-cm"):
            Log.info("Deleted Configuration AdminCLI CM.")

        Log.info(os.linesep + "Deleting Configuration CLDB CM...", True)
        if self.run_kubectl_delete("configuration-cldb-cm"):
            Log.info("Deleted Configuration CLDB CM.")

        Log.info(os.linesep + "Deleting Configuration Collectd CM...", True)
        if self.run_kubectl_delete("configuration-collectd-cm"):
            Log.info("Deleted Configuration Collectd CM.")

        Log.info(os.linesep + "Deleting Configuration Data Access Gateway CM...", True)
        if self.run_kubectl_delete("configuration-dag-cm"):
            Log.info("Deleted Configuration Data Access Gateway CM.")

        Log.info(os.linesep + "Deleting Configuration Elastic Search CM...", True)
        if self.run_kubectl_delete("configuration-elasticsearch-cm"):
            Log.info("Deleted Configuration Elastic Search CM.")

        Log.info(os.linesep + "Deleting Configuration Fluentbit CM...", True)
        if self.run_kubectl_delete("configuration-fluentbit-cm"):
            Log.info("Deleted Configuration Fluentbit CM.")

        Log.info(os.linesep + "Deleting Configuration Grafana CM...", True)
        if self.run_kubectl_delete("configuration-grafana-cm"):
            Log.info("Deleted Configuration Grafana CM.")

        Log.info(os.linesep + "Deleting Configuration Kafka Rest CM...", True)
        if self.run_kubectl_delete("configuration-kafkarest-cm"):
            Log.info("Deleted Configuration Kafka Rest CM.")

        Log.info(os.linesep + "Deleting Configuration Kibana CM...", True)
        if self.run_kubectl_delete("configuration-kibana-cm"):
            Log.info("Deleted Configuration Kibana CM.")

        Log.info(os.linesep + "Deleting Configuration MapR Gateway CM...", True)
        if self.run_kubectl_delete("configuration-maprgateway-cm"):
            Log.info("Deleted Configuration MapR Gateway CM.")

        Log.info(os.linesep + "Deleting Configuration Mast Gateway CM...", True)
        if self.run_kubectl_delete("configuration-mastgateway-cm"):
            Log.info("Deleted Configuration Mast Gateway CM.")

        Log.info(os.linesep + "Deleting Configuration MFS CM...", True)
        if self.run_kubectl_delete("configuration-mfs-cm"):
            Log.info("Deleted Configuration MFS CM.")

        Log.info(os.linesep + "Deleting Configuration NFS CM...", True)
        if self.run_kubectl_delete("configuration-nfs-cm"):
            Log.info("Deleted Configuration NFS CM.")

        Log.info(os.linesep + "Deleting Configuration Objectstore CM...", True)
        if self.run_kubectl_delete("configuration-objectstore-cm"):
            Log.info("Deleted Configuration Objectstore CM.")

        Log.info(os.linesep + "Deleting Configuration OpenTSDB CM...", True)
        if self.run_kubectl_delete("configuration-opentsdb-cm"):
            Log.info("Deleted Configuration OpenTSDB CM.")

        Log.info(os.linesep + "Deleting Configuration Webserver CM...", True)
        if self.run_kubectl_delete("configuration-webserver-cm"):
            Log.info("Deleted Configuration Webserver CM.")

        Log.info(os.linesep + "Deleting Configuration Zookeeper CM...", True)
        if self.run_kubectl_delete("configuration-zookeeper-cm"):
            Log.info("Deleted Configuration Zookeeper CM.")

        Log.info(os.linesep + "Deleting Configuration Namespace...", True)
        if self.run_kubectl_delete("configuration-clusters-namespace"):
            Log.info("Deleted Configuration Namespace.")

    def install_csi_components(self):
        Log.info(os.linesep + "Creating CSI Namespace...", True)
        if self.run_kubectl_apply("csi-namespace"):
            Log.info("Created Bootstrap Namespace.")

        Log.info(os.linesep + "Creating CSI Node Plugin Service Account...", True)
        if self.run_kubectl_apply("csi-nodeplugin-sa"):
            Log.info("Created CSI Node Plugin Service Account.")

        Log.info(os.linesep + "Creating CSI Provisioner Service Account...", True)
        if self.run_kubectl_apply("csi-provisioner-sa"):
            Log.info("Created CSI Provisioner Service Account.")

        Log.info(os.linesep + "Creating CSI Attacher Cluster Role...", True)
        if self.run_kubectl_apply("csi-attacher-cr"):
            Log.info("Created CSI Attacher Cluster Role.")

        Log.info(os.linesep + "Creating CSI Attacher Cluster Role Binding...", True)
        if self.run_kubectl_apply("csi-attacher-crb"):
            Log.info("Created CSI Attacher Cluster Role Binding.")

        Log.info(os.linesep + "Creating CSI Node Plugin Cluster Role...", True)
        if self.run_kubectl_apply("csi-nodeplugin-cr"):
            Log.info("Created CSI Node Plugin Cluster Role.")

        Log.info(os.linesep + "Creating CSI Node Plugin Cluster Role Binding...", True)
        if self.run_kubectl_apply("csi-nodeplugin-crb"):
            Log.info("Created CSI Node Plugin Cluster Role Binding.")

        Log.info(os.linesep + "Creating CSI Provisioner Cluster Role...", True)
        if self.run_kubectl_apply("csi-provisioner-cr"):
            Log.info("Created CSI Provisioner Cluster Role.")

        Log.info(os.linesep + "Creating CSI Provisioner Cluster Role Binding...", True)
        if self.run_kubectl_apply("csi-provisioner-crb"):
            Log.info("Created CSI Provisioner Cluster Role Binding.")

        if self.is_openshift:
            Log.info(os.linesep + "Creating CSI SCC...", True)
            if self.run_oc_apply("csi-scc"):
                Log.info("Created SCC policy for mapr-csi on Openshift", True)
                self.csi_openshift_policy_add()
                Log.info("Created CSI SCC.")

        Log.info(os.linesep + "Creating secret to pull images for CSI...", True)
        if self.run_kubectl_apply("csi-imagepullsecret"):
            Log.info("Created CSI Pull Secret.")

        Log.info(os.linesep + "Creating CSI NodePlugin DaemonSet...", True)
        if self.is_openshift:
            if self.run_kubectl_apply("csi-openshift-nodeplugin"):
                Log.info("Created CSI NodePlugin DaemonSet on Openshift.")
        else:
            if self.run_kubectl_apply("csi-nodeplugin"):
                Log.info("Created CSI NodePlugin DaemonSet.")

        Log.info(os.linesep + "Creating CSI Provisioner StatefulSet...", True)
        if self.is_openshift:
            if self.run_kubectl_apply("csi-openshift-provisioner"):
                Log.info("Created CSI Provisioner StatefulSet on Openshift.")
        else:
            if self.run_kubectl_apply("csi-provisioner"):
                Log.info("Created CSI Provisioner StatefulSet.")

    def uninstall_csi_components(self):
        Log.info(os.linesep + "Deleting CSI NodePlugin DaemonSet...", True)
        if self.run_kubectl_delete("csi-nodeplugin"):
            Log.info("Deleted CSI NodePlugin DaemonSet.")

        Log.info(os.linesep + "Deleting CSI Provisioner StatefulSet...", True)
        if self.run_kubectl_delete("csi-provisioner"):
            Log.info("Deleted CSI Provisioner StatefulSet.")

        Log.info(os.linesep + "Deleting secret to pull images for CSI...", True)
        if self.run_kubectl_delete("csi-imagepullsecret"):
            Log.info("Deleted CSI Pull Secret.")

        if self.is_openshift:
            Log.info(os.linesep + "Deleting CSI SCC...", True)
            self.csi_openshift_policy_remove()
            if self.run_oc_delete("csi-scc"):
                Log.info("Deleted CSI policy for mapr-bootstrap on Openshift.", True)

        Log.info(os.linesep + "Deleting CSI Node Plugin Cluster Role Binding...", True)
        if self.run_kubectl_delete("csi-nodeplugin-crb", True):
            Log.info("Deleted CSI Node Plugin Cluster Role Binding.")

        Log.info(os.linesep + "Deleting CSI Node Plugin Cluster Role...", True)
        if self.run_kubectl_delete("csi-nodeplugin-cr"):
            Log.info("Deleted CSI Node Plugin Cluster Role.")

        Log.info(os.linesep + "Deleting CSI Provisioner Cluster Role Binding...", True)
        if self.run_kubectl_delete("csi-provisioner-crb", True):
            Log.info("Deleted CSI Provisioner Cluster Role Binding.")

        Log.info(os.linesep + "Deleting CSI Provisioner Cluster Role...", True)
        if self.run_kubectl_delete("csi-provisioner-cr"):
            Log.info("Deleted CSI Provisioner Cluster Role.")

        Log.info(os.linesep + "Deleting CSI Attacher Cluster Role Binding...", True)
        if self.run_kubectl_delete("csi-attacher-crb", True):
            Log.info("Deleted CSI Cluster Role Binding.")

        Log.info(os.linesep + "Deleting CSI Attacher Cluster Role...", True)
        if self.run_kubectl_delete("csi-attacher-cr"):
            Log.info("Deleted CSI Cluster Role.")

        Log.info(os.linesep + "Deleting CSI Provisioner Service Account...", True)
        if self.run_kubectl_delete("csi-provisioner-sa"):
            Log.info("Deleted CSI Provisioner Service Account.")

        Log.info(os.linesep + "Deleting CSI Node Plugin Service Account...", True)
        if self.run_kubectl_delete("csi-nodeplugin-sa"):
            Log.info("Deleted CSI Service Account.")

        Log.info(os.linesep + "Deleting CSI Namespace...", True)
        if self.run_kubectl_delete("csi-namespace"):
            Log.info("Deleted CSI Namespace.")

    def install_drill_components(self):
        Log.info(os.linesep + "Creating Drill Namespace...", True)
        if self.run_kubectl_apply("drill-namespace"):
            Log.info("Created Drill Namespace.")

        Log.info(os.linesep + "Creating Drill Service Account...", True)
        if self.run_kubectl_apply("drill-sa"):
            Log.info("Created Drill Service Account.")

        Log.info(os.linesep + "Creating Drill Cluster Role...", True)
        if self.run_kubectl_apply("drill-cr"):
            Log.info("Created Drill Cluster Role.")

        Log.info(os.linesep + "Creating Drill Role...", True)
        if self.run_kubectl_apply("drill-role"):
            Log.info("Created Drill Role.")

        Log.info(os.linesep + "Creating Drill Cluster Role Binding...", True)
        if self.run_kubectl_apply("drill-crb"):
            Log.info("Created Drill Cluster Role Binding.")

        Log.info(os.linesep + "Creating Drill Role Binding...", True)
        if self.run_kubectl_apply("drill-rb"):
            Log.info("Created Drill Role Binding.")

        if self.is_openshift:
            Log.info(os.linesep + "Creating Drill SCC...", True)
            if self.run_oc_apply("drill-scc"):
                Log.info("Created SCC policy for mapr-drill on Openshift", True)
                self.drill_openshift_policy_add()
                Log.info("Created Drill SCC.")

        Log.info(os.linesep + "Creating secret to pull images for Drill...", True)
        if self.run_kubectl_apply("drill-imagepullsecret"):
            Log.info("Created Drill Pull Secret.")

        Log.info(os.linesep + "Creating Drill CRD...", True)
        if self.run_kubectl_apply("drill-crd"):
            Log.info("Created Drill CRD.")

        Log.info(os.linesep + "Creating Drill Operator...", True)
        if self.run_kubectl_apply("drill-drilloperator"):
            Log.info("Created Drill Operator.")

    def uninstall_drill_components(self):
        Log.info(os.linesep + "Deleting Drill Operator...", True)
        if self.run_kubectl_delete("drill-drilloperator"):
            Log.info("Deleted Drill Operator.")

        Log.info(os.linesep + "Deleting Drill CRD...", True)
        if self.run_kubectl_delete("drill-crd"):
            Log.info("Deleted Drill CRD.")

        Log.info(os.linesep + "Deleting secret to pull images for Drill...", True)
        if self.run_kubectl_delete("drill-imagepullsecret"):
            Log.info("Deleted Drill Pull Secret.")

        if self.is_openshift:
            Log.info(os.linesep + "Deleting Drill SCC...", True)
            self.drill_openshift_policy_remove()
            if self.run_oc_delete("drill-scc"):
                Log.info("Deleted SCC policy for mapr-bootstrap on Openshift.", True)

        Log.info(os.linesep + "Deleting Drill Role Binding...", True)
        if self.run_kubectl_delete("drill-rb"):
            Log.info("Deleted Drill Role Binding.")

        Log.info(os.linesep + "Deleting Drill Cluster Role Binding...", True)
        if self.run_kubectl_delete("drill-crb", True):
            Log.info("Deleted Drill Cluster Role Binding.")

        Log.info(os.linesep + "Deleting Drill Role...", True)
        if self.run_kubectl_delete("drill-role"):
            Log.info("Deleted Drill Role.")

        Log.info(os.linesep + "Deleting Drill Cluster Role...", True)
        if self.run_kubectl_delete("drill-cr"):
            Log.info("Deleted Bootstrap Drill Role.")

        Log.info(os.linesep + "Deleting Drill Service Account...", True)
        if self.run_kubectl_delete("drill-sa"):
            Log.info("Deleted Drill Service Account.")

        Log.info(os.linesep + "Deleting Drill Namespace...", True)
        if self.run_kubectl_delete("drill-namespace"):
            Log.info("Deleted Drill Namespace.")

    def install_external_components(self):
        Log.info(os.linesep + "Creating External Info Namespace...", True)
        if self.run_kubectl_apply("external-namespace"):
            Log.info("Created External Info Namespace")

    def uninstall_external_components(self):
        Log.info(os.linesep + "Deleting External Info Namespace...", True)
        if self.run_kubectl_delete("external-namespace"):
            Log.info("Deleted External Info Namespace")

    def install_ingress_components(self, is_cloud):
        Log.info(os.linesep + "Creating Ingress Namespace...", True)
        if self.run_kubectl_apply("ingress-namespace"):
            Log.info("Created Ingress Namespace.")

        Log.info(os.linesep + "Creating Ingress Service Account...", True)
        if self.run_kubectl_apply("ingress-sa"):
            Log.info("Created Ingress Service Account.")

        Log.info(os.linesep + "Creating Ingress Cluster Role...", True)
        if self.run_kubectl_apply("ingress-cr"):
            Log.info("Created Ingress Cluster Role.")

        Log.info(os.linesep + "Creating Ingress Cluster Role Binding...", True)
        if self.run_kubectl_apply("ingress-crb"):
            Log.info("Created Ingress Cluster Role Binding.")

        if self.is_openshift:
            Log.info(os.linesep + "Creating Ingress SCC...", True)
            if self.run_oc_apply("ingress-scc"):
                Log.info("Created SCC policy for mapr-ingress on Openshift", True)
                self.ingress_openshift_policy_add()
                Log.info("Created Ingress SCC.")

        Log.info(os.linesep + "Creating Ambassador Ingress 1...", True)
        if self.run_kubectl_apply("ingress-ambassador1"):
            Log.info("Created Ambassador Ingress 1.")

        Log.info(os.linesep + "Creating Ambassador Ingress 2...", True)
        if self.run_kubectl_apply("ingress-ambassador2"):
            Log.info("Created Ambassador Ingress 2.")

        Log.info(os.linesep + "Creating Ambassador Service...", True)
        if is_cloud:
            if self.run_kubectl_apply("ingress-svc-cloud"):
                Log.info("Created MapR Ingress Service for cloud")
        else:
            if self.run_kubectl_apply("ingress-secret-tls"):
                Log.info("Created MapR Ingress TLS Secret")
            if self.run_kubectl_apply("ingress-svc-baremetal-http"):
                Log.info("Created MapR Ingress Service for Baremetal-HTTP")
            if self.run_kubectl_apply("ingress-svc-baremetal-https"):
                Log.info("Created MapR Ingress Service for Baremetal-HTTPS")

    def uninstall_ingress_components(self, is_cloud):
        Log.info(os.linesep + "Deleting Ambassador Service...", True)
        if is_cloud:
            if self.run_kubectl_delete("ingress-svc-cloud"):
                Log.info("Deleted MapR Ingress Service for cloud")
        else:
            if self.run_kubectl_delete("ingress-secret-tls"):
                Log.info("Deleted MapR Ingress TLS Secret")
            if self.run_kubectl_delete("ingress-svc-baremetal-http"):
                Log.info("Deleted MapR Ingress Service for Baremetal-HTTP")
            if self.run_kubectl_delete("ingress-svc-baremetal-https"):
                Log.info("Deleted MapR Ingress Service for Baremetal-HTTPS")

        Log.info(os.linesep + "Deleting Ambassador Ingress 1...", True)
        if self.run_kubectl_delete("ingress-ambassador1"):
            Log.info("Deleted Ambassador Ingress 1.")

        Log.info(os.linesep + "Deleting Ambassador Ingress 2...", True)
        if self.run_kubectl_delete("ingress-ambassador2"):
            Log.info("Deleted Ambassador Ingress 2.")

        if self.is_openshift:
            Log.info(os.linesep + "Deleting Ingress SCC...", True)
            self.ingress_openshift_policy_remove()
            if self.run_oc_delete("ingress-scc"):
                Log.info("Deleted SCC policy for mapr-ingress on Openshift.", True)

        Log.info(os.linesep + "Deleting Ingress Cluster Role Binding...", True)
        if self.run_kubectl_delete("ingress-crb"):
            Log.info("Deleted Ingress Cluster Role Binding.")

        Log.info(os.linesep + "Deleting Ingress Cluster Role...", True)
        if self.run_kubectl_delete("ingress-cr"):
            Log.info("Deleted Ingress Cluster Role.")

        Log.info(os.linesep + "Deleting Ingress Service Account...", True)
        if self.run_kubectl_delete("ingress-sa"):
            Log.info("Deleted Ingress Service Account.")

        Log.info(os.linesep + "Deleting Ingress Namespace...", True)
        if self.run_kubectl_delete("ingress-namespace"):
            Log.info("Deleted Ingress Namespace.")

    def install_kubeflow_components(self):
        Log.info(os.linesep + "Creating Kubeflow Namespace...", True)
        if self.run_kubectl_apply("kubeflow-namespace"):
            Log.info("Created Kubeflow Namespace.")

        Log.info(os.linesep + "Creating Kubeflow Service Account...", True)
        if self.run_kubectl_apply("kubeflow-sa"):
            Log.info("Created Kubeflow Service Account.")

        Log.info(os.linesep + "Creating Kubeflow Cluster Role...", True)
        if self.run_kubectl_apply("kubeflow-cr"):
            Log.info("Created Kubeflow Cluster Role.")

        Log.info(os.linesep + "Creating Kubeflow Cluster Role Binding...", True)
        if self.run_kubectl_apply("kubeflow-crb"):
            Log.info("Created Kubeflow Cluster Role Binding.")

        Log.info(os.linesep + "Creating secret to pull images for Kubeflow...", True)
        if self.run_kubectl_apply("kubeflow-imagepullsecret"):
            Log.info("Created Kubeflow Pull Secret.")

        Log.info(os.linesep + "Creating Kubeflow Alert Manager CRD...", True)
        if self.run_kubectl_apply("kubeflow-crd-alertmanager"):
            Log.info("Created Kubeflow Alert Manager CRD.")

        Log.info(os.linesep + "Creating Kubeflow Argo CRD...", True)
        if self.run_kubectl_apply("kubeflow-crd-argo"):
            Log.info("Created Kubeflow Argo CRD.")

        Log.info(os.linesep + "Creating Kubeflow CRD...", True)
        if self.run_kubectl_apply("kubeflow-crd-kubeflowoperator"):
            Log.info("Created Kubeflow CRD.")

        Log.info(os.linesep + "Creating Kubeflow Notebook CRD...", True)
        if self.run_kubectl_apply("kubeflow-crd-notebook"):
            Log.info("Created Kubeflow Notebook CRD.")

        Log.info(os.linesep + "Creating Kubeflow Prometheus CRD...", True)
        if self.run_kubectl_apply("kubeflow-crd-prometheus"):
            Log.info("Created Kubeflow Prometheus CRD.")

        Log.info(os.linesep + "Creating Kubeflow Prometheus Rule CRD...", True)
        if self.run_kubectl_apply("kubeflow-crd-prometheusrule"):
            Log.info("Created Kubeflow Prometheus Rule CRD.")

        Log.info(os.linesep + "Creating Kubeflow PyTorch CRD...", True)
        if self.run_kubectl_apply("kubeflow-crd-pytorch"):
            Log.info("Created Kubeflow PyTorch CRD.")

        Log.info(os.linesep + "Creating Kubeflow Seldon Deployment CRD...", True)
        if self.run_kubectl_apply("kubeflow-crd-seldondeployment"):
            Log.info("Created Kubeflow Seldon Deployment CRD.")

        Log.info(os.linesep + "Creating Kubeflow Service Monitor CRD...", True)
        if self.run_kubectl_apply("kubeflow-crd-servicemonitor"):
            Log.info("Created Kubeflow Service Monitor CRD.")

        Log.info(os.linesep + "Creating Kubeflow TF Job CRD...", True)
        if self.run_kubectl_apply("kubeflow-crd-tfjob"):
            Log.info("Created Kubeflow TF Job CRD.")

        Log.info(os.linesep + "Creating Kubeflow TF Serving CRD...", True)
        if self.run_kubectl_apply("kubeflow-crd-tfserving"):
            Log.info("Created Kubeflow TF Serving CRD.")

        Log.info(os.linesep + "Creating Kubeflow Zeppelin CRD...", True)
        if self.run_kubectl_apply("kubeflow-crd-zeppelin"):
            Log.info("Created Kubeflow Zeppelin CRD.")

        Log.info(os.linesep + "Creating Kubeflow Operator...", True)
        if self.run_kubectl_apply("kubeflow-kubeflowoperator"):
            Log.info("Created Kubeflow Operator.")

    def uninstall_kubeflow_components(self):
        Log.info(os.linesep + "Deleting Kubeflow Operator...", True)
        if self.run_kubectl_delete("kubeflow-kubeflowoperator"):
            Log.info("Deleted Kubeflow Operator.")

        Log.info(os.linesep + "Deleting Kubeflow Alert Manager CRD...", True)
        if self.run_kubectl_delete("kubeflow-crd-alertmanager"):
            Log.info("Deleted Kubeflow Alert Manager CRD.")

        Log.info(os.linesep + "Deleting Kubeflow Argo CRD...", True)
        if self.run_kubectl_delete("kubeflow-crd-argo"):
            Log.info("Deleted Kubeflow Argo CRD.")

        Log.info(os.linesep + "Deleting Kubeflow CRD...", True)
        if self.run_kubectl_delete("kubeflow-crd-kubeflowoperator"):
            Log.info("Deleted Kubeflow CRD.")

        Log.info(os.linesep + "Deleting Kubeflow Notebook CRD...", True)
        if self.run_kubectl_delete("kubeflow-crd-notebook"):
            Log.info("Deleted Kubeflow Notebook CRD.")

        Log.info(os.linesep + "DeletingDeleting Kubeflow Prometheus CRD...", True)
        if self.run_kubectl_delete("kubeflow-crd-prometheus"):
            Log.info("Deleted Kubeflow Prometheus CRD.")

        Log.info(os.linesep + "Deleting Kubeflow Prometheus Rule CRD...", True)
        if self.run_kubectl_delete("kubeflow-crd-prometheusrule"):
            Log.info("Deleted Kubeflow Prometheus Rule CRD.")

        Log.info(os.linesep + "DeletingDeleting Kubeflow PyTorch CRD...", True)
        if self.run_kubectl_delete("kubeflow-crd-pytorch"):
            Log.info("Deleted Kubeflow PyTorch CRD.")

        Log.info(os.linesep + "DeletingDeletingDeleting Kubeflow Seldon Deployment CRD...", True)
        if self.run_kubectl_delete("kubeflow-crd-seldondeployment"):
            Log.info("Deleted Kubeflow Seldon Deployment CRD.")

        Log.info(os.linesep + "DeletingDeletingDeletingDeleting Kubeflow Service Monitor CRD...", True)
        if self.run_kubectl_delete("kubeflow-crd-servicemonitor"):
            Log.info("Deleted Kubeflow Service Monitor CRD.")

        Log.info(os.linesep + "DeletingDeletingDeletingDeletingDeleting Kubeflow TF Job CRD...", True)
        if self.run_kubectl_delete("kubeflow-crd-tfjob"):
            Log.info("Deleted Kubeflow TF Job CRD.")

        Log.info(os.linesep + "DeletingDeletingDeletingDeletingDeletingDeleting Kubeflow TF Serving CRD...", True)
        if self.run_kubectl_delete("kubeflow-crd-tfserving"):
            Log.info("Deleted Kubeflow TF Serving CRD.")

        Log.info(os.linesep + "DeletingDeletingDeletingDeletingDeletingDeletingDeleting Kubeflow Zeppelin CRD...", True)
        if self.run_kubectl_delete("kubeflow-crd-zeppelin"):
            Log.info("Deleted Kubeflow Zeppelin CRD.")

        Log.info(os.linesep + "Deleting secret to pull images for Kubeflow...", True)
        if self.run_kubectl_delete("kubeflow-imagepullsecret"):
            Log.info("Deleted Kubeflow Pull Secret.")

        Log.info(os.linesep + "Deleting Kubeflow Cluster Role Binding...", True)
        if self.run_kubectl_delete("kubeflow-crb", True):
            Log.info("Deleted Kubeflow Cluster Role Binding.")

        Log.info(os.linesep + "Deleting Kubeflow Cluster Role...", True)
        if self.run_kubectl_delete("kubeflow-cr"):
            Log.info("Deleted Kubeflow Cluster Role.")

        Log.info(os.linesep + "Deleting Kubeflow Service Account...", True)
        if self.run_kubectl_delete("kubeflow-sa"):
            Log.info("Deleted Kubeflow Service Account.")

        Log.info(os.linesep + "Deleting Kubeflow Namespace...", True)
        if self.run_kubectl_delete("kubeflow-namespace"):
            Log.info("Deleted Kubeflow Namespace.")

    def install_spark_components(self):
        Log.info(os.linesep + "Creating Spark Namespace...", True)
        if self.run_kubectl_apply("spark-namespace"):
            Log.info("Deleted Spark Namespace.")

        Log.info(os.linesep + "Creating Spark Service Account...", True)
        if self.run_kubectl_apply("spark-sa"):
            Log.info("Deleted Spark Service Account.")

        Log.info(os.linesep + "Creating Spark Cluster Role...", True)
        if self.run_kubectl_apply("spark-cr"):
            Log.info("Created Spark Cluster Role.")

        Log.info(os.linesep + "Creating Spark Cluster Role Binding...", True)
        if self.run_kubectl_apply("spark-crb"):
            Log.info("Created Spark Cluster Role Binding.")

        if self.is_openshift:
            Log.info(os.linesep + "Creating Spark SCC...", True)
            if self.run_oc_apply("spark-scc"):
                Log.info("Created SCC policy for Spark on Openshift", True)
                self.spark_openshift_policy_add()
                Log.info("Created Spark SCC.")

        Log.info(os.linesep + "Creating secret to pull images for Spark...", True)
        if self.run_kubectl_apply("spark-imagepullsecret"):
            Log.info("Created Spark Pull Secret.")

        Log.info(os.linesep + "Creating Spark Application CRD...", True)
        if self.run_kubectl_apply("spark-crd-sparkapplication"):
            Log.info("Created Spark Application CRD.")

        Log.info(os.linesep + "Creating Spark Scheduled Application CRD...", True)
        if self.run_kubectl_apply("spark-crd-sparkscheduledapplication"):
            Log.info("Created Spark Scheduled Application CRD.")

        Log.info(os.linesep + "Creating Spark Operator...", True)
        if self.run_kubectl_apply("spark-sparkoperator"):
            Log.info("Created Spark Operator.")

        Log.info(os.linesep + "Creating Spark Operator Service...", True)
        if self.run_kubectl_apply("spark-svc"):
            Log.info("Created Spark Operator Service.")

        Log.info(os.linesep + "Creating Spark Operator Job...", True)
        if self.run_kubectl_apply("spark-job"):
            Log.info("Created Spark Operator Job.")

    def uninstall_spark_components(self):
        Log.info(os.linesep + "Deleting Spark Operator Service...", True)
        if self.run_kubectl_delete("spark-svc"):
            Log.info("Deleted Spark Operator Service.")

        Log.info(os.linesep + "Deleting Spark Operator Job...", True)
        if self.run_kubectl_delete("spark-job"):
            Log.info("Deleted Spark Operator Job.")

        Log.info(os.linesep + "Deleting Spark Operator...", True)
        if self.run_kubectl_delete("spark-sparkoperator"):
            Log.info("Deleted Spark Operator.")

        Log.info(os.linesep + "Deleting secret to pull images for Spark...", True)
        if self.run_kubectl_delete("spark-imagepullsecret"):
            Log.info("Deleted Spark Pull Secret.")

        if self.is_openshift:
            Log.info(os.linesep + "Deleting Spark SCC...", True)
            self.spark_openshift_policy_remove()
            if self.run_oc_delete("spark-scc"):
                Log.info("Deleted SCC policy for mapr-spark on Openshift.", True)

        else:
            Log.info(os.linesep + "Deleting Spark Cluster Role Binding...", True)
            if self.run_kubectl_delete("spark-crb"):
                Log.info("Deleted Spark Cluster Role Binding.")

        Log.info(os.linesep + "Deleting Spark Cluster Role...", True)
        if self.run_kubectl_delete("spark-cr"):
            Log.info("Deleted Spark Cluster Role.")

        Log.info(os.linesep + "Deleting Spark Application CRD...", True)
        if self.run_kubectl_delete("spark-crd-sparkapplication"):
            Log.info("Deleted Spark Application CRD.")

        Log.info(os.linesep + "Deleting Spark Scheduled Application CRD...", True)
        if self.run_kubectl_delete("spark-crd-sparkscheduledapplication"):
            Log.info("Deleted Spark Scheduled Application CRD.")

        Log.info(os.linesep + "Deleting Spark Service Account...", True)
        if self.run_kubectl_delete("spark-sa"):
            Log.info("Deleted Spark Service Account.")

        Log.info(os.linesep + "Deleting Spark Namespace...", True)
        if self.run_kubectl_delete("spark-namespace"):
            Log.info("Deleted Spark Namespace.")

    def install_system_cspace_components(self):
        Log.info(os.linesep + "Creating System Namespace...", True)
        if self.run_kubectl_apply("system-namespace"):
            Log.info("Created System Namespace.")

        Log.info(os.linesep + "Creating secret to pull images for System...", True)
        if self.run_kubectl_apply("system-imagepullsecret"):
            Log.info("Created System Pull Secret.")

        Log.info(os.linesep + "Creating CSpace Operator Service Account...", True)
        if self.run_kubectl_apply("system-sa-cspace"):
            Log.info("Created CSpace Operator Service Account.")

        Log.info(os.linesep + "Creating CSpace Operator ClusterRole...", True)
        if self.run_kubectl_apply("system-cr-cspace"):
            Log.info("Created CSpace Operator ClusterRole.")

        Log.info(os.linesep + "Creating CSpace Operator ClusterRoleBinding...", True)
        if self.run_kubectl_apply("system-crb-cspace"):
            Log.info("Created CSpace Operator ClusterRoleBinding.")

        Log.info(os.linesep + "Creating CSpace CRD...", True)
        if self.run_kubectl_apply("system-crd-cspace"):
            Log.info("Created CSpace CRD.")

        if self.is_openshift:
            Log.info(os.linesep + "Creating CSpace Operator for Openshift...", True)
            if self.run_kubectl_apply("system-cspaceoperator-openshift"):
                Log.info("Created CSpace Operator for Openshift.")

            Log.info(os.linesep + "Creating CSpace SCC...", True)
            if self.run_oc_apply("system-scc-cspace"):
                Log.info("Created SCC policy for cspace on Openshift", True)
                self.cspace_openshift_policy_add()
                Log.info("Created CSpace SCC.")
        else:
            Log.info(os.linesep + "Creating CSpace Operator...", True)
            if self.run_kubectl_apply("system-cspaceoperator"):
                Log.info("Created CSpace Operator.")

        Log.info(os.linesep + "Creating PVCreate ClusterRole...", True)
        if self.run_kubectl_apply("system-cr-pv"):
            Log.info("Created PVCreate ClusterRole.")

        Log.info(os.linesep + "Creating System Priority Class Admin...", True)
        if self.run_kubectl_apply("system-priorityclass-admin"):
            Log.info("Created System Priority Class Admin")

        Log.info(os.linesep + "Creating System Priority Class Cluster Services...", True)
        if self.run_kubectl_apply("system-priorityclass-clusterservices"):
            Log.info("Created System Priority Class Cluster Services")

        Log.info(os.linesep + "Creating System Priority Class Compute...", True)
        if self.run_kubectl_apply("system-priorityclass-compute"):
            Log.info("Created System Priority Class Compute")

        Log.info(os.linesep + "Creating System Priority Class Critical...", True)
        if self.run_kubectl_apply("system-priorityclass-critical"):
            Log.info("Created System Priority Class Critical")

        Log.info(os.linesep + "Creating System Priority Class Admin...", True)
        if self.run_kubectl_apply("system-priorityclass-admin"):
            Log.info("Created System Priority Class Admin")

        Log.info(os.linesep + "Creating System Priority Class Gateways...", True)
        if self.run_kubectl_apply("system-priorityclass-gateways"):
            Log.info("Created System Priority Class Gateways")

        Log.info(os.linesep + "Creating System Priority Class Metrics...", True)
        if self.run_kubectl_apply("system-priorityclass-metrics"):
            Log.info("Created System Priority Class Metrics")

        Log.info(os.linesep + "Creating System Priority Class MFS...", True)
        if self.run_kubectl_apply("system-priorityclass-mfs"):
            Log.info("Created System Priority Class MFS")

        Log.info(os.linesep + "Creating System Priority Class CSpace Services...", True)
        if self.run_kubectl_apply("system-priorityclass-cspaceservices"):
            Log.info("Created System Priority Class CSpace Services")

        Log.info(os.linesep + "Creating System Storage Class HDD...", True)
        if self.run_kubectl_apply("system-storageclass-hdd"):
            Log.info("Created System Storage Class HDD")

        Log.info(os.linesep + "Creating System Storage Class NVME...", True)
        if self.run_kubectl_apply("system-storageclass-nvme"):
            Log.info("Created System Priority Class NVME")

        Log.info(os.linesep + "Creating System Storage Class SSD...", True)
        if self.run_kubectl_apply("system-storageclass-ssd"):
            Log.info("Created System Storage Class SSD")

    def uninstall_system_cspace_components(self):
        if self.is_openshift:
            Log.info(os.linesep + "Deleting CSpace SCC...", True)
            self.cspace_openshift_policy_remove()
            if self.run_oc_delete("system-scc-cspace"):
                Log.info("Deleted SCC policy for CSpace on Openshift.", True)
        else:
            Log.info(os.linesep + "Deleting CSpace Operator ClusterRoleBinding...", True)
            if self.run_kubectl_delete("system-crb-cspace"):
                Log.info("Deleted CSpace Operator ClusterRoleBinding.")

        Log.info(os.linesep + "Deleting PVCreate Cluster Role...", True)
        if self.run_kubectl_delete("system-cr-pv"):
            Log.info("Deleted PVCreate Cluster Role.")

        Log.info(os.linesep + "Deleting CSpace Operator...", True)
        if self.run_kubectl_delete("system-cspaceoperator"):
            Log.info("Deleted CSpace Operator.")

        Log.info(os.linesep + "Deleting CSpace Operator CRD...", True)
        if self.run_kubectl_delete("system-crd-cspace"):
            Log.info("Deleted CSpace Operator CRD.")

        Log.info(os.linesep + "Deleting CSpace Operator Cluster Role...", True)
        if self.run_kubectl_delete("system-cr-cspace"):
            Log.info("Deleted CSpace Operator Cluster Role.")

        Log.info(os.linesep + "Deleting CSpace Operator Service Account...", True)
        if self.run_kubectl_delete("system-sa-cspace"):
            Log.info("Deleted CSpace Operator Service Account.")

        Log.info(os.linesep + "Deleting System Storage Class SSD...", True)
        if self.run_kubectl_delete("system-storageclass-ssd"):
            Log.info("Deleted System Storage Class SSD.")

        Log.info(os.linesep + "Deleting System Storage Class NVME...", True)
        if self.run_kubectl_delete("system-storageclass-nvme"):
            Log.info("Deleted System Storage Class NVME.")

        Log.info(os.linesep + "Deleting System Storage Class HDD...", True)
        if self.run_kubectl_delete("system-storageclass-hdd"):
            Log.info("Deleted System Storage Class HDD.")

        Log.info(os.linesep + "Deleting System Priority Class CSpace Services...", True)
        if self.run_kubectl_delete("system-priorityclass-cspaceservices"):
            Log.info("Deleted System Priority Class CSpace Services.")

        Log.info(os.linesep + "Deleting System Priority Class MFS...", True)
        if self.run_kubectl_delete("system-priorityclass-mfs"):
            Log.info("Deleted System Priority Class MFS.")

        Log.info(os.linesep + "Deleting System Priority Class Metrics...", True)
        if self.run_kubectl_delete("system-priorityclass-metrics"):
            Log.info("Deleted System Priority Class Metrics.")

        Log.info(os.linesep + "Deleting System Priority Class Gateways...", True)
        if self.run_kubectl_delete("system-priorityclass-gateways"):
            Log.info("Deleted System Priority Class Gateways.")

        Log.info(os.linesep + "Deleting System Priority Class Critical...", True)
        if self.run_kubectl_delete("system-priorityclass-critical"):
            Log.info("Deleted System Priority Class Critical.")

        Log.info(os.linesep + "Deleting System Priority Class Compute...", True)
        if self.run_kubectl_delete("system-priorityclass-compute"):
            Log.info("Deleted System Priority Class Compute.")

        Log.info(os.linesep + "Deleting System Priority Class Cluster Services...", True)
        if self.run_kubectl_delete("system-priorityclass-clusterservices"):
            Log.info("Deleted System Priority Class Cluster Services.")

        Log.info(os.linesep + "Deleting System Priority Class Admin...", True)
        if self.run_kubectl_delete("system-priorityclass-admin"):
            Log.info("Deleted System Priority Class Admin.")

        Log.info(os.linesep + "Deleting secret to pull images for System...", True)
        if self.run_kubectl_delete("system-imagepullsecret"):
            Log.info("Deleted System Pull Secret.")

        Log.info(os.linesep + "Deleting System Namespace...", True)
        if self.run_kubectl_delete("system-namespace"):
            Log.info("Deleted System Namespace.")

    def install_system_cluster_components(self):
        Log.info(os.linesep + "Creating Cluster Operator Service Account...", True)
        if self.run_kubectl_apply("system-sa-cluster"):
            Log.info("Created Cluster Operator Service Account.")

        Log.info(os.linesep + "Creating Cluster Operator Cluster Role...", True)
        if self.run_kubectl_apply("system-cr-cluster"):
            Log.info("Created Cluster Operator Cluster Role.")

        Log.info(os.linesep + "Creating Cluster Operator ClusterRoleBinding...", True)
        if self.run_kubectl_apply("system-crb-cluster"):
            Log.info("Created Cluster Operator ClusterRoleBinding.")

        Log.info(os.linesep + "Creating System User Secret...", True)
        if self.run_kubectl_create_secret():
            Log.info("Created system user secret")

        Log.info(os.linesep + "Creating Cluster CRD...", True)
        if self.run_kubectl_apply("system-crd-cluster"):
            Log.info("Created Cluster CRD.")

        Log.info(os.linesep + "Creating Cluster Operator...", True)
        if self.run_kubectl_apply("system-clusteroperator"):
            Log.info("Created Cluster Operator.")

        if self.is_openshift:
            Log.info(os.linesep + "Creating Cluster SCC...", True)
            if self.run_oc_apply("system-scc-cluster"):
                Log.info("Created SCC policy for Cluster on Openshift", True)
                self.cluster_openshift_policy_add()
                Log.info("Created Cluster SCC.")

    def uninstall_system_cluster_components(self):
        if self.is_openshift:
            Log.info(os.linesep + "Deleting Cluster SCC...", True)
            self.cluster_openshift_policy_remove()
            if self.run_oc_delete("system-scc-cluster"):
                Log.info("Deleted SCC policy for Cluster on Openshift.", True)

        Log.info(os.linesep + "Deleting Cluster Operator CRD...", True)
        if self.run_kubectl_delete("system-crd-cluster"):
            Log.info("Deleted Cluster Operator CRD.")

        Log.info(os.linesep + "Deleting Cluster Operator ClusterRoleBinding...", True)
        if self.run_kubectl_delete("system-crb-cluster"):
            Log.info("Deleted Cluster Operator ClusterRoleBinding.")

        Log.info(os.linesep + "Deleting Cluster Operator Cluster Role...", True)
        if self.run_kubectl_delete("system-cr-cluster"):
            Log.info("Deleted Cluster Operator Cluster Role.")

        # Log.info(os.linesep + "Deleting Cluster Operator...", True)
        #if self.run_kubectl_delete("system-clusteroperator"):
        #    Log.info("Deleted Cluster Operator.")

        #Log.info(os.linesep + "Deleting Cluster Operator Service Account...", True)
        #if self.run_kubectl_delete("system-sa-cluster"):
        #    Log.info("Deleted Cluster Operator Service Account.")

        #Log.info(os.linesep + "Deleting System User Secret...", True)
        #if self.run_kubectl_delete_secret():
        #    Log.info("Deleted System User Secret.")


    def install_ui_components(self):
        Log.info(os.linesep + "Creating UI Namespace...", True)
        if self.run_kubectl_apply("ui-namespace"):
            Log.info("Created UI Namespace.")

        Log.info(os.linesep + "Creating secret to pull images for UI...", True)
        if self.run_kubectl_apply("ui-imagepullsecret"):
            Log.info("Created UI Pull Secret.")

        Log.info(os.linesep + "Creating UI Service Account...", True)
        if self.run_kubectl_apply("ui-sa"):
            Log.info("Created UI Service Account.")

        Log.info(os.linesep + "Creating UI Cluster Role...", True)
        if self.run_kubectl_apply("ui-cr"):
            Log.info("Created UI Cluster Role.")

        Log.info(os.linesep + "Creating UI Role...", True)
        if self.run_kubectl_apply("ui-role"):
            Log.info("Created UI Role.")

        Log.info(os.linesep + "Creating UI Cluster Role Binding...", True)
        if self.run_kubectl_apply("ui-crb"):
            Log.info("Created UI Cluster Role Binding.")

        Log.info(os.linesep + "Creating UI Role Binding...", True)
        if self.run_kubectl_apply("ui-rb"):
            Log.info("Created UI Role Binding")

        if self.is_openshift:
            Log.info(os.linesep + "Creating UI SCC...", True)
            if self.run_oc_apply("ui-scc"):
                Log.info("Created SCC policy for mapr-ui on Openshift", True)
                self.ui_openshift_policy_add()
                Log.info("Created UI SCC.")

        Log.info(os.linesep + "Deploying Picasso Admin Service...", True)
        if self.run_kubectl_apply("ui-pas-svc"):
            Log.info("Deployed Picasso Admin Service.")

        Log.info(os.linesep + "Deploying MapR Picasso Admin UI...", True)
        if self.run_kubectl_apply("ui-pas"):
            Log.info("Deployed MapR Picasso Admin UI")

    def uninstall_ui_components(self):
        Log.info(os.linesep + "Deleting MapR Picasso Admin UI...", True)
        if self.run_kubectl_delete("ui-pas"):
            Log.info("Deleted MapR Picasso Admin UI.")

        Log.info(os.linesep + "Deleting Picasso Admin Service...", True)
        if self.run_kubectl_delete("ui-pas-svc"):
            Log.info("Deleted Picasso Admin Service.")

        Log.info(os.linesep + "Deleting secret to pull images for UI...", True)
        if self.run_kubectl_delete("ui-imagepullsecret"):
            Log.info("Deleted UI Pull Secret.")

        if self.is_openshift:
            Log.info(os.linesep + "Deleting UI SCC...", True)
            self.ui_openshift_policy_remove()
            if self.run_oc_delete("ui-scc"):
                Log.info("Deleted UI policy for mapr-ui on Openshift.", True)

        Log.info(os.linesep + "Deleting UI Role Binding...", True)
        if self.run_kubectl_delete("ui-rb"):
            Log.info("Deleted UI Role Binding.")

        Log.info(os.linesep + "Deleting UI Cluster Role Binding...", True)
        if self.run_kubectl_delete("ui-crb"):
            Log.info("Deleted UI Cluster Role Binding.")

        Log.info(os.linesep + "Deleting UI Role...", True)
        if self.run_kubectl_delete("ui-role"):
            Log.info("Deleted UI Role.")

        Log.info(os.linesep + "Deleting UI Cluster Role...", True)
        if self.run_kubectl_delete("ui-cr"):
            Log.info("Deleted UI Cluster Role.")

        Log.info(os.linesep + "Deleting UI Service Account...", True)
        if self.run_kubectl_delete("ui-sa"):
            Log.info("Deleted UI Service Account.")

        Log.info(os.linesep + "Deleting UI Namespace...", True)
        if self.run_kubectl_delete("ui-namespace"):
            Log.info("Deleted UI Namespace.")
