#!/usr/bin/env ambari-python-wrap
"""
Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import socket

from stack_advisor import StackAdvisor

class HDP21StackAdvisor(HDP206StackAdvisor):

  def recommendServiceConfigurations(self, service):
    calculator = super(HDP21StackAdvisor, self).recommendServiceConfigurations(service)
    if calculator is None:
      return {
        "OOZIE": self.recommendOozieConfigurations,
        "HIVE": self.recommendHiveConfigurations,
        "TEZ": self.recommendTezConfigurations
      }.get(service, None)
    else:
      return calculator

  def recommendOozieConfigurations(self, configurations, clusterData):
    if "FALCON_SERVER" in clusterData["components"]:
      putMapredProperty = self.putProperty(configurations, "oozie-site")
      putMapredProperty("oozie.services.ext",
                        "org.apache.oozie.service.JMSAccessorService," +
                        "org.apache.oozie.service.PartitionDependencyManagerService," +
                        "org.apache.oozie.service.HCatAccessorService")

  def recommendHiveConfigurations(self, configurations, clusterData):
    containerSize = clusterData['mapMemory'] if clusterData['mapMemory'] > 2048 else clusterData['reduceMemory']
    containerSize = min(clusterData['containers'] * clusterData['ramPerContainer'], containerSize)
    putHiveProperty = self.putProperty(configurations, "hive-site")
    putHiveProperty('hive.auto.convert.join.noconditionaltask.size', int(containerSize / 3) * 1048576)
    putHiveProperty('hive.tez.java.opts', "-server -Xmx" + str(int(0.8 * containerSize))
                    + "m -Djava.net.preferIPv4Stack=true -XX:NewRatio=8 -XX:+UseNUMA -XX:+UseParallelGC")
    putHiveProperty('hive.tez.container.size', containerSize)

  def recommendTezConfigurations(self, configurations, clusterData):
    putTezProperty = self.putProperty(configurations, "tez-site")
    putTezProperty("tez.am.resource.memory.mb", clusterData['amMemory'])
    putTezProperty("tez.am.java.opts",
                   "-server -Xmx" + str(int(0.8 * clusterData["amMemory"]))
                   + "m -Djava.net.preferIPv4Stack=true -XX:+UseNUMA -XX:+UseParallelGC")

  def isNotPreferableOnAmbariServerHost(self, component):
    componentName = component["StackServiceComponents"]["component_name"]
    service = ['STORM_UI_SERVER', 'DRPC_SERVER', 'STORM_REST_API', 'NIMBUS', 'GANGLIA_SERVER', 'NAGIOS_SERVER']
    return componentName in service

  def isNotValuable(self, component):
    componentName = component["StackServiceComponents"]["component_name"]
    service = ['JOURNALNODE', 'ZKFC', 'GANGLIA_MONITOR', 'APP_TIMELINE_SERVER']
    return componentName in service

  def selectionScheme(self, componentName):
    scheme = super(HDP21StackAdvisor, self).selectionScheme(componentName)
    if scheme is None:
      return {
        'APP_TIMELINE_SERVER': {31: 1, "else": 2},
        'FALCON_SERVER': {6: 1, 31: 2, "else": 3}
        }.get(componentName, None)
    else:
      return scheme

  def validateServiceConfigurations(self, serviceName):
    validator = super(HDP21StackAdvisor, self).validateServiceConfigurations(serviceName)
    if validator is None:
      return {
        "STORM": ["storm-site", self.validateStormConfigurations],
        "HIVE": ["hive-site", self.validateHiveConfigurations],
        "TEZ": ["tez-site", self.validateTezConfigurations]
      }.get(serviceName, None)
    else:
      return validator

  def validateHiveConfigurations(self, properties, recommendedDefaults):
    validationItems = [ {"config-name": 'hive.tez.container.size', "message": self.validatorLessThenDefaultValue(properties, recommendedDefaults, 'hive.tez.container.size')},
                        {"config-name": 'hive.tez.java.opts', "message": self.validateXmxValue(properties, recommendedDefaults, 'hive.tez.java.opts')},
                        {"config-name": 'hive.auto.convert.join.noconditionaltask.size', "message": self.validatorLessThenDefaultValue(properties, recommendedDefaults, 'hive.auto.convert.join.noconditionaltask.size')} ]
    return self.toConfigurationValidationErrors(validationItems, "hive-site")

  def validateStormConfigurations(self, properties, recommendedDefaults):
    validationItems = [ {"config-name": 'drpc.childopts', "message": self.validateXmxValue(properties, recommendedDefaults, 'drpc.childopts')},
                        {"config-name": 'ui.childopts', "message": self.validateXmxValue(properties, recommendedDefaults, 'ui.childopts')},
                        {"config-name": 'logviewer.childopts', "message": self.validateXmxValue(properties, recommendedDefaults, 'logviewer.childopts')} ]
    return self.toConfigurationValidationErrors(validationItems, "storm-site")

  def validateTezConfigurations(self, properties, recommendedDefaults):
    validationItems = [ {"config-name": 'tez.am.resource.memory.mb', "message": self.validatorLessThenDefaultValue(properties, recommendedDefaults, 'tez.am.resource.memory.mb')},
                        {"config-name": 'tez.am.java.opts', "message": self.validateXmxValue(properties, recommendedDefaults, 'tez.am.java.opts')} ]
    return self.toConfigurationValidationErrors(validationItems, "tez-site")

