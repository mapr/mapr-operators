import argparse
import os
import signal
from datetime import datetime

from common.const import Constants
from common.mapr_logger.log import Log
from common.prompts import Prompts
from validators.python_validator import PythonValidator
from validators.validator import Validator

BOOTSTRAP_BUILD_VERSION_NO = "Development"


class BootstrapBase(object):
    NOW = datetime.now()
    _prompts = None

    def __init__(self, is_install):
        self.prompt_mode = Prompts.PROMPT_MODE_STR
        self.prompt_response_file = None
        self.parsed_args = None

        self.is_install = is_install
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.script_dir = os.path.abspath(os.path.join(self.base_dir, ".."))
        self.log_config_file = os.path.join(self.base_dir, Constants.LOGGER_CONF)
        signal.signal(signal.SIGINT, self.exit_application)

    def run(self):
        logdir = os.path.join(self.script_dir, "logs")
        if os.path.exists(logdir):
            if not os.path.isdir(logdir):
                print("ERROR: {0} is not a directory and cannot be used as alog directory".format(logdir))
                BootstrapBase.exit_application(1)
        else:
            os.mkdir(logdir)

        logname = os.path.join(logdir, BootstrapBase.NOW.strftime("bootstrap-%m-%d_%H:%M:%S.log"))
        Log.initialize(self.log_config_file, logname)

        BootstrapBase._prompts = Prompts.initialize(self.prompt_mode, self.prompt_response_file)
        Log.info("Prompt mode: {0}, response file: {1}".format(self.prompt_mode, self.prompt_response_file))

    def _parse_args(self):
        self.arg_parser = argparse.ArgumentParser()
        self.arg_parser.add_argument("-m", "--mode", action="store",
                                     default=self.prompt_mode, help="prompt mode ({0}, {1}, {2})".format(Prompts.PROMPT_MODE_STR, Prompts.HEADLESS_MODE_STR, Prompts.RECORD_MODE_STR))
        self.arg_parser.add_argument("-r", "--response-file", action="store",
                                     default=self.prompt_response_file, help="prompt response file")
        if self.is_install:
            # Not intended for customer use. No guarantees given if these are set to True
            self.arg_parser.add_argument("--cloud_install", action="store_true", default=False, help=argparse.SUPPRESS)
            self.arg_parser.add_argument("--core_install", action="store_true", default=False, help=argparse.SUPPRESS)

        self.parsed_args = self.arg_parser.parse_args()

        self.prompt_mode = self.parsed_args.mode
        self.prompt_response_file = self.parsed_args.response_file
        self.prompt_mode, self.prompt_response_file = Prompts.validate_commandline_options(self.prompt_mode, self.prompt_response_file)

    def prologue(self):
        title = os.linesep + "MapR for Kubernetes Bootstrap "
        title += "Installer" if self.is_install is True else "Uninstaller"
        title += " (version {0})".format(BOOTSTRAP_BUILD_VERSION_NO)
        Log.info(title, True)
        Log.info("Copyright 2019 MapR Technologies, Inc., All Rights Reserved", True)
        Log.info("https://mapr.com/legal/eula/", True)

    @staticmethod
    def python_check():
        python_validator = PythonValidator()
        python_validator.collect()

        if python_validator.operation == Validator.OPERATION_INSTALL:
            BootstrapBase.exit_application(1)

        if python_validator.operation == Validator.OPERATION_WARNING:
            if not BootstrapBase._prompts.prompt_boolean("Continue with an incompatible Python version?", False,
                                                         key_name="PYTHON_INCOMPATIBLE_CONTINUE"):
                BootstrapBase.exit_application(1)
        elif python_validator.operation != Validator.OPERATION_OK:
            BootstrapBase.exit_application(1)

    @staticmethod
    def exit_application(signum, _=None):
        if signum == 0:
            Log.info("Bootstrap terminated {0}".format(signum))
        else:
            print(os.linesep)
            Log.warning("Bootstrap terminated {0}".format(signum))
        if BootstrapBase._prompts is not None:
            BootstrapBase._prompts.write_response_file()
            BootstrapBase._prompts = None
        Log.close()
        exit(signum)
