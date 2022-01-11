import os
import rospy
import rospkg
import rosservice


from digital_interface_msgs.srv import ConfigRead, ConfigSet,ConfigSetRequest


from qt_gui.plugin import Plugin
#from python_qt_binding import loadUi
from python_qt_binding.QtWidgets import QWidget, QGroupBox, QVBoxLayout, QCheckBox, QPushButton, QLabel, QHBoxLayout, QLineEdit
from python_qt_binding.QtCore import  QTimer

class MyPlugin(Plugin):

    def __init__(self, context):
        self._sim_namespace = "/simulate/"
        self.groupbox = None

        self.active_module_template = "None"

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

        # Create QWidget
        self._widget = QWidget()
        self._layout  = QVBoxLayout()
        self.button1 = QPushButton("Update simulation interface")
        self.button_template = QPushButton("Select RASPI template to change")

        self._layout.addWidget(self.button1)
        self._layout.addWidget(self.button_template)
        #self._layout.addStretch()
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
        self.demo_test()


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
        groupbox = QGroupBox("GroupBoxExample")

        layout=QVBoxLayout()
        for i in param_list:
            if i.find(self._sim_namespace) != -1:
  
                j = i.replace(self._sim_namespace,"")
                in_te = j.find("/")

                if in_te != -1:
                    module_name=j[0:in_te]

                    if last_module != module_name:
                        modulebox = QGroupBox(module_name)
                        #modulebox.setFixedSize(300,40)
                        module_layout = QVBoxLayout()

                        last_module = module_name
                        #self._widget.addWidget(buttom)
                        #self._context.add_widget(groupbox)

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

                        #module_layout.addWidget(buttom)
                        h_layout = QHBoxLayout()
                  
                        h_layout.addWidget(label_1)
                        label_name = QLabel(j[in_te+1:j.rfind("/")])
                        h_layout.addWidget(label_name)
                        h_layout.addStretch()
                        module_layout.addLayout(h_layout)


                        modulebox.setLayout(module_layout)
                        layout.addWidget(modulebox)



                        self.param_list.append(i.replace("type","value"))

                #self.interface_dict['new']=label_1

                #module_list.append(k)
        layout.addStretch()
        groupbox.setLayout(layout)
        self.groupbox =  groupbox
        self._layout.addWidget(groupbox)
        #self._context.add_widget(groupbox)

        
        print("updating layout")
        self.update_values()


        pass
    def select_template(self):

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

        layout.addStretch()
        groupbox.setLayout(layout)
        self._layout.addWidget(groupbox)    

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

    def load_template(self):
        print("load TEMPLAT")
        groupbox = QGroupBox(self.active_module_template)
        layout = QVBoxLayout()


        for i in self.template_msg.pin_configs:
            h_layout = QHBoxLayout()
                  
            



            label_1 = QLabel("Pin number: "+str(i.pin_number))

            h_layout.addWidget(label_1)

            label_2 = QLabel("Service name: ")

            h_layout.addWidget(label_2)
            lineEdit =  QLineEdit()
            lineEdit.setText(i.service_name)
            h_layout.addWidget(lineEdit)
            for j in i.available_config:
                config_chose= QLabel(j)
                h_layout.addWidget(config_chose)

            


            h_layout.addStretch()
            layout.addLayout(h_layout)


        layout.addStretch()
        groupbox.setLayout(layout)

        self.templatebox=groupbox
        self._layout.addWidget(groupbox)
        self.active_module_template="None"

        pass

    def delete_template_layout(self):

        self.templatebox.deleteLater()
        print("deliting trem")
        pass

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
            print(value)
            label=self.output_interface_dict[param]
            if value==False:
                label.setStyleSheet("border: 1px solid black; background-color: black")
            elif value==True:    
                label.setStyleSheet("border: 1px solid black; background-color: green")


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