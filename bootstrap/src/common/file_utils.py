

class FileUtils(object):
    """
    Find an occurance of a yaml key in a file and replace the value for that key.
    filename - the yaml file to load the contents of to check for replacements
    replace_dict - keys/values of where the key is also the key in the yaml file and value is the replacement

    return the new file name and if the file has changed or is the original file
    """
    @staticmethod
    def replace_yaml_value(filename, replace_dict):
        # 1) open with PyYAML
        # 2) try and find all keys in replace_dict and replace the value
        # 3) write new yaml file to a new file
        # 4) return full path to new yaml file

        # TODO: Don't return original file name, return the temporary one
        return filename, False
