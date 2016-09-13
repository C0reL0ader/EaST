toastr.options.timeOut = 1000;

$(document).ready(function() {
    mainVue = new Vue({
        el: '#mainVue',
        data: commonData,
        events: {
            onTreeNodeSelected: function(data, module) {
                this.selectedModule = module;
            },
            onTreeNodeClicked: function(module) {
                this.runSelectedModule(module.NAME);
            },
            onTabClose: function(tab) {
                // Kill process at server-side
                guiCommandsHandler.killProcess(tab.title);
            },
            onSendCommand: function(command, tab) {
                guiCommandsHandler.sendListenerCommand(tab.title, command);
                var index = _.indexOf(this.tabsData, tab);
            },
            onImageClick: function(image) {
                imagePopup.showImage(image);
            },
            onModuleEdit: function(module) {
                this.editSelectedModule(module.NAME)
            }
                    
        },
        ready: function() {
            bindEvent("on_module_message", this.onModuleMessage);
            bindEvent("on_listener_message", this.onListenerMessage);
        },
        methods: {
            addTab: function(data) {
                this.tabs.push(data);
            },
            runSelectedModule: function(moduleName) {
                guiCommandsHandler.showOptions(moduleName, function(evt) {
                    optionsDialog.showDialog(moduleName, evt.args);                    
                });
            },

            editSelectedModule: function(moduleName) {
                guiCommandsHandler.getSource(moduleName, function(evt) {
                    var args = evt.args;
                    var content = args.message;
                    editorDialog.showContent(moduleName, content);
                });
            },

            onModuleMessage: function(e) {
                var args = e.args;
                var module = _.find(this.tabs, {title: args.module_name});
                if(!module)
                    return
                var index = _.indexOf(this.tabs, module);
                if (args.message.type == 'image') {
                    args.message.message = 'data:image/jpg;base64,' + args.message.message;
                }
                module.content.push(args.message);
                if (args.state != null) {
                    module.state = args.state;
                    showTabInfo(module);
                }
                if (index != -1) {
                    var selector = '.tab-content #tab_item_' + index + ' .logView';
                    Vue.nextTick(function () {
                       $(selector).scrollTop($(selector)[0].scrollHeight);
                    })
                }
                
            },

            onListenerMessage: function(e) {
                var args = e.args;
                var listenerState = args.state;
                var listenerMessage = args.message;
                var module = _.find(this.tabs, {title: args.module_name});
                if (!module)
                    return
                var index = _.indexOf(this.tabs, module);
                module.listenerMessages += '\n' + listenerMessage;
                if (listenerState == 1 && module.listenerState != 1){
                    module.listenerState = listenerState;
                    toastr.success("Shell successfully connected to " + args.module_name);
                    showTabInfo(module);
                }
                if (listenerState == 2  && module.listenerState != 2){
                    module.listenerState = listenerState;
                    toastr.warning("Listener disconnected from " + args.module_name);
                    showTabInfo(module);
                }                
                var selector = '.tab-content #tab_item_' + index + ' .pre-scrollable';
                Vue.nextTick(function () {
                   $(selector).scrollTop($(selector)[0].scrollHeight);
                })
            }
        }
    })

    optionsDialog = new Vue({
        el: '#optionsDialog',
        data: {
            options: [],
            show: false,
            moduleName: {},
            useListener: false
        },
        methods: {
            showDialog: function(moduleName, options) {
                var hostPort = commonData.target.split(':');
                if (hostPort) {
                    var host = hostPort[0];
                    var port;
                    if (hostPort.length > 1) {
                        port = hostPort[1];
                    }
                    _.forEach(options, function(entry, index) {
                        if (entry.option.toLowerCase() == "host")
                            options[index].value.value = host || entry.value.value;
                        else if (entry.option.toLowerCase() == "port")
                            options[index].value.value = port || entry.value.value;
                    })
                }
                this.$data.moduleName = moduleName;
                this.$data.options = options;
                this.$data.show = true;
            },
            ok: function() {
                var args = {
                    module_name: this.moduleName,
                    use_listener: this.useListener,
                    options: this.options
                };
                guiCommandsHandler.startModule(args, function(e) {
                    var args = e.args;
                    var data = {
                        title: args.module_name,
                        content: [{message: 'Starting ' + args.module_name}],
                        active: true,
                        useListener: args.listener,
                        listenerMessages: '',
                        listenerState: 0,
                        state: null
                    }
                    mainVue.addTab(data);
                })             
                this.cancel();
            },

            cancel: function() {
                this.show = false;
            }
        }
    })

    imagePopup = new Vue({
        el: '#imagePopup',
        data: {
            image: '',
            show: false,
        },
        methods: {
            showImage: function(image) {
                this.image = image;
                this.show = true;
            },
            close: function() {
                this.show = false;
            }
        }
    })

    editorDialog = new Vue({
        el: '#editorDialog',
        data: {
            show: false,
            title: '',
            content: '',
            editor: null
        },
        ready: function() {
            var scope = this;
            this.editor = CodeMirror.fromTextArea(document.getElementById('editor'), {
                lineNumbers: true,
                indentUnit: 4,
                mode: "python",
                autofocus: true
            });
            this.editor.refresh();

        },
        methods: {
            showContent: function(moduleName, content) {
                this.title = moduleName;
                this.content = content;
                this.editor.setValue(content);
                this.show = true;
                var self = this;
                Vue.nextTick(function () {
                   self.editor.refresh();
                })
                
            },
            save: function() {
                this.content = this.editor.getValue();
                guiCommandsHandler.saveSource(this.title, this.content);
                this.show = false;
            }
        }
    })
});

function changeFavicon(icon) {
  var $favicon = document.querySelector('link[rel="icon"]')
  // If a <link rel="icon"> element already exists,
  // change its href to the given link.
  if ($favicon !== null) {
    $favicon.href = "/icons/" + icon
  // Otherwise, create a new element and append it to <head>.
  } else {
    $favicon = document.createElement("link")
    $favicon.id = 'dynamic-favicon';
    $favicon.rel = "icon"
    $favicon.href = "/icons/" + icon
    document.head.appendChild($favicon)
  }
}

function setDefaultInfo() {
    changeFavicon('transparent.ico');
    document.title = "EaST Framework";
}

function showTabInfo(tab) {
    if (tab.useListener) {
        if (tab.listenerState == 0) {
            changeFavicon('listener-enabled.ico');
        } else if (tab.listenerState == 1) {
            changeFavicon('listener-connected.ico');
        } else if (tab.listenerState == 2) {
            changeFavicon('listener-disconnected.ico');
        }
    } else {
        changeFavicon('transparent.ico');
    }
    var title = tab.title
    if (tab.state == true) {
        title += "(SUCCEEDED)";
    } else if (tab.state == false) {
        title += "(FAILED)"
    } else {
        title += "(RUNNING)"
    }
    document.title = title;
}