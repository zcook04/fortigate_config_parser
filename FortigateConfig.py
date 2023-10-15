import re

class NestedDict(dict):
    def add_nested_key(self, dic: dict, keys: list):
        if not keys:
            return True
        key = keys[0]
        if key not in dic:
            dic[key] = {}
        return self.add_nested_key(dic[key], keys[1:])

    def add_nested_value(self, keys: str, value: str):
        for key in keys:
            self = self[key]
        config_item, value = FortinetConfig.parse_set_command_into_value(value)
        if len(value) == 1:
            self[config_item] = value[0]
        else:
            self.setdefault(config_item, value)


class FortinetConfig:
    def __init__(self, configuration_path: str):
        self.configuration = self.parse_full_configuration(
            configuration_path)

    @property
    def hostname(self):
        return self.configuration.get('system global', {}).get('hostname', '')

    @property
    def management_ip(self):
        return self.configuration.get('system interface', {}).get('mgmt1', {}).get('ip', ['none']).split(' ')[0]

    @property
    def address_objects(self):
        return self.configuration.get('firewall address', {})

    @staticmethod
    def parse_set_command_into_value(set_command: str):
        m = re.search(r'(set )([\w-]*\s)([\S ]*)', set_command)
        return (m.group(2).strip(), m.group(3).strip())

    def parse_full_configuration(self, configuration_path):
        with open(configuration_path, 'r') as file:
            parsed_dictionary = NestedDict()
            indented_keys = []

            for line in file:
                line = line.strip()

                # End of configuration section go next.
                if line == 'end' or line == 'next':
                    if (indented_keys):
                        indented_keys.pop()
                    continue

                # Start of configuration section.
                if line.startswith('config '):
                    indented_keys.append(line[7:])
                    parsed_dictionary.add_nested_key(
                        parsed_dictionary, indented_keys)

                # Start of sub configuration section
                if line.strip().startswith('edit '):
                    indented_keys.append(line.replace('"', '')[5:])
                    parsed_dictionary.add_nested_key(
                        parsed_dictionary, indented_keys)

                if line.strip().startswith('set ') and len(indented_keys) > 0:
                    value = line.strip().replace('"', '')
                    parsed_dictionary.add_nested_value(indented_keys, value)

        return parsed_dictionary

    def add_finding(self, finding_id: str, trigger: str):
        self.findings.setdefault(finding_id, trigger)