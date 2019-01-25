var treeNodeTemplate = function(){/*
 <li :class="{'hidden': !visible}" @click="select" @dblclick="run">
   <span v-if="isFolder" :class="[opened ? folderIconOpened: folderIconClosed]"></span>
   <button v-show="!isFolder" class="btn btn-default btn-xs" @click="run">
     <span class="glyphicon glyphicon-play"></span>
   </button>
   <button v-show="!isFolder" class="btn btn-default btn-xs" @click="edit">
     <span class="glyphicon glyphicon-pencil"></span>
   </button>
   {{module.NAME}}
 </li>
 <ul :class="{ 'hidden': !opened || isChildrenInvisible }">
    <tree-node v-for="child in sortedChildren" :module="child"></tree-node>
 </ul>
 */}.toString().slice(14, -3);
Vue.component('tree-node', {
  template: treeNodeTemplate,
  computed: {
    isChildrenInvisible: function() {
      return _.filter(this.$children, 'visible').length == 0;
    },
    isFolder: function () {
      return !this.module.isFile;
    },
    sortedChildren: function () {
      return _.sortBy(this.module.children, ['isFile', 'NAME'])
    }
  },
  props: ['module', 'toFilter'],
  data: function () {
    return {
      opened: false,
      visible: true,
      folderIconOpened: 'glyphicon glyphicon-folder-open',
      folderIconClosed: 'glyphicon glyphicon-folder-close'
    }
  },
  methods: {
    select: function() {
      if (!this.isFolder) {
        this.$dispatch('onTreeNodeSelected', this.$data, this.module);
      } else {
        this.opened = !this.opened;
      }
    },
    edit: function() {
      this.$dispatch('onModuleEdit', this.module);
    },
    run: function () {
      if (this.isFolder) {
        this.opened = !this.opened
      } else {
        this.$dispatch('onTreeNodeClicked', this.module);
        this.select();
      }
    },
  }
});

var treeViewTemplate = function(){/*
 <div class="form-group has-feedback">
    <input type="text" class="form-control" v-model="toSearch" placeholder="Search for...">
    <span v-show='toSearch.length' class="form-control-feedback"> <a class="pointer" @click="toSearch=''"><small>X</small></a></span>
  </div>
 <div class="treeview left-panel">
   <ul>
     <tree-node v-for="module in sortedModules" :module="module"></tree-node>
   </ul>
 </div>
 */}.toString().slice(14, -3);
Vue.component('tree-view', {
  template: treeViewTemplate,
  props: {
    modules: []
  },
  data: function () {
    return {
      toSearch: ''
    }
  },
  computed: {
    sortedModules: function () {
      return _.sortBy(this.modules, ['isFile', 'NAME'])
    }
  },
  watch: {
    'toSearch': function (newVal, oldVal) {
      this.search(this.$children);
    }
  },
  methods: {
    search: function (children, parent) {
      var self = this;
      children.forEach(function(child, index) {
        if (child.$children && child.$children.length) {
          if (self.toSearch)
            child.opened = true;
          else
            child.opened = false;
          return self.search(child.$children, child);
        } else {
          var module = child.module;
          var toSearch = self.toSearch.toLowerCase();
          if (module.NAME && module.NAME.toLowerCase().indexOf(toSearch) !== -1 ||
              module.DESCRIPTION && module.DESCRIPTION.toLowerCase().indexOf(toSearch) !== -1 ||
              module.VENDOR && module.VENDOR.toLowerCase().indexOf(toSearch) !== -1 ||
              module.NOTES && module.NOTES.toLowerCase().indexOf(toSearch) !== -1 ||
              module['CVE Name'] && module['CVE Name'].toLowerCase().indexOf(toSearch) !== -1){
            child.visible = true;
          } else {
            child.visible = false;
          }
        }
      })
      if (parent) {
        var visible_count = _.filter(children, 'visible').length;
        if (!visible_count) {
          parent.visible = false;
        } else {
          parent.visible = true;
        }
      }

    },
  }
});

var tab_view_template = function(){/*
  <div class="tab-widget">
    <ul class="nav nav-tabs">
      <li v-for="tab in tabs" @click="chooseTab($index)" :class="{'active': tab.active}">
        <a href="#tab_item_{{$index}}" :class="{'module-failed': tab.state == false, 'module-succeeded': tab.state == true}">
        <div v-show="tab.useListener" :class="['listener-state-indicator', {'listener-connected': tab.listenerState == 1, 'listener-disconnected': tab.listenerState == 2}]" :title="tab.listenerState ? tab.listenerState == 1 ? 'Listener connected': 'Listener disconnected' : 'Listener is not connected'"></div>
        {{tab.title}}
        </a>
        <div class="closeTab" @click="closeTab($index)">x</div>
      </li>
    </ul>
    <div class="tab-content">
      <div v-for="tab in tabs" id="tab_item_{{$index}}" :class="['tab-pane fade', {'in active': tab.active}]">
        <div class="panel">
          <div class="panel-heading modal-header">
            <b>Log for {{tab.title}}</b>
          </div>
          <div class="panel-body">
            <div class="logView" :class="{'half-height': tab.useListener, 'full-height': !tab.useListener}">
              <re-log-view :messages.sync="tab.content" ></re-log-view>
            </div>
          </div>
        </div>
        <div class="panel" style="height:40%;" v-show="tab.useListener">
          <div class="panel-heading modal-header"><b>Listener for {{tab.title}}:</b></div>
          <div class="panel-body">
            <pre class="pre-scrollable"> {{tab.listenerMessages}}</pre>
            <div class="form-inline">
              <label>Command to execute >></label>
              <div class="input-group">
                <input type="text" class="form-control" @keyup.enter="send($index)" @keyup.up="historyUp" @keyup.down="historyDown" v-model="command">
                <span class="input-group-btn">
                  <button class="btn btn-default" type="button" @click="send($index)">Send</button>
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

  </div>
*/}.toString().slice(14,-3);

Vue.component('tab-view', {
  template: tab_view_template,
  props: {
    tabs: Array
    /*
    tabs = {
      title: args.module_name,
      content: 'Starting ' + args.module_name,
      active: true,
      useListener: args.listener,
      listenerMessages: '',
      listenerState: null,
      state: null
    }
    */
  },
  data: function () {
    return {
      search: '',
      tabActive: 'active',
      command: '',
      history: []
    }
  },
  watch: {
    'tabs.length': {
      handler: function (val, oldVal) {
        //make new tab active
        if(val > oldVal) {
          this.chooseTab(val - 1);
        }
      }
    }
  },
  methods: {
    historyUp: function() {
      if (!this.history || !this.history.length) {
        return;
      }
      this.historyIndex -= 1;
      if (this.historyIndex < 0) {
        this.historyIndex = 0;
      }
      this.command = this.history[this.historyIndex];
    },
    historyDown: function() {
      if (!this.history || !this.history.length) {
        return;
      }
      this.historyIndex += 1;
      if (this.historyIndex >= this.history.length) {
        this.historyIndex = this.history.length;
        this.command = '';
        return;
      }
      this.command = this.history[this.historyIndex];
    },
    closeTab: function(index) {
      var current_tab = this.tabs[index];
      this.tabs.splice(index, 1);
      if(current_tab.active){
        if (this.tabs.length <= index) {
          index -= 1;
        }
        this.chooseTab(index);
      }
      this.$dispatch('onTabClose', current_tab)
      if (!this.tabs.length) {
        setDefaultInfo();
      }
    },

    chooseTab: function(index) {
      if(!this.tabs.length)
        return;
      this.tabs.forEach(function(tab) {
        tab.active = false;
      });
      this.tabs[index].active = true;
      showTabInfo(this.tabs[index]);
    },
    send: function(index) {
      var tab = this.tabs[index];
      tab.listenerMessages += "\n>> " + this.command;
      if (_.indexOf(this.history, this.command) !== -1) {
        this.history.splice(this.history.indexOf(this.command), 1);
      }
      this.history.push(this.command);
      this.historyIndex = this.history.length;
      this.$dispatch('onSendCommand', this.command, tab);
      this.command = "";
    }
  },
});

var logViewTemplate = function(){/*
    <div class="logItem" v-for="item in messages">
      <pre v-show="item.type=='text'">{{getMessage($index)}}</pre>
      <div v-show="item.type=='image'">
        <pre>{{item.time}}: </pre>
        <p>
          <img :src="item.type=='image' ? item.message: '/'" @click="onImageClick($index)"></img>
        </p>
      </div>
      
    </div>
*/}.toString().slice(14,-3);

Vue.component('re-log-view', {
  template: logViewTemplate,
  props: {
    messages: Array
  },
  methods: {
    onImageClick: function(index) {
      var image = this.messages[index].message;
      this.$dispatch('onImageClick', image);
    },
    getMessage: function(index) {
      var item = this.messages[index];
      var resp = '';
      if (item.time) {
        resp += item.time + ': '
      }
      resp += item.message;
      return resp;
    }
  }
})

var btn_create_module_template = function() {/*
    <div class="create-module">
      <button class="btn btn-create-module" type="button" @click="click">
        <span class="glyphicon glyphicon-plus"></span>
      </button>
    </div>
*/}.toString().slice(14, -3)

Vue.component('re-btn-create-module', {
  template: btn_create_module_template,
  props: {
    title: String
  },
  methods: {
    click: function() {
      this.$dispatch('onCreateModule');
    }
  }
})

var create_module_options_template = function() {/*
    <tr>
      <td>
        <input type="text" v-model="option_name" v-on:input="onChange()"/>
      </td>
      <td>
        <select v-model="option_type" @change="onChange()">
          <option>int</option>
          <option selected="">string</option>
          <option>boolean</option>
          <option>select</option>
        </select>
      </td>
      <td>
        <template v-if="option_type == 'int' || option_type == 'string'">
          <input type="text" v-model="option_value" v-on:input="onChange()"/>
        </template>
        <template v-if="option_type == 'boolean'">
          <input type="checkbox" v-bind:value="option_value" v-on:input="onChange(option_type)">Enabled</input>
        </template>
        <template v-if="option_type == 'select'">
          <select>
            <option>
            </option>
          </select>
        </template>
      </td>
      <td>
        <input type="text" v-model="option_desc" v-on:input="onChange()"/>
      </td>
      <td>
        <button class="btn btn-add-option" v-if="show_button" v-on:click="click">
          Add option
        </button>
      </td>
      <td>
        <button class="btn btn-delete-option" v-on:click="onDelete"> 
          Delete
        </button>
      </td>
    </tr>
*/}.toString().slice(14, -3)

Vue.component('create-module-options', {
  template: create_module_options_template,
  props: {
    id: Number,
    option_name: String,
    option_value: {
      default: this.defaultValue
    },
    option_desc: String,
    option_type: String,
    show_button: {
      default: true
    }
  },
  data: function() {
    var theData = {
      option_name: this.option_name,
      option_value: this.option_value,
      option_desc: this.option_desc,
      option_type: this.option_type,
      show_button: this.show_button
    }
    return theData
  },
  methods: {
    click: function() {
      this.show_button = false
      this.$dispatch('add_option', this.id)
    },
    onChange: function(input_type) {
      // inventing bycicle...
      // TODO: refactor this
      if (input_type == 'boolean') {
        if (this.option_value == 'false') {
          this.option_value = 'True'
        }
        else if (this.option_value == 'true') {
          this.option_value = 'False'
        }
        else {
          this.option_value = 'True'
        }
      }
      let data = {
        id: this.id,
        option_name: this.option_name,
        option_value: this.option_value,
        option_desc: this.option_desc,
        option_type: this.option_type
      }
      this.$dispatch('create_module_option_changed', data)
    },
    onDelete: function() {
      let data = {id: this.id}
      this.$dispatch('delete_module_option', data)
    }
  }
})

var modal_create_module_dialog_template = function() {/*
<div v-show="show" :transition="transition">
    <div class="modal" @click.self="clickMask">
      <div class="modal-dialog" :class="modalClass" v-el:dialog>
        <div class="modal-content">
          <!--Header-->
          <div class="modal-header">
            <slot name="header">
              <a type="button" class="close" @click="cancel">x</a>
              <h4 class="modal-title">
                <slot name="title">
                    {{title}}
                </slot>
              </h4>
            </slot>
          </div>
          <!--Container-->
          <div class="modal-body">
            <slot></slot>
            <input type="text" id="create" rows="1" autocomplete="off" v-model="moduleName"></input>
            <input type="checkbox" id="showAdvanced" v-model="show_advanced">Advanced</input>
            <div v-show="show_advanced">
              <h4>Module options:</h4>
              <table id="newModuleOptions">
                <tr>
                  <th>name</th>
                  <th>type</th>
                  <th>value</th>
                  <th>description</th>
                </tr>
                <template v-for="data in moduleOptions">
                  <create-module-options :show_button="data.show" :option_name="data.name" :option_value="data.value" :option_desc="data.desc" :id="data.id"/>
                </template>
              </table>
              <h4>Module features:</h4>
              <create-module-features/>
            </div>
          </div>
          <!--Footer-->
          <div class="modal-footer">
            <slot name="footer">
              <button type="button" :class="cancelClass" @click="cancel">{{cancelText}}</button>
              <button type="button" :class="okClass" @click="ok">{{okText}}</button>
            </slot>
          </div>
        </div>
      </div>
    </div>
  <div class="modal-backdrop in"></div>
</div>
*/}.toString().slice(14, -3)
Vue.component('re-modal-create-module', {
  template: modal_create_module_dialog_template,
  props: {
    moduleName: String,
    moduleOptions: {
      twoWay: true,
      default: [
      {id:0, name:'', value:'', desc:'', type: 'string', show:true }
    ]},
    optionId: {
      default: 1
    },
    show: {
      twoWay: true,
      default: false
    },
    small: {
        default: false
    },
    large: {
        default: false
    },
    full: {
        default: false
    },
    transition: {
        default: 'modal'
    },
    cancelText: {
      default: 'Cancel'
    },
    okText: {
      default: 'OK'
    },
    force: {
      default: false
    },
    show_advanced: {
      default: false
    }
  },
  events: {
    add_option: function(id) {
      this.moduleOptions.push({id:this.optionId, name:'', value:'', desc:'', type:'string', show:true })
      this.optionId++
      for (var i = 0; i < this.moduleOptions.length - 1; i++) {
        if (this.moduleOptions[i].id === id) {
          this.moduleOptions[i].show = false
          break
        }
      }
    },
    create_module_option_changed: function(data) {
      console.log('change intercepted')
      console.log('value ' + data.option_value)
      this.debug()
      for (var i = 0; i < this.moduleOptions.length; i++) {
        if (this.moduleOptions[i].id === data.id) {
          this.moduleOptions[i].name = data.option_name
          this.moduleOptions[i].value = data.option_value
          this.moduleOptions[i].desc = data.option_desc
          this.moduleOptions[i].type = data.option_type
          console.log('change made\r\n')
          this.debug()
          break
        }
      }
    },
    delete_module_option: function(data) {
      if (this.moduleOptions.length === 1) {
        return
      }
      this.moduleOptions = this.moduleOptions.filter(function(value, index, arr) {
        return value.id != data.id
      })
      if (data.id === this.optionId - 1) {
        var index = this.moduleOptions.length - 1
        this.moduleOptions[index].show = true
        this.optionId--
      }

    }
  },
  computed: {
    modalClass: function () {
      return {
          'modal-lg': this.large,
          'modal-sm': this.small,
          'modal-full': this.full
      }
    }
  },
  created: function() {
    if (this.show) {
      document.body.className += ' modal-open';
    }
  },
  beforeDestroy: function() {
    document.body.className = document.body.className.replace('modal-open', '');
  },
  watch: {
    show: function(value) {
      if (value) {
        document.body.className += ' modal-open';
      }
      else {
        if (!this.duration) {
          this.duration = window.getComputedStyle(this.$el)['transition-duration'].replace('s', '') * 1000;
        }
        document.body.className = document.body.className.replace(' modal-open', '');
      }
    }
  },
  methods: {
    ok: function() {
      this.$emit('ok')
      var filtered = this.moduleOptions.filter(function(value, index, arr){
        return value.name.length > 0 && value.value.length > 0;
      })
      guiCommandsHandler.createModule(this.moduleName, filtered)
      this.show = false
    },
    cancel: function() {
      this.$emit('cancel')
      this.show = false
      this.moduleOptions = [{id:0, name:'', value:'', desc:'', type: 'string', show:true }]
      this.optionId = 1
    },
    clickMask: function() {
        if (!this.force) {
            this.cancel();
        }
    },
    openAdvanced: function() {
        showAdvanced = document.getElementById("showAdvanced").value
    },
    debug: function() {
      for (var i = 0; i < this.moduleOptions.length; i++) {
        var info = this.moduleOptions[i].name + ' ' + this.moduleOptions[i].type + ' ' + this.moduleOptions[i].value + ' ' + this.moduleOptions[i].desc
        console.log(info)
      }
    }
  }
})

var create_module_features = function() {/*
  <table style="width: 100%; border: 1px solid black;">
    <tr>
      <th>Target</th>
      <th>Exploit type</th>
      <th>Features</th>
    </tr>
    <tr>
      <td>
        <select v-model="target.selected">
          <option v-for="opt in target.options" :value="opt.value">
            {{ opt.text }}
          </option>
        </select>
      </td>
      <td>
        <select v-model="exploitType.selected">
          <option v-for="opt in exploitType.options" :value="opt.value">
            {{ opt.text }}
          </option>
        </select>
      </td>
      <td>
        <table style="width: 100%;">
          <module-feature v-for="f in features" :name="f.name" :checked="f.checked"/>
        </table>
      </td>
    </tr>
  </table>
*/}.toString().slice(14, -3)

Vue.component('create-module-features', {
  template: create_module_features,
  data: function() {
    return {
      target: {
        selected: 'web',
        options: [
          {text: 'Web', value: 'web'},
          {text: 'Local', value: 'local'}
        ]
      },
      exploitType: {
        selected: 'sqli',
        options: [
          {text: 'SQL Injection', value: 'sqli'},
          {text: 'Time-based Blind SQL Injection', value: 'bsqli'}
        ]
      },
      features: [
        {id: 1, name: 'Create method', checked: false},
        {id: 2, name: 'Import lib', checked: false},
        {id: 3, name: 'Make url', checked: false}
      ]
    }
  },
  created: function() {
    //this.applyPredefined([2,3]);
  },
  watch: {
    'target.selected': function(val) {
      switch (val) {
        case 'web':
          this.applyPredefined([1,3], true)
          break
        case 'local':
          this.applyPredefined([2], true)
        default:
          return
      }
    }
  },
  methods: {
    applyPredefined: function(features_id, value) {
      for (var i = 0; i < features_id.length; i++) {
        var index = this.features.findIndex(function(elem, index, arr) {
          return elem.id == features_id[i]
        })
        if (index != -1) {
          this.features[index].checked = value
        }
      }
    },
    uncheckAll: function() {
      for (var i = 0; i < this.features.length; i++) {
        this.features[i].checked = false
      }
    }
  }
})

var module_feature = function() {/*
  <tr>
    <td>
      <input type="checkbox" v-model="checked">{{ name }}</input>
    </td>
  </tr>
*/}.toString().slice(14, -3)

Vue.component('module-feature', {
  template: module_feature,
  props: {
    name: {
      default: 'Feature'
    },
    checked: {
      default: false
    }
  },
  data: function() {
    
  }
})


var modal_dialog_template = function() {/*
  <div v-show="show" :transition="transition">
    <div class="modal" @click.self="clickMask">
      <div class="modal-dialog" :class="modalClass" v-el:dialog>
        <div class="modal-content">
          <!--Header-->
          <div class="modal-header">
            <slot name="header">
              <a type="button" class="close" @click="cancel">x</a>
              <h4 class="modal-title">
                <slot name="title">
                    {{title}}
                </slot>
              </h4>
            </slot>
          </div>
          <!--Container-->
          <div class="modal-body">
            <slot></slot>
          </div>
          <!--Footer-->
          <div class="modal-footer">
            <slot name="footer">
              <button type="button" :class="cancelClass" @click="cancel">{{cancelText}}</button>
              <button v-show="showOk" type="button" :class="okClass" @click="ok">{{okText}}</button>
            </slot>
          </div>
        </div>
      </div>
    </div>
  <div class="modal-backdrop in"></div>
</div>
*/}.toString().slice(14,-3)
Vue.component('re-modal', {
  template: modal_dialog_template,
  props: {
    show: {
        twoWay: true,
        default: false
    },
    title: {
        default: 'Modal'
    },
    small: {
        default: false
    },
    large: {
        default: false
    },
    full: {
        default: false
    },
    force: {
        default: false
    },
    transition: {
        default: 'modal'
    },
    okText: {
        default: 'OK'
    },
    cancelText: {
        default: 'Cancel'
    },
    okClass: {
        default: 'btn blue'
    },
    cancelClass: {
        default: 'btn red btn-outline'
    },
    closeWhenOK: {
        default: false
    },
    showOk: {
      default: true
    }
  },
  data: function() {
    return {
      duration: null
    }
  },
  computed: {
    modalClass: function () {
      return {
          'modal-lg': this.large,
          'modal-sm': this.small,
          'modal-full': this.full
      }
    }
  },
  created: function() {
    if (this.show) {
      document.body.className += ' modal-open';
    }
  },
  beforeDestroy: function() {
    document.body.className = document.body.className.replace('modal-open', '');
  },
  watch: {
    show: function(value) {
      if (value) {
        document.body.className += ' modal-open';
      }
      else {
        if (!this.duration) {
          this.duration = window.getComputedStyle(this.$el)['transition-duration'].replace('s', '') * 1000;
        }
        document.body.className = document.body.className.replace(' modal-open', '');
      }
    }
  },
  methods: {
    ok: function() {
        this.$emit('ok');
        if (this.closeWhenOK) {
            this.show = false;
        }
    },
    cancel: function() {
        this.$emit('cancel');
        this.show = false;
    },
    clickMask: function() {
        if (!this.force) {
            this.cancel();
        }
    }
  }
})

var moduleInfo = function(){/*
    <div class="panel">
      <div class="panel-heading modal-header">
        <b>Module info:</b>
      </div>
      <div class="panel-body left-panel">
        <b>Description:</b> {{module.DESCRIPTION || 'N/A'}} <br>
        <b>Vendor:</b>
        <a v-show="module.VENDOR" href="{{module.VENDOR}}" target="_blank">{{module.VENDOR}}</a>
        <div v-show="!module.VENDOR" :style="displayInline">N/A</div>
        <br>
        <b>CVE:</b> {{module['CVE Name'] || 'N/A'}} <br>
        <b>Links:</b>
        <ol v-if="links.length">
          <li v-for="link in links">
            <a href="{{link}}">{{link}}</a>
          </li>
        </ol>
        <div v-else :style="displayInline">N/A</div>
        <br v-show="!links.length">
        <b>Download link:</b>
        <a v-show="module.DOWNLOAD_LINK" href="{{module.DOWNLOAD_LINK}}" target="_blank">{{module.DOWNLOAD_LINK}}</a>
        <div v-show="!module.DOWNLOAD_LINK" :style="displayInline">N/A</div>
        <br>
        <b>Notes:</b>
        <pre>{{module.NOTES}}</pre>
      </div>
    </div>
*/}.toString().slice(14,-3)

Vue.component('re-module-info', {
  template: moduleInfo,
  props: {
    module: Object
  },
  computed: {
    displayInline: function() {
      return 'display: inline;'
    },
    links: function () {
      var links = this.module.LINKS;
      if (links && links.length) {
        if (_.isString(links)) {
          links = [links];
        }
      }
      return _.filter(links, function(link) {
        return link && link.length;
      })
    }
  }
})

var serviceMessagesTemplate = function(){/*
    <!--<li><a href="#">Warnings:</a> </li>-->
  <a href="#" v-show="messages && messages.length"><span class="label label-danger" @click="show=!show">{{messages.length}}</span></a>

  <re-modal title="Service Messages" :show.sync="show" :large="true" :show-ok="false" cancel-text="Close">
  <ul class="list-group">
    <li class="" v-for="entry in messages" :class="getMessageLevel($index)">
        {{entry.message}}
        <button v-show="entry.message_type==1" class="btn btn-default btn-xs" title="Install via PIP"
            :disabled="entry.installed" @click="install($index)">{{entry.installed ? 'Installing...': 'Install'}}</button>
    </li>
  </ul>
  </re-modal>
*/}.toString().slice(14,-3);
Vue.component('re-service-messages', {
  template: serviceMessagesTemplate,
  props: {
    messages: []
  },
  data: function() {
    return {
      show: false,
    }
  },
  methods: {
    getMessageLevel: function (index) {
      var entry = this.messages[index];
      if (entry.level == 4) {
        return 'list-group-item list-group-item-danger';
      } else if (entry.level == 3) {
        return 'list-group-item list-group-item-warning';
      } else if (entry.level == 2) {
        return 'list-group-item list-group-item-info'
      } else {
        return ''
      }
    },
    install: function(index) {
      var entry = this.messages[index];
      entry.installed = true;
      var self = this;
      guiCommandsHandler.installViaPip(entry.module_to_import, function(event) {
        var args = event.args;
        if (args.error) {
          toastr.error(args.message);
          entry.installed = false;
          return;
        }
        self.messages = _.filter(self.messages, function(message) {
          if (message.message_type == 1) {
            return message.module_to_import != entry.module_to_import;
          } else {
            return true;
          }
        })
        toastr.success('Module ' + entry.module_to_import + ' successfully installed');
        if (!self.messages || !self.messages.length) {
          self.show = false;
        }
      });
    }
  }
})