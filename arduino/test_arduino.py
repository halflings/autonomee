#!/usr/bin/python -tt
# Copyright (c) 2012, Fabian Affolter <fabian@affolter-engineering.ch>
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
# * Neither the name of the pyfirmata team nor the names of its contributors
#   may be used to endorse or promote products derived from this software
#   without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS ''AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import os
import sys
import time
import signal
import pyfirmata
from gi.repository import Gtk

PORT = '/dev/ttyACM0'

class UI:
    def __init__(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file(os.path.join(os.getcwd(), 'pyfirmata-gui.ui'))
        self.window = self.builder.get_object('window')
        self.aboutdialog = self.builder.get_object('aboutdialog')
        self.bt_exit = self.builder.get_object('bt_exit')
        self.bt_on = self.builder.get_object('bt_on')
        self.bt_off = self.builder.get_object('bt_off')
        self.statusbar = self.builder.get_object('statusbar')
        self.imagemenuitem5 = self.builder.get_object('imagemenuitem5')
        self.imagemenuitem10 = self.builder.get_object('imagemenuitem10')

        self.spinbutton = Gtk.SpinButton()
        self.spinbutton = self.builder.get_object('spinbutton')
        self.spinbutton.connect("changed", self.on_spin_changed)

        self.window.connect('delete-event', self.quit)
        self.bt_on.connect('clicked', self.pin_high)
        self.bt_off.connect('clicked', self.pin_low)
        self.bt_exit.connect('clicked', self.quit)
        self.imagemenuitem5.connect('activate', self.quit)
        self.imagemenuitem10.connect('activate', self.show_aboutdialog)
        self.window.show_all()
        self.pin = 2
        self.port = PORT
        self.board = pyfirmata.Arduino(self.port)
        self.statusbar.push(1, ("Connected to %s" % PORT))

    def show_aboutdialog(self, *args):
        self.aboutdialog.run()
        self.aboutdialog.hide()

    def quit(self, *args):
        Gtk.main_quit()

    def pin_high(self, pin):
        self.board.digital[int(self.pin)].write(1)

    def pin_low(self, pin):
        self.board.digital[int(self.pin)].write(0)

    def on_spin_changed(self, spin):
        self.pin = self.spinbutton.get_text()

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    signal.signal(signal.SIGTERM, signal.SIG_DFL)
    ui = UI()
    Gtk.main()