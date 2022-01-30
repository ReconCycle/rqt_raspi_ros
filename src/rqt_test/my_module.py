import os
import rospy
import rospkg
import rosservice


from digital_interface_msgs.srv import ConfigRead, ConfigSet,ConfigSetRequest


from qt_gui.plugin import Plugin
#from python_qt_binding import loadUi
from python_qt_binding.QtWidgets import QWidget, QGroupBox, QVBoxLayout, QCheckBox, QPushButton, QLabel, QHBoxLayout, QLineEdit, QRadioButton, QButtonGroup
from python_qt_binding.QtCore import  QTimer
from python_qt_binding.QtGui import  QPixmap

class MyPlugin(Plugin):

    def __init__(self, context):
        self._sim_namespace = "/simulate/"
        self.groupbox = None

        self.active_module_template = "None"
        self.template_config_list = []
        self.templates_in_reach_box = "None"

        super(MyPlugin, self).__init__(context)
        # Give QObjects reasonable names
        self.setObjectName('MyPlugin')

        # Process standalone plugin command-line arguments
        from argparse import ArgumentParser
        parser = ArgumentParser()
        # Add argument(s) to the parser.
        parser.add_argument("-q", "--quiet", action="store_true",
                      dest="quiet",
                      help="Put plugin in silent mode")
        args, unknowns = parser.parse_known_args(context.argv())

        if not args.quiet:
            print('arguments: ', args)
            print('unknowns: ', unknowns)


        # creating label
        self.label = QLabel("")
         
        # loading image
        path=os.path.dirname(os.path.realpath(__file__)) 
        print(path+"/reconcycle-logo-head.png")
        self.pixmap = QPixmap(path+"/reconcycle-logo-head.png")
        #self.pixmap = QPixmap("Blue_dot.png", format = "png")
        print(self.pixmap)
        #print(self.pixmap.load('reconcycle-logo-head.png'))
        print(self.pixmap.width())
        print(self.pixmap.height())

 
        # adding image to label
        self.label.setPixmap(self.pixmap)
 
        # Optional, resize label to image size
        self.label.resize(self.pixmap.width(),
                          self.pixmap.height())

        

        # Create QWidget
        self._widget = QWidget()
        self._layout  = QVBoxLayout()
        self._layout.addWidget(self.label)

        self.button1 = QPushButton("Update simulation interface")
        self.button_template = QPushButton("Select RASPI template to change")

        self._layout.addWidget(self.button1)
        self._layout.addWidget(self.button_template)

        self._layout.addStretch()
        self._widget.setLayout(self._layout)
        # Get path to UI file which should be in the "resource" folder of this package
        #ui_file = os.path.join(rospkg.RosPack().get_path('rqt_test'), 'resource', 'MyPlugin.ui')
        # Extend the widget with all attributes and children from UI file
        #loadUi(ui_file, self._widget)
        # Give QObjects reasonable names


        
        self._widget.setObjectName('MyPluginUi')

        #print(self._widget)
        self.button1.clicked[bool].connect(self.update_layout)
        self.button_template.clicked[bool].connect(self.select_template)


        # Show _widget.windowTitle on left-top of each plugin (when 
        # it's set in _widget). This is useful when you open multiple 
        # plugins at once. Also if you open multiple instances of your 
        # plugin at once, these lines add number to make it easy to 
        # tell from pane to pane.
        if context.serial_number() > 1:
            self._widget.setWindowTitle(self._widget.windowTitle() + (' (%d)' % context.serial_number()))
        # Add widget to the user interface
        context.add_widget(self._widget)
        self._context=context


        self.input_interface_dict = {}
        self.output_interface_dict = {}
        self.param_list = []

        #self.demo_test()


        # Start a timer to trigger updates
        self._update_timer = QTimer()
        self._update_timer.setInterval(500)
        self._update_timer.timeout.connect(self.update_values)
        self._update_timer.start()


    def shutdown_plugin(self):
        # TODO unregister all publishers here
        pass

    def save_settings(self, plugin_settings, instance_settings):
        # TODO save intrinsic configuration, usually using:
        # instance_settings.set_value(k, v)
        pass

    def restore_settings(self, plugin_settings, instance_settings):
        # TODO restore intrinsic configuration, usually using:
        # v = instance_settings.value(k)
        pass

    def delete_layout(self):
        self.groupbox.deleteLater()
        print("deliting")
        pass

    def update_layout(self):

        if self.groupbox != None:
            self.delete_layout()
        param_list = rospy.get_param_names()
        module_list = []
        self.param_list=[]

        self.input_interface_dict = {}
        self.output_interface_dict = {}

        last_module = ""
        groupbox = QGroupBox("Values of simulated modules IOs")

        list_layout=QVBoxLayout()
        #list_layout.addStretch()



   
        first=True
        for i in param_list:
            

            if i.find(self._sim_namespace) != -1:
                
                j = i.replace(self._sim_namespace,"")
                in_te = j.find("/")

                if in_te != -1:
                    
                    module_name=j[0:in_te]




                    if last_module != module_name:

                        last_module = module_name  
                        if first==True:
                            first = False
                             
                        else:
    
                            modulebox.setLayout(module_layout)
                        #h_dummy = QHBoxLayout()
                        #h_dummy.insertWidget(-1,modulebox)
                        #list_layout.addLayout(h_dummy)
                            list_layout.insertWidget(list_layout.count()-1,modulebox)

                        modulebox = QGroupBox(module_name)
                        module_layout = QVBoxLayout()


                    if j[j.rfind("/")+1:]=="type":


                        interface_type=rospy.get_param(i)
    
            
                        if interface_type=="DO":
                    

                            label_1 = QLabel("")
                            label_1.setStyleSheet("border: 1px solid black; background-color: green")
            
                            label_1.setFixedSize(20, 20)
                            label_1.move(20, 20)
                            self.output_interface_dict[i.replace("type","value")]=label_1


                        if interface_type=="DI":
                            label_1 = QCheckBox("")
                            self.input_interface_dict[i.replace("type","value")]=label_1

                        h_layout = QHBoxLayout()

                        h_layout.addStretch()
                        h_layout.insertWidget(h_layout.count()-1,label_1)


                        io_names = self.get_pin_names(module_name)

                        #print(io_names[int(j[in_te+1:j.rfind("/")])-1].service_name)
                        #label_name = QLabel(j[in_te+1:j.rfind("/")])
                        label_name = QLabel(io_names[int(j[in_te+1:j.rfind("/")])-1].service_name)


                        h_layout.insertWidget(h_layout.count()-1,label_name)                      
                        module_layout.addLayout(h_layout)

                        self.param_list.append(i.replace("type","value"))



        if first==False:
            modulebox.setLayout(module_layout)
            list_layout.insertWidget(list_layout.count()-1,modulebox)

                #self.interface_dict['new']=label_1

        #layout.addStretch()
        print(list_layout.count())
        groupbox.setLayout(list_layout)
        groupbox.adjustSize()
        self.groupbox =  groupbox
        self._layout.insertWidget(self._layout.count()-1,groupbox)   
        #self._layout.addStretch()
        #self._context.add_widget(groupbox)
        #self._layout.addStretch()
        self._widget.setLayout(self._layout)
        self._widget.adjustSize()
        
        self.update_values()


        pass

    def select_template(self):


        if self.templates_in_reach_box == "None":
            service_list=rosservice.get_service_list()
                #search for the configuration services
            raspi_services=[]
            for i in service_list:
                if 'config_set_new' in i:
                    i = i.replace('config_set_new','')
                    raspi_services.append(i)

            if len(raspi_services)==0:
                label_1 = QLabel("No Raspberries services in reach!")
                print('Hello! I\'m Rassberry ROS configuration client. No Raspberries services in my reach!')
                return

            else:    
                label_1 = QLabel("Raspberries in reach:")
                
            groupbox = QGroupBox("Raspberries templates")
            layout = QVBoxLayout()
            layout.addWidget(label_1)

            j=0
            for i in raspi_services:
                j=j+1
                button = QPushButton(str(j)+'.  '+str(i))
                name = str(i)
                #button.clicked[bool].connect(lambda state, x=name: self.change_template(name))
                button.clicked[bool].connect(self.change_template(name))
                #label_1 = QLabel(str(j)+'.  '+str(i))
                layout.addWidget(button)
                del button
                #print(str(j)+'.  '+str(i))

            #layout.addStretch()
            groupbox.setLayout(layout)
            groupbox.adjustSize()
            self.templates_in_reach_box = groupbox
            self._layout.insertWidget(self._layout.count()-1,groupbox)    
            #self._layout.addStretch()
            self._widget.setLayout(self._layout)
            self._widget.adjustSize()
        pass

    def change_template(self,name):

        def this_template():

            self.active_module_template=name
            demand_name=self.active_module_template+'config_read_current'

            read_proxy= rospy.ServiceProxy(demand_name, ConfigRead)

            self.template_msg = read_proxy().config


            
 
        return this_template
 

    def create_one_group(self):
        pass

    def get_pin_names(self,module_name):

        #def this_template():

        demand_name='/'+module_name+'_manager/'+'config_read_current'
        #print(demand_name)
        read_proxy= rospy.ServiceProxy(demand_name, ConfigRead)

        template_msg = read_proxy().config

        return template_msg.pin_configs


        #return this_template()


    def load_template(self):
        print("load TEMPLAT")
        groupbox = QGroupBox(self.active_module_template)
        self.active_module_adreass=self.active_module_template
        layout = QVBoxLayout()
        self.save_button = QPushButton("Save and send template")

        self.save_button.clicked[bool].connect(self.send_template)

        layout.addWidget(self.save_button)

        self.pin_buttoms=[]

        for i in self.template_msg.pin_configs:
            pin_interface = {}


            h_layout = QHBoxLayout()
                  
            label_1 = QLabel("Pin number: "+str(i.pin_number))

            h_layout.addWidget(label_1)

            label_2 = QLabel("Service name: ")

            h_layout.addWidget(label_2)
            lineEdit =  QLineEdit()
            lineEdit.setText(i.service_name)

            pin_interface["service_name"] = lineEdit

            h_layout.addWidget(lineEdit)

            button_group= QButtonGroup()
            radio_layout = QHBoxLayout()
            self.template_config_list=[]
            for j in i.available_config:
                config_chose= QRadioButton(j)
                self.template_config_list.append(config_chose)
                if j == i.actual_config:
                    config_chose.setChecked(True)

                radio_layout.addWidget(config_chose)
                button_group.addButton(config_chose)

            button_group.setExclusive(True)   
            pin_interface["buttoms"]=button_group
            #button_group.set_layout(radio_layout)
            h_layout.addLayout(radio_layout)
            
            self.pin_buttoms.append(pin_interface)

            h_layout.addStretch()
            layout.addLayout(h_layout)


        layout.addStretch()
        groupbox.setLayout(layout)

        self.templatebox=groupbox
        self._layout.insertWidget(self._layout.count()-1,groupbox)
        self.active_module_template="None"

        pass

    def delete_template_layout(self):

        self.templatebox.deleteLater()
        print("deliting trem")
        pass


    def send_template(self):

        template_msgs=ConfigSetRequest
        c=0
        for i in self.pin_buttoms:
            self.template_msg.pin_configs[c] 
            #template_msgs.config.pin_configs[c].pin_number = i
            self.template_msg.pin_configs[c] .actual_config = i["buttoms"].checkedButton().text()
            if i["buttoms"].checkedButton().text()=="empty":
                self.template_msg.pin_configs[c] .service_name = ""
            else:
                self.template_msg.pin_configs[c] .service_name = i["service_name"].text()
            #print(i["service_name"].text())
            #print(i["buttoms"].checkedButton().text())
            c=c+1
        #print(self.template_msg)
        print('Sending config')
        #print(self.active_module_adreass+"config_set_new")
        
        write_proxy = rospy.ServiceProxy(self.active_module_adreass+"config_set_new", ConfigSet)

        response = write_proxy(self.template_msg)   


    def update_values(self):
        #print("update values")
        #print(self.param_list)
        #print(self.input_interface_dict)

        if self.active_module_template !="None":
            try:
                self.delete_template_layout()
            except:
                pass
            self.load_template()

        for param in self.output_interface_dict:


            value=rospy.get_param(param)
            #print(value)
            label=self.output_interface_dict[param]
            if value==False:
                label.setStyleSheet("border: 1px solid black; background-color: black")
            elif value==True:    
                label.setStyleSheet("border: 1px solid black; background-color: green")

        for param in self.input_interface_dict:
            value=self.input_interface_dict[param].isChecked() 
            rospy.set_param(param,value)
            

        pass

    def demo_test(self):

        rospy.set_param(self._sim_namespace+'modul_1/celinder/value',True)
        rospy.set_param(self._sim_namespace+'modul_1/celinder/type',"DO")

        rospy.set_param(self._sim_namespace+'modul_1/koncno/value',False)
        rospy.set_param(self._sim_namespace+'modul_1/koncno/type',"DI")

        rospy.set_param(self._sim_namespace+'modul_2/pihanje/value',False)
        rospy.set_param(self._sim_namespace+'modul_2/pihanje/type',"DO")
        
        pass

    #def trigger_configuration(self):
        # Comment in to signal that the plugin has a way to configure
        # This will enable a setting button (gear icon) in each dock widget title bar
        # Usually used to open a modal configuration dialog