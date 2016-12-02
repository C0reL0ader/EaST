// Very dirty hack
var tree_template = function(){/*
  <ul v-show="showNode">
    <li class="node" :class="{ 'collapsed': !open}">
        <button v-show="model.isFile" class="btn btn-default btn-xs" @click="run">
          <span class="mif-play"></span>
        </button>
        <button v-show="model.isFile" class="btn btn-default btn-xs" @click="edit">
          <span class="mif-pencil"></span>
        </button>
        <span class="leaf" @click="select" @dblclick="run">{{model.NAME}}</span>
        <span v-if="model.children" class="node-toggle" @click="open=!open"></span>
        <tree-node v-if="model.children" v-for="child in model.children" :model.sync="child" />
    </li>
  </ul>
*/}.toString().slice(14,-3)

Vue.component('tree-node', {
  template: tree_template,
  props: {
    model: Object,
    entry_filter: String
  },
  data: function () {
    return {
      showNode: true,
      open: false,
      search: '',
      selected: false
    }
  },
  computed: {
    isFolder: function () {
      return !this.model.isFile;
    },
  },
  methods: {
    select: function() {
      if (!this.isFolder) {
        // this.selected = true;
        this.$dispatch('onTreeNodeSelected', this.$data, this.model);
      } else {
        this.open = !this.open;
      }
    },
    edit: function() {
      this.$dispatch('onModuleEdit', this.model);
    },
    run: function () {      
      if (this.isFolder) {
        this.open = !this.open
      } else {
        this.$dispatch('onTreeNodeClicked', this.model);
        this.select();
      }
    },
  }
})




var tree_view_template = function(){/*
  <div class="input-control text">
      <input type="text" v-model="search" placeholder="Search for...">
      <button class="button helper-button clear" tabindex="-1" @click="search=''"><span class="mif-cross"></span></button>
  </div>
  <div class="treeview left-panel">
    <tree-node v-for="entry in model" :model.sync="entry" :entry_filter.sync="search"></tree-node>
  </div>
*/}.toString().slice(14,-3)

Vue.component('tree-view', {
  template: tree_view_template,
  props: {
    model: Array
  },
  data: function () {
    return {
      search: '',
      previousSelected: null
    }
  },
  computed: {
    searchFor: function() {
      return this.search
    },    
  },
  watch: {
    'search.length': {
      handler: function(oldVal, newVal) {
        var self = this;
        var walk = function (node) {
          if (node.$children) {
            var filteredCount = 0;
            _.forEach(node.$children, function(child, index) {
              if (child.$children && child.$children.length) {
                return walk(child);
              }
              var toSearch = self.search.toLowerCase();
              var model = child.model;
              if (model.isFile) {
                if (model.NAME && model.NAME.toLowerCase().indexOf(toSearch) !== -1 ||
                    model.DESCRIPTION && model.DESCRIPTION.toLowerCase().indexOf(toSearch) !== -1 ||
                    model.VENDOR && model.VENDOR.toLowerCase().indexOf(toSearch) !== -1 ||
                    model.NOTES && model.NOTES.toLowerCase().indexOf(toSearch) !== -1 ||
                    model['CVE Name'] && model['CVE Name'].toLowerCase().indexOf(toSearch) !== -1) {
                  child.$data.showNode = true;
                } else {
                  child.$data.showNode = false;
                  filteredCount += 1;
                }
              } else {
                child.$data.showNode = true;
              }
            });
            if (filteredCount == node.$children.length) {
              node.$data.showNode = false;
            } 
            else {
              node.$data.showNode = true;
              node.$data.open = true;
            }
            if (!_.filter(node.$children, 'showNode').length) {
              node.$data.showNode = false;
            }
          }
        }
        walk(self);
      }
    }
  },
  methods: {
    makeAction: function() {
      alert(1);
    },
  },
})




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
                <input type="text" class="form-control" @keyup.enter="send($index)" v-model="command">
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
*/}.toString().slice(14,-3)


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
      command: ''
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
      this.$dispatch('onSendCommand', this.command, tab);
      this.command = "";
    }
  },  
})

var logViewTemplate = function(){/*
    <div class="logItem" v-for="item in messages">
      <pre v-show="item.type=='text'">{{item.time}}: {{item.message}}</pre>
      <div v-show="item.type=='image'">
        <pre>{{item.time}}: </pre>
        <p>
          <img :src="item.type=='image' ? item.message: '/'" @click="onImageClick($index)"></img>
        </p>
      </div>
      
    </div>
*/}.toString().slice(14,-3)

Vue.component('re-log-view', {
  template: logViewTemplate,
  props: {
    messages: Array
  },
  data: function () {
    return {
      
    }
  },
  computed: {
    searchFor: function() {
      return this.search
    },    
  },
  methods: {
    onImageClick: function(index) {
      var image = this.messages[index].message;
      this.$dispatch('onImageClick', image);
    }
  }
})


var modal_dialog_template = function(){/*  
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