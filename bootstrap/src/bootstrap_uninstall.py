import os

from bootstrapbase import BootstrapBase
from common.mapr_logger.log import Log
from k8s_operations import K8SOperations


class BootstrapUninstall(BootstrapBase):
    def __init__(self):
        super(BootstrapUninstall, self).__init__(False)
        self._parse_args()

    def run(self):
        super(BootstrapUninstall, self).run()
        k8s = K8SOperations(self._prompts, self.base_dir)
        self.python_check()
        self.prologue()
        self.confirm_delete_installation()

        do_csi = True
        uninstall_csi = False
        do_cspaces = False
        uninstall_cspaces = True
        do_storage = False
        uninstall_storage = False
        do_kubeflow = False
        uninstall_kubeflow = False
        uninstall_ui = False
        do_spark = False
        uninstall_spark = True
        do_drill = False
        uninstall_drill = True
        do_config = True
        uninstall_config = False
        do_external = True
        uninstall_external = False
        # FIXME: Enable for ingress uninstallation
        # do_ingress = False
        uninstall_ingress = False

        if do_csi:
            uninstall_csi = self.check_remove_csi()
        if do_cspaces:
            uninstall_cspaces = self.check_remove_cspaces()
        if do_storage:
            uninstall_storage = self.check_remove_storage()
        if do_spark:
            uninstall_spark = self.check_remove_spark()
        if do_drill:
            uninstall_drill = self.check_remove_drill()
        if do_kubeflow:
            uninstall_kubeflow = self.check_remove_kubeflow()
        if do_config:
            uninstall_config = self.check_remove_config()
        if do_external:
            uninstall_external = self.check_remove_external()
        # Check if the connected k8s environment is Openshift
        if k8s.is_openshift_connected():
            k8s.is_openshift = True
        if uninstall_cspaces:
            k8s.uninstall_system_cspace_components()
        if uninstall_storage:
            k8s.uninstall_system_cluster_components()
        if uninstall_spark:
            k8s.uninstall_spark_components()
        if uninstall_drill:
            k8s.uninstall_drill_components()
        if uninstall_config:
            if uninstall_cspaces:
                k8s.uninstall_cspaces_configuration_components()
            if uninstall_storage:
                k8s.uninstall_clusters_configuration_components()
        if uninstall_kubeflow:
            k8s.uninstall_kubeflow_components()
        if uninstall_storage:
            if uninstall_ui:
                k8s.uninstall_ui_components()
            if uninstall_ingress:
                is_cloud = self.is_cloud_env()
                k8s.uninstall_ingress_components(is_cloud)
        if uninstall_csi:
            k8s.uninstall_csi_components()
        if uninstall_external:
            k8s.uninstall_external_components()
        self.complete_uninstallation()

    def confirm_delete_installation(self):
        print(os.linesep)
        Log.info("This will uninstall ALL MapR operators from your Kubernetes environment. This will cause all Compute Spaces to be destroyed. They cannot be recovered!", True)
        agree = self._prompts.prompt_boolean("Do you agree?", False, key_name="AGREEMENT")
        if not agree:
            Log.info("Very wise decision. Exiting uninstall...", True)
            BootstrapBase.exit_application(2)

    def check_remove_csi(self):
        choice = self._prompts.prompt_boolean("Remove MapR CSI driver?", False, key_name="REMOVE_CSI")
        return choice

    def check_remove_spark(self):
        choice = self._prompts.prompt_boolean("Remove Spark components?", False, key_name="REMOVE_SPARK")
        return choice

    def check_remove_drill(self):
        choice = self._prompts.prompt_boolean("Remove Drill components?", False, key_name="REMOVE_DRILL")
        return choice

    def check_remove_kubeflow(self):
        choice = self._prompts.prompt_boolean("Remove Kubeflow components?", False, key_name="REMOVE_KUBEFLOW")
        return choice

    def check_remove_cspaces(self):
        choice = self._prompts.prompt_boolean("Remove MapR CSPACES?", False, key_name="REMOVE_CSPACES")
        return choice

    def check_remove_storage(self):
        choice = self._prompts.prompt_boolean("Remove MapR Data Platform?", False, key_name="REMOVE_STORAGE")
        return choice

    def check_remove_ui(self):
        choice = self._prompts.prompt_boolean("Remove MapR Picasso Admin UI?", False, key_name="REMOVE_UI")
        return choice

    def check_remove_config(self):
        choice = self._prompts.prompt_boolean("Remove MapR Configuration?", False, key_name="REMOVE_CONFIG")
        return choice

    def check_remove_external(self):
        choice = self._prompts.prompt_boolean("Remove MapR External Info?", False, key_name="REMOVE_EXTERNAL_INFO")
        return choice

    def check_remove_ingress(self):
        choice = self._prompts.prompt_boolean("Remove MapR Ingress", False, key_name="REMOVE_INGRESS")
        return choice

    def is_cloud_env(self):
        print(os.linesep)
        is_cloud = self._prompts.prompt_boolean("Is this a cloud env?", True, key_name="CLOUD_ENV")
        if is_cloud:
            return True
        return False

    @staticmethod
    def complete_uninstallation():
        print(os.linesep)
        Log.info("Installation deleted successfully!", True)


bootstrap_uninstall = BootstrapUninstall()
bootstrap_uninstall.run()
BootstrapBase.exit_application(0)
