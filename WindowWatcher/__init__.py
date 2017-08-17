# -*- coding: utf-8 -*-

# Contains LGPL code of PyHooked: https://github.com/ethanhs/pyhooked

import eg

eg.RegisterPlugin(
    name = "WindowWatcher",
    author = "David Perry <d.perry@utoronto.ca>",
    version = "0.0.1",
    kind = "other",
    description = "Detect changes in Windows.",
    url = "https://github.com/Boolean263/EventGhost-WindowWatcher",
    guid = "{051a79aa-80f7-4150-bead-538537d17dd5}",
)

import wx
import win32gui
from eg.WinApi.Utils import GetWindowProcessName
from eg.WinApi import GetWindowText, GetClassName

from threading import Event, Thread

class WindowWatcher(eg.PluginBase):
    stopThreadEvent = None
    interval = 1.0
    lastWindow = None
    showFocus = True
    showBlur = False
    showOpen = False
    showClose = False
    setAsFound = False
    allWindows = set()

    def __init__(self):
        #print "WindowWatcher inited"
        pass

    def __start__(self):
        if self.showOpen or self.showClose:
            self.allWindows = self.GetAllWindows()
        self.stopThreadEvent = Event()
        thread = Thread(
                target = self.ThreadLoop,
                args = (self.stopThreadEvent, )
        )
        thread.start()

    def __stop__(self):
        self.stopThreadEvent.set()

    def __close__(self):
        print "WindowWatcher closed"
        pass

    def GetAllWindows(self):
        s = set()
        def cb(hwnd, args):
            s.add(hwnd)
            return True

        win32gui.EnumWindows(cb, None)
        return s


    def WindowEvent(self, eventType, window_id):
        payload = { "id": window_id }
        payload["process"] = GetWindowProcessName(window_id).upper()
        payload["title"] = GetWindowText(window_id)
        payload["class"] = GetClassName(window_id)
        payload["is_visible"] = win32gui.IsWindowVisible(window_id)
        payload["is_enabled"] = win32gui.IsWindowEnabled(window_id)

        self.TriggerEvent("{}.{}".format(eventType, payload["process"]),
            payload=payload)

        if self.setAsFound:
            eg.lastFoundWindows[:] = [window_id]

    def ThreadLoop(self, stopThreadEvent):
        while not stopThreadEvent.isSet():
            if self.showFocus or self.showBlur:
                # Figure out if the current window has changed
                thisWindow = win32gui.GetForegroundWindow()
                if thisWindow != self.lastWindow:
                    if self.showBlur:
                        self.WindowEvent("Blur", self.lastWindow)
                    if self.showFocus:
                    self.WindowEvent("Focus", thisWindow)
                    self.lastWindow = thisWindow

            if self.showOpen or self.showClose:
                # Figure out if windows have been opened or closed
                wins = self.GetAllWindows()

                if self.showOpen:
                    for w in wins - self.allWindows:
                        self.WindowEvent("Open", w)
                if self.showClose:
                    for w in self.allWindows - wins:
                        self.WindowEvent("Close", w)

                self.allWindows = wins

            # Sleep
            stopThreadEvent.wait(self.interval)
        #print("Stopped")


#
# Editor modelines  -  https://www.wireshark.org/tools/modelines.html
#
# Local variables:
# c-basic-offset: 4
# tab-width: 4
# indent-tabs-mode: nil
# coding: utf-8
# End:
#
# vi: set shiftwidth=4 tabstop=4 expandtab fileencoding=utf-8:
# :indentSize=4:tabSize=4:noTabs=true:coding=utf-8:
#
