#!/usr/bin/env python
# -*- coding: utf-8 -*-
import csv
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
        self.frame.Bind(wx.EVT_CLOSE, self.OnClose)
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
    
    def OnClose(self, evt):
        #TODO: try to poll the device if it is connected
        if self.connectBtn.GetValue():
            self.fg.disconnect()
        evt.Skip()
        
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
        """Saving grid content as CSV."""
        filedlg = wx.FileDialog(self.frame, style=wx.FD_SAVE)
        if filedlg.ShowModal() != wx.ID_OK:
            filedlg.Destroy()
            return
        filename = filedlg.GetFilename()
        filedlg.Destroy()
        data = self.get_grid_data()
        self.write_data(filename, data)
        evt.Skip()
        
    def OnOpenFile(self, evt):
        """Load grid content from CSV."""
        evt.Skip()
        filedlg = wx.FileDialog(self.frame)
        if filedlg.ShowModal() != wx.ID_OK:
            filedlg.Destroy()
            return
        filename = filedlg.GetFilename()
        filedlg.Destroy()
        data = self.read_data(filename)
        self.set_grid_data(data)
        self.clean_rows()
        
    def OnToggleStart(self, evt):
        """Start executing protocol from the grid."""
        if self.startBtn.GetValue(): #button was pressed
            self.startBtn.SetLabel('Abort')
            self.start()
        else:
            self.startBtn.SetLabel('Start')
##        self.OnError('Start is not implemented')
        evt.Skip()
    
    def OnError(self, mesg):
        if mesg:
            dlg = wx.MessageDialog(self.frame, mesg, 'Error', style=wx.OK|wx.ICON_ERROR)
            dlg.ShowModal()
    
    def OnCleanRows(self, evt):
        self.clean_rows()
        evt.Skip()
        
    def start(self):
        """Perform actual protocol."""
        #TODO: check for connection, if not - connect
        data = self.get_grid_data()
        for row in data:
            #devise smth smarter here (dict?)
            stage, T, Ustart, Fstart, Uend, Fend, Nsteps = row
            dU = (Uend-Ustart)/(Nsteps-1)
            dF = (Fend-Fstart)/(Nsteps-1)
            dT = T*60/(Nsteps-1)
            self.fg.set_freq(Fstart)
            self.fg.set_volt(Ustart)
            self.fg.out_on()
            self.update_display(stage, Ustart, Fstart, T)
            for i in range(Nsteps):
                time.sleep(dT)
                U = Ustart+(i+1)*dU
                F = Fstart+(i+1)*dF
                self.fg.set_freq(F)
                self.fg.set_volt(U)
                Tremain = T*60-(i+1)*dT
                self.update_display(stage, U, F, Tremain)
            time.sleep(dT)
            
    def update_display(self, mesg, u, f, t):
        """Updates display of function generator"""
        if u:
            U = '%.2f'%u
        else:
            U = '--'
        if f:
            F = '%.2f'%f
        else:
            F = '--'
        if t:
            T = '%i:%02i'%(t//60, t%60)
        else:
            T = '--'
        line1 = "%s - %s"%(mesg, T)
        line2 = '%s Vpp | %s Hz'%(U,F)
        self.fg.set_display(line1, line2)
        
    def get_grid_data(self):
        """Returns data from the table as list of rows"""
        self.clean_rows()
        gridtable = self.protocolGrid.GetTable()
        Nrow = gridtable.GetNumberRows()
        rows = []
        for row in range(Nrow):
            line = []
            for col in range(len(PROTOCOLCOLS)):
                strval = gridtable.GetValue(row, col)
                try:
                    val = PROTOCOLCOLS[col][1](strval)
                except ValueError:
                    msg = 'Could not convert item at row %i, col %i to desired type'
                    self.OnError(msg%(row, col))
                    return
                line.append(val)
            rows.append(line)
        return rows
        
    def set_grid_data(self, data):
        """Puts the data into the protocol grid."""
        for rownum, row in enumerate(data):
            for colnum, value in enumerate(row):
                self.protocolGrid.SetCellValue(rownum, colnum, value)
                    
    def read_data(self, filename):
        """Reads data from CSV file"""
        data = []
        with open(filename, 'rb') as f:
            reader = csv.reader(f, dialect='excel')
            for row in reader:
                if len(row) != len(PROTOCOLCOLS):
                    self.OnError('Error in file formatting: %s'%filename)
                    return
                data.append(row)
        return data
    
    def write_data(self, filename, data):
        """Writes data to CSV file"""
        with open(filename, 'wb') as f:
            writer = csv.writer(f, dialect='excel')
            writer.writerows(data)
    
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
        
if __name__ == "__main__":
    app = AgilentApp(False)
    app.MainLoop()
