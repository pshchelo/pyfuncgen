#!/usr/bin/env python
# -*- coding: utf-8 -*-

import wx
from wx import xrc
import wx.grid #for wxGrid to be loaded from XRC

## from visa import instrument, get_instrument_list

## import pyagilent

PROTOCOLCOLS = ['Stage',
                't, min', 
                'start Upp, V', 
                'start f, Hz', 
                'end Upp, V', 
                'end f, Hz', 
                'No of steps']

DEVICENAMES = pyagilent.get_devices()
    
class AgilentApp(wx.App):
    """GUI to control Agilent Function Generator"""
    def OnInit(self):
        """Init method of the app"""
        self.res = xrc.XmlResource('agilentgui.xrc')
        self.init_frame()
        self.SetTopWindow(self.frame)
        self.frame.Show()
        return True
    
    def init_frame(self):
        """Load components from XRC and bind them to handlers"""
        self.frame = self.res.LoadFrame(None, 'AgilentFrame')
        self.connectBtn = xrc.XRCCTRL(self.frame, 'connectbtn')
        
        self.deviceChoice = xrc.XRCCTRL(self.frame, 'device_cmbox')
        self.init_device_choice()
        
        self.protocolGrid = xrc.XRCCTRL(self.frame, 'protocol_grd')
        self.init_grid()
        
        self.addRowBtn = xrc.XRCCTRL(self.frame, 'wxID_ADD')
        self.saveFileBtn = xrc.XRCCTRL(self.frame, 'wxID_SAVE')
        self.openFileBtn = xrc.XRCCTRL(self.frame, 'wxID_OPEN')
        self.startBtn = xrc.XRCCTRL(self.frame, 'startBtn')
        self.abortBtn = xrc.XRCCTRL(self.frame, 'wxID_ABORT')
        
        self.connectBtn.Bind(wx.EVT_TOGGLEBUTTON, self.OnToggleConnect)
        self.addRowBtn.Bind(wx.EVT_BUTTON, self.OnAddRow)
        self.saveFileBtn.Bind(wx.EVT_BUTTON, self.OnSaveFile)
        self.openFileBtn.Bind(wx.EVT_BUTTON, self.OnOpenFile)
        self.startBtn.Bind(wx.EVT_BUTTON, self.OnStart)
        self.abortBtn.Bind(wx.EVT_BUTTON, self.OnAbort)
        
    def init_device_choice(self):
        """Init device choise combo box"""
        for name in DEVICENAMES:
            self.deviceChoice.Append(name)
        self.deviceChoice.SetSelection(0)
        
    def init_grid(self):
        """Init protocol grid"""
        self.protocolGrid.CreateGrid(10, len(PROTOCOLCOLS))
        self.protocolGrid.EnableDragRowSize(0)
        for item in enumerate(PROTOCOLCOLS):
            self.protocolGrid.SetColLabelValue(*item)
        self.protocolGrid.SetMinSize((630, 210))
        
    def OnToggleConnect(self, evt):
        """Handler for Connect/Dicsonnect device button."""
        evt.Skip()
        devicename = self.deviceChoice.GetValue()
        if self.connectBtn.GetValue():# button was pressed
            self.device = pyagilent.connect(devicename)
            if self.device:
                self.device.write("*RST")
                self.connectBtn.SetLabel('disconnect')
            else:
                self.OnError('Can not connect to device %s'%devicename)
                self.ConnectBtn.SetValue(0)
        else: #button was depressed
            pyagilent.disconnect(self.device)
            self.connectBtn.SetLabel('connect')
    
    def OnAddRow(self, evt):
        """Handler for Add Row button."""
        mesg = self.protocolGrid.AppendRows(1)
        if not mesg:
            self.OnError('Could not append row')
        evt.Skip()
        
    def OnSaveFile(self, evt):
        """Saving grid content as CVS."""
        print('SaveFile not implemented')
        evt.Skip()
        
    def OnOpenFile(self, evt):
        """Load grid content from CVS."""
        print('OpenFile not implemented')
        evt.Skip()
        
    def OnStart(self, evt):
        """Start executing protocol from the grid."""
        print('Start not implemented')
        evt.Skip()
        
    def OnAbort(self, evt):
        """Abort executing protocol from the grid."""
        print('Abort not implemented')
        evt.Skip()
        
    def OnError(self, mesg):
        if mesg:
            dlg = wx.MessageDialog(self.frame, mesg, 'Error', style=wx.OK|wx.ICON_ERROR)
            dlg.ShowModal()
        
if __name__ == "__main__":
    app = AgilentApp(True)
    app.MainLoop()
