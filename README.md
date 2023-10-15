# Fortigate Config Parser
Given a Fortigate 'show full-configuration' output, this will take the indented text configuration and convert it into a dictionary.

## Usage
1. Initiate FortigateConfig class using a relative path (str) to the 'show full-configuration' Fortigate output.
2. Access the configuration as any other dictionary: self.configuration.