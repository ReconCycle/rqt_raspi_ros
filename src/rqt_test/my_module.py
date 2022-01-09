import os
import rospy
import rospkg


from qt_gui.plugin import Plugin
#from python_qt_binding import loadUi
from python_qt_binding.QtWidgets import QWidget, QGroupBox, QVBoxLayout, QCheckBox, QPushButton, QLabel, QHBoxLayout
from python_qt_binding.QtCore import  QTimer

class MyPlugin(Plugin):

    def __init__(self, context):
        self._sim_namespace = "/simulate/"
        self.groupbox = None

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

        self._layout.addWidget(self.button1)
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
        self._update_timer.setInterval(1000)
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

        print(module_list)
        print("updating layout")
        self.update_values()


        pass
    def create_one_group(self):
        pass

    def update_values(self):
        print("update values")
        print(self.param_list)
        print(self.input_interface_dict)

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

        rospy.set_param(self._sim_namespace+'tool1/celinder/value',True)
        rospy.set_param(self._sim_namespace+'tool1/celinder/type',"DO")

        rospy.set_param(self._sim_namespace+'tool1/koncno/value',False)
        rospy.set_param(self._sim_namespace+'tool1/koncno/type',"DI")

        rospy.set_param(self._sim_namespace+'tool2/pihanje/value',False)
        rospy.set_param(self._sim_namespace+'tool2/pihanje/type',"DO")
        
        pass

    #def trigger_configuration(self):
        # Comment in to signal that the plugin has a way to configure
        # This will enable a setting button (gear icon) in each dock widget title bar
        # Usually used to open a modal configuration dialog