#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time

import wx
from wx import xrc
import wx.grid #for wxGrid to be loaded from XRC

import pyagilent

PROTOCOLCOLS = [
                ('Stage', str),
                ('t, min', int), 
                ('start Upp, V', float), 
                ('start f, Hz', float), 
                ('end Upp, V', float), 
                ('end f, Hz', float),
                ('No of steps', int),
                ]

class AgilentApp(wx.App):
    """GUI to control Agilent Function Generator"""
    def OnInit(self):
        """Init method of the app"""
        self.res = xrc.XmlResource('agilentgui.xrc')
        self.init_frame()
        self.SetTopWindow(self.frame)
        self.frame.Show()
        self.fg = pyagilent.AgilentFuncGen(self.deviceChoice.GetStringSelection())
        return True
    
    def init_frame(self):
        """Load components from XRC and bind them to handlers"""
        self.frame = self.res.LoadFrame(None, 'AgilentFrame')
        self.devListRefreshBtn = xrc.XRCCTRL(self.frame, 'devListRefreshBtn')
        self.connectBtn = xrc.XRCCTRL(self.frame, 'connectBtn')
        self.deviceChoice = xrc.XRCCTRL(self.frame, 'deviceChoice')
        self.init_device_choice()
        
        self.protocolGrid = xrc.XRCCTRL(self.frame, 'protocolGrid')
        self.init_grid()
        
        self.addRowBtn = xrc.XRCCTRL(self.frame, 'wxID_ADD')
        self.cleanRowsBtn = xrc.XRCCTRL(self.frame, 'wxID_DELETE')
        self.saveFileBtn = xrc.XRCCTRL(self.frame, 'wxID_SAVE')
        self.openFileBtn = xrc.XRCCTRL(self.frame, 'wxID_OPEN')
        self.startBtn = xrc.XRCCTRL(self.frame, 'startBtn')
        
        self.connectBtn.Bind(wx.EVT_TOGGLEBUTTON, self.OnToggleConnect)
        self.devListRefreshBtn.Bind(wx.EVT_BUTTON, self.OnDevListRefresh)
        
        self.addRowBtn.Bind(wx.EVT_BUTTON, self.OnAddRow)
        self.cleanRowsBtn.Bind(wx.EVT_BUTTON, self.OnCleanRows)
        self.saveFileBtn.Bind(wx.EVT_BUTTON, self.OnSaveFile)
        self.openFileBtn.Bind(wx.EVT_BUTTON, self.OnOpenFile)
        self.startBtn.Bind(wx.EVT_TOGGLEBUTTON, self.OnToggleStart)
        
    def init_device_choice(self):
        """Init device choise combo box"""
        self.deviceChoice.SetItems(pyagilent.get_devices())
        self.deviceChoice.SetSelection(0)
        
    def init_grid(self):
        """Init protocol grid"""
        self.protocolGrid.CreateGrid(10, len(PROTOCOLCOLS))
        self.protocolGrid.EnableDragRowSize(0)
        for i, item in enumerate(PROTOCOLCOLS):
            title, format = item
            self.protocolGrid.SetColLabelValue(i, title)
        self.protocolGrid.SetMinSize((630, 210))
    
    def OnDevListRefresh(self, evt):
        self.init_device_choice()
        evt.Skip()
        
    def OnToggleConnect(self, evt):
        """Handler for Connect/Dicsonnect device button."""
        evt.Skip()
        if self.connectBtn.GetValue():# button was pressed
            self.fg.connect()
            if self.fg.dev:
                self.connectBtn.SetLabel('disconnect')
            else:
                self.OnError('Can not connect to device %s'%self.fg.devicename)
                self.ConnectBtn.SetValue(0)
        else: #button was depressed
            self.fg.disconnect()
            self.connectBtn.SetLabel('connect')
    
    def OnAddRow(self, evt):
        """Handler for Add Row button."""
        mesg = self.protocolGrid.AppendRows(1)
        if not mesg:
            self.OnError('Could not append row')
        evt.Skip()
        
    def OnSaveFile(self, evt):
        """Saving grid content as CVS."""
        data = self.table2list_ascolumns()
        self.OnError('SaveFile not implemented')
        evt.Skip()
        
    def OnOpenFile(self, evt):
        """Load grid content from CVS."""
        evt.Skip()
        filedlg = wx.FileDialog(self.frame)
        if filedlg.ShowModal() != wx.ID_OK:
            filedlg.Destroy()
            return
        filename = filedlg.GetFilename()
        filedlg.Destroy()
        data = self.read_data(filename)
        self.set_grid_data(data)
        self.OnError('OpenFile not implemented')
        
    def OnToggleStart(self, evt):
        """Start executing protocol from the grid."""
        if self.startBtn.GetValue(): #button was pressed
            self.startBtn.SetLabel('Abort')
        else:
            self.startBtn.SetLabel('Start')
        self.OnError('Start is not implemented')
        evt.Skip()
        
    def OnError(self, mesg):
        if mesg:
            dlg = wx.MessageDialog(self.frame, mesg, 'Error', style=wx.OK|wx.ICON_ERROR)
            dlg.ShowModal()
    
    def OnCleanRows(self, evt):
        self.clean_rows()
        evt.Skip()
        
    def table2list_ascolumns(self):
        self.clean_rows()
        gridtable = self.protocolGrid.GetTable()
        Nrow = gridtable.GetNumberRows()
        content = []
        for col in range(len(PROTOCOLCOLS)):
            column = []
            for row in range(Nrow):
                val = gridtable.GetValue(row, col)
            content.append(column)
        return content
    
    def clean_rows(self):
        """Removes empty rows from the bottom of the grid."""
        table = self.protocolGrid.GetTable()
        Nrows = table.GetNumberRows()
        for row in range(Nrows-1, -1, -1):
            empty = True
            for col in range(len(PROTOCOLCOLS)):
                if not table.IsEmptyCell(row, col):
                    empty = False
            if empty:
                self.protocolGrid.DeleteRows(row)
            else:
                break
        
    def read_data(self, filename):
        """Reads data from CSV file"""
        self.OnError("read_data is not implemented")
        data=None
        return data
    
    def set_grid_data(self, data):
        """Puts the data into the protocol grid."""
        self.OnError("set_grid_data is not implemented")
        
if __name__ == "__main__":
    app = AgilentApp(False)
    app.MainLoop()
