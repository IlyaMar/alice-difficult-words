import os
import yaml

# read resource as string array
class ResourceAdapter:
    def __init__(self):
        pass
    # read as string[]
    def read(self, resource):
        raise Exception("not implemented")

    def read_yaml(self, resource):
        raise Exception("not implemented")

class AdapterException(Exception):
    def __init__(self, message):
        self.message = message


class ArchiveResourceAdapter(ResourceAdapter):
    def __init__(self):
        pass

    def read(self, resource):
        fname = "resources/%s" % resource
        if not os.path.isfile(fname):
            return None
        try:
            f = open(fname)
        except Exception as e:
            raise AdapterException('cannot open resource ' + fname + " " + e)
        return f.read().splitlines()

    def read_yaml(self, resource):
        fname = "resources/%s" % resource
        if not os.path.isfile(fname):
            return None
        with open(fname, "r") as stream:
            try:
                out = yaml.safe_load(stream)
                assert out
                return out
            except yaml.YAMLError as exc:
                raise AdapterException('cannot parse yaml ' + fname + " " + exc)
