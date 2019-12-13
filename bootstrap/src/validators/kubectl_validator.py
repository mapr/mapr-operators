from common.mapr_logger.log import Log
from common.os_command import OSCommand
from validators.validator import Validator


class KubectlValidator(Validator):
    _instance = None

    @staticmethod
    def get_result(key):
        if KubectlValidator._instance is None:
            return None
        return KubectlValidator._instance.results.get(key)

    @staticmethod
    def get_operation():
        if KubectlValidator._instance is None:
            return None
        return KubectlValidator._instance.operation

    def __init__(self):
        super(KubectlValidator, self).__init__('kubectl')

    def collect(self):
        Log.debug('Checking kubectl is installed correctly...')
        response, status = OSCommand.run2("command -v kubectl")
        if status == 0:
            Log.info("Looking good... Found kubectl")
            self.operation = Validator.OPERATION_OK
        else:
            self.operation = Validator.OPERATION_INSTALL
            Log.error("You will need to have kubectl installed on this machine.")
            Log.error("To install kubectl please see: https://kubernetes.io/docs/tasks/tools/install-kubectl/")
