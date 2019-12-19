import os

from bootstrapbase import BootstrapBase
from common.mapr_logger.log import Log
from common.os_command import OSCommand
from k8s_operations import K8SOperations
from mapr.clouds.cloud import Cloud
from nodelabels import NodeLabels
from validators.kubectl_validator import KubectlValidator
from validators.openshiftclient_validator import OpenshiftClientValidator
from validators.validator import Validator


class BootstrapInstall(BootstrapBase):
    def __init__(self):
        super(BootstrapInstall, self).__init__(True)

        self.cloud_instance = None
        self.cloud_created = False
        self._parse_args()

    def run(self):
        super(BootstrapInstall, self).run()
        k8s = K8SOperations(self._prompts, self.base_dir)
        self.prologue()
        self.python_check()
        self.check_laptop_tools()

        do_storage = self.parsed_args.core_install
        do_cloud_install = self.parsed_args.cloud_install
        do_open_shift = True
        do_csi = True
        install_csi = False
        install_cspaces = True
        install_storage = False
        do_kubeflow = False
        install_kubeflow = False
        do_ui = False
        install_ui = False
        do_ingress = False
        install_ingress = False
        do_config = False
        install_config = True
        do_external = False
        is_cloud = False
        do_spark = False
        install_spark = True
        do_drill = False
        install_drill = True

        if do_cloud_install:
            is_cloud = self.install_cloud()
        if do_open_shift:
            self.is_openshift_env(k8s)
        if do_csi:
            install_csi = self.check_if_csi()
        if do_config:
            install_config = self.check_if_config()
        if do_external:
            self.check_if_external()
        if do_spark:
            install_spark = self.check_if_spark()
        if do_drill:
            install_drill = self.check_if_drill()
        if do_kubeflow:
            install_kubeflow = self.check_if_kubeflow()
        if do_storage:
            install_storage = self.check_if_storage()
            if do_ui:
                install_ui = self.check_if_ui()
            if do_ingress:
                is_cloud = self.is_cloud_env(k8s, is_cloud)
                install_ingress = self.check_if_ingress()
        self.configure_kubernetes()

        nl = NodeLabels(k8s)
        nl.process_labels()
        if install_storage:
            self.validate_nodes()
            k8s.install_bootstrap_components()
            # FIXME: Create Secrets
            k8s.create_user_secret()
            if not k8s.check_ready():
                return
        if install_config:
            if install_cspaces:
                k8s.install_cspaces_configuration_components()
            if install_storage:
                k8s.install_clusters_configuration_components()
        if install_csi:
            k8s.install_csi_components()
        if install_config:
            k8s.install_external_components()
        if install_cspaces:
            k8s.install_system_cspace_components()
        if install_storage:
            k8s.install_system_cluster_components()
        if install_spark:
            k8s.install_spark_components()
        if install_drill:
            k8s.install_drill_components()
        if install_kubeflow:
            k8s.install_kubeflow_components()
        if install_storage:
            if install_ingress:
                k8s.install_ingress_components(is_cloud)
            if install_ui:
                k8s.install_ui_components()
            k8s.uninstall_bootstrap_components()
        self.complete_installation()

    def pas(self, k8s):
        # Configure MapR PAS
        if self.cloud_created:
            if k8s.install_mapr_pas():
                self.pas_complete_installation()

    def is_cloud_env(self, k8s, is_cloud):
        # Don't ask any cloud questions when we created a cloud env
        if is_cloud:
            return True
        if k8s.is_openshift:
            return False
        print(os.linesep)
        # Check if this is cloud environment
        is_cloud = self.check_if_cloud()
        if is_cloud:
            return True
        return False

    def is_openshift_env(self, k8s):
        print(os.linesep)
        # Check if this is openshift environment
        is_openshift = self.check_if_openshift()
        if is_openshift:
            # Check if oc client installed for openshift operations
            self.check_oc_installed()
            k8s.is_openshift = True

    def check_if_storage(self):
        print(os.linesep)
        agree = self._prompts.prompt_boolean("Install MapR Data Platform?", True, key_name="CREATE_STORAGE")
        Log.info("Attention: MapR Data Platform on Kubernetes is PRE-ALPHA Software. Please DO NOT store critical data in clusters you create with this "
                 "operator. You WILL lose data and these clusters WILL NOT be upgradable.", stdout=True)
        print("")
        return agree

    def validate_nodes(self):
        print(os.linesep)
        Log.info("We must validate and annotate your Kubernetes nodes. "
                 "MapR node validation pods will be installed.", stdout=True)
        agree = self._prompts.prompt_boolean("Do you agree?", True, key_name="AGREEMENT_VALIDATE")
        if not agree:
            Log.error("Exiting due to non-agreement...")
            BootstrapBase.exit_application(2)
        # TODO: Add node exclusion code here
        # exclude = self._prompts.prompt_boolean("Do you want to exclude any nodes?", False, key_name="EXCLUDE_NODES")
        # if exclude:
        #    Log.error("Operation not currently supported...")
        #    BootstrapBase.exit_application(6)
        print("")

    @staticmethod
    def check_laptop_tools():
        kubectl_validator = KubectlValidator()
        kubectl_validator.collect()
        if kubectl_validator.operation != Validator.OPERATION_OK:
            BootstrapBase.exit_application(3)

    @staticmethod
    def check_oc_installed():
        oc_validator = OpenshiftClientValidator()
        oc_validator.collect()

        if oc_validator.operation != Validator.OPERATION_OK:
            BootstrapBase.exit_application(5)

    def check_if_cloud(self):
        # TODO: Replace with code to automatically detect if EKS, AKS, or GKE
        choice = self._prompts.prompt_boolean("Installing to a previously created cloud environment?", True, key_name="CLOUD_ENV")
        return choice

    def check_if_openshift(self):
        # TODO: Replace with code to automatically detect openshift
        choice = self._prompts.prompt_boolean("Installing to an Openshift environment?", False, key_name="OPENSHIFT_ENV")
        return choice

    def check_if_csi(self):
        choice = self._prompts.prompt_boolean("Install MapR CSI driver?", True, key_name="INSTALL_CSI")
        return choice

    def check_if_cspaces(self):
        # TODO: Replace with code to sense existing operator and offer to upgrade
        choice = self._prompts.prompt_boolean("Install MapR CSPACES?", True, key_name="INSTALL_CSPACES")
        return choice

    def check_if_spark(self):
        # TODO: Replace with code to sense existing operator and offer to upgrade
        choice = self._prompts.prompt_boolean("Install Spark components?", True, key_name="INSTALL_SPARK")
        return choice

    def check_if_drill(self):
        # TODO: Replace with code to sense existing operator and offer to upgrade
        choice = self._prompts.prompt_boolean("Install Drill components?", True, key_name="INSTALL_DRILL")
        return choice

    def check_if_kubeflow(self):
        # TODO: Add code to sense existing operator and upgrade if avail. Keep question
        choice = self._prompts.prompt_boolean("Install Kubeflow components?", False, key_name="INSTALL_KUBEFLOW")
        return choice

    def check_if_ui(self):
        choice = self._prompts.prompt_boolean("Configure MapR Picasso Admin UI?", False, key_name="INSTALL_UI")
        return choice

    def check_if_ingress(self):
        # TODO: Replace with code to automatically detect environment enough to do automatically
        choice = self._prompts.prompt_boolean("Configure MapR Ingress?", False, key_name="INSTALL_INGRESS")
        return choice

    def check_if_config(self):
        # TODO: Replace with code to sense existing operator and offer to upgrade
        choice = self._prompts.prompt_boolean("Install configuration templates?", True, key_name="INSTALL_CONFIG")
        return choice

    def check_if_external(self):
        # TODO: Replace with code to sense existing operator and offer to upgrade
        choice = self._prompts.prompt_boolean("Install external cluster namespace?", True, key_name="INSTALL_EXTERNAL")
        return choice

    def install_cloud(self):
        print("")
        Cloud.initialize(self._prompts)
        cloud_names = Cloud.get_cloud_names()

        if len(cloud_names) == 0:
            Log.warning("There are no supported cloud providers found in this bootstrapper application")
            return False

        Log.info("If you are installing in a cloud provider, we can help you create your kubernetes environment.", True)
        Log.info("ATTENTION: Cloud Environment installation is provided AS IS with no support.", True)
        Log.info("Work with your IT Team to help create kubernetes environments with the security and reliability features that suit your enterprise needs.", True)

        create = self._prompts.prompt_boolean("Do you want to create a kubernetes environment in the Cloud?", False, key_name="CLOUD_ENV")
        if not create:
            Log.info("Not building cloud environment")
            return False

        # Check the availability of each enabled cloud provider
        Cloud.check_available()
        cloud_names = Cloud.get_cloud_names()
        if len(cloud_names) == 0:
            Log.warning("Some clouds were enabled but necessary modules that support these clouds are not available")
            BootstrapBase.exit_application(7)

        choice = self._prompts.prompt_choices("Choose a cloud provider", Cloud.get_cloud_names(), key_name="CLOUD_PROVIDER")
        Log.info("Using cloud provider {0}".format(choice))
        self.cloud_instance = Cloud.get_instance(choice)
        Log.debug("Using cloud instance {0}".format(str(self.cloud_instance)))

        Log.info("Building {0} cloud k8s...".format(choice))
        self.cloud_instance.build_cloud()
        Log.info("Created {0} cloud k8s".format(choice))
        self.cloud_created = True
        return True

    def configure_kubernetes(self):
        print(os.linesep)
        Log.info("Ensuring proper kubernetes configuration...", True)
        Log.info("Checking kubectl can connect to your kubernetes cluster...", True)
        response, status = OSCommand.run2("kubectl get nodes")
        if status != 0:
            Log.error("Cannot connect to Kubernetes. Make sure kubectl is pre-configured to communicate with a Kubernetes cluster.")
            BootstrapBase.exit_application(4)

        Log.info("Looking good... Connected to Kubernetes", True)
        if self.cloud_instance is not None:
            self.cloud_instance.configure_cloud()

    @staticmethod
    def complete_installation():
        print(os.linesep)

        msg = "This Kubernetes environment"
        warnings = Log.get_warning_count()
        errors = Log.get_error_count()

        if errors > 0 and warnings > 0:
            msg = "{0} had {1} error(s) and {2} warning(s) during the bootstraping process for MapR".format(msg, errors, warnings)
            Log.error(msg)
        elif errors > 0 and warnings == 0:
            msg = "{0} had {1} error(s) during the bootstraping process for MapR".format(msg, errors)
            Log.error(msg)
        elif errors == 0 and warnings > 0:
            msg = "{0} had {1} warnings(s) during the bootstraping process for MapR".format(msg, warnings)
            Log.warning(msg)
        else:
            msg = "{0} has been successfully bootstrapped for MapR".format(msg)
            Log.info(msg, True)
            Log.info("MapR components can now be created via the newly installed operators", True)

        if errors > 0 or warnings > 0:
            msg = "Please check the bootstrap log file for this session here: {0}".format(Log.get_log_filename())
            Log.warning(msg)

        Log.info("")

    @staticmethod
    def pas_complete_installation():
        Log.info("PAS Installation complete")


bootstrap_instsall = BootstrapInstall()
bootstrap_instsall.run()
BootstrapBase.exit_application(0)
