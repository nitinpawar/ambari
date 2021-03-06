/**
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

require('views/common/controls_view');

var App = require('app');
/**
 * Checkbox config widget for enhanced configs.
 * @type {Em.View}
 */
App.CheckboxConfigWidgetView = App.ConfigWidgetView.extend({
  templateName: require('templates/common/configs/widgets/checkbox_config_widget'),
  classNames: ['widget-config', 'checkbox-widget'],

  didInsertElement: function () {
    var self = this;
    this._super(arguments);
    Em.run.next(function () {
      if (self.$())
      self.$('input[type="checkbox"]:eq(0)').checkbox({
        defaultState: self.get('config.value'),
        buttonStyle: 'btn-link btn-large',
        checkedClass: 'icon-check',
        uncheckedClass: 'icon-check-empty'
      });
    });
  },

  configView: App.ServiceConfigCheckbox.extend({
    serviceConfigBinding: 'parentView.config',
    // @TODO maybe find use case of this method for widget
    focusIn: function() {}
  }),

  /**
   * Manually reset bootstrap-checkbox
   * @method restoreValue
   */
  restoreValue: function () {
    this.$('input[type="checkbox"]:eq(0)').checkbox('click');
    this._super();
  }

});
