# pylint has troubles importing from gi.repository because
# it uses introspection
# pylint: disable=E0611
#from gi.repository import GLib
from gi.repository import Gtk
# pylint: disable=F0401
from gi.repository.Gtk import SizeGroupMode
from gi.repository import Gdk

from reportclient import _
from froslogging import info, warn
import os

class Controls(Gtk.Window):
    #  selected plugin
    controller = None

    def __update_progressbar(self, percent):
        self.progress.set_visible(True)
        self.progress.set_fraction(percent / 100)  # progressbar uses promiles
        # xgettext:no-c-format
        self.progress.set_text("Encoding: {0!s}% complete".format(percent))

    def __area_selected(self, result):
        if result is True:
            self.rec_button.set_sensitive(True)

    def __init__(self, controller):
        Gtk.Window.__init__(self)
        self.controller = controller
        self.controller.SetProgressUpdate(self.__update_progressbar)
        buttons_size_group = Gtk.SizeGroup(SizeGroupMode.BOTH)
        main_vbox = Gtk.VBox()
        main_hbox = Gtk.HBox()
        # pylint: disable=E1101
        self.add(main_vbox)
        # pylint: disable=E1101
        self.set_decorated(False)

        # move away from the UI!
        self.wroot = Gdk.get_default_root_window()
        self.wwidth = self.wroot.get_width()
        self.wheight = self.wroot.get_height()

        #progress bar
        self.progress = Gtk.ProgressBar()
        self.progress.set_no_show_all(True)

        #stop button
        self.stop_button = Gtk.Button(stock=Gtk.STOCK_MEDIA_STOP)
        self.stop_button.connect("clicked", self.__stop_recording__)
        self.stop_button.set_sensitive(False)
        buttons_size_group.add_widget(self.stop_button)
        main_hbox.pack_start(self.stop_button, False, False, 0)

        #start button
        self.rec_button = Gtk.Button(stock=Gtk.STOCK_MEDIA_RECORD)
        self.rec_button.connect("clicked", self.__start_recording__)
        # have to select window first
        self.rec_button.set_sensitive(False)
        buttons_size_group.add_widget(self.rec_button)
        main_hbox.pack_start(self.rec_button, False, False, 0)

        # select button
        select_button = Gtk.Button(_("Select window"))
        select_button.connect("clicked", self.controller.SelectArea, self.__area_selected)
        buttons_size_group.add_widget(select_button)
        main_hbox.pack_start(select_button, False, False, 0)

        # close button
        close_button = Gtk.Button(stock=Gtk.STOCK_CLOSE)
        close_button.connect("clicked", Gtk.main_quit)
        buttons_size_group.add_widget(close_button)
        main_hbox.pack_start(close_button, False, False, 0)

        main_vbox.pack_start(main_hbox, True, True, 0)
        main_vbox.pack_start(self.progress, True, True, 0)

        self.connect("destroy", Gtk.main_quit)

    def __stop_recording__(self, button):
        self.controller.StopScreencast(Gtk.main_quit)
        button.set_sensitive(False)
        self.rec_button.set_sensitive(True)

    def __start_recording__(self, button):
        info("start recording")
        res = self.controller.Screencast()
        if res.success:
            info("Capturing screencast to {0}".format(res.filename))
            button.set_sensitive(False)
            self.stop_button.set_sensitive(True)
