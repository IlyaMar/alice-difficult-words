import os
# import yaml
import json


# read resource as string array
class ResourceAdapter:
    def __init__(self):
        pass

    def read(self, resource):
        raise Exception("not implemented")

    def read_yaml(self, resource):
        raise Exception("not implemented")


class AdapterException(Exception):
    def __init__(self, message):
        self.message = message


class ArchiveResourceAdapter(ResourceAdapter):
    def __init__(self, resources_path):
        self.resources_path = resources_path

    def __get_file_name(self, resource):
        return "%s/%s" % (self.resources_path, resource)

    def read(self, resource):
        fname = self.__get_file_name(resource)
        if not os.path.isfile(fname):
            return None
        try:
            f = open(fname)
        except Exception as e:
            raise AdapterException('cannot open resource ' + fname + " " + e)
        return f.read().splitlines()

    # def read_yaml(self, resource):
    #     fname = "resources/%s" % resource
    #     if not os.path.isfile(fname):
    #         return None
    #     with open(fname, "r") as stream:
    #         try:
    #             out = yaml.safe_load(stream)
    #             assert out
    #             return out
    #         except yaml.YAMLError as exc:
    #             raise AdapterException('cannot parse yaml ' + fname + " " + exc)


    def read_json(self, resource):
        fname = self.__get_file_name(resource)
        if not os.path.isfile(fname):
            return None
        with open(fname, "r") as stream:
            try:
                out = json.load(stream)
                assert out
                return out
            except Exception as e:
                raise AdapterException('cannot parse json ' + fname + " " + e)


