#!/usr/bin/env python
# -*- coding: utf-8 -*-

#TODO: add display of current parameters (frequency and voltage)
#TODO: add manual controls of the function generator
# that is some controls to turn output on/off, set Voltage and frequency
#TODO: think of something more elegant (generators? threads?) than list inflating
#TODO:? add scripting so that any command can be sent to the device with
# pyVISA interface of read, write or ask.

from __future__ import division
import csv

import wx
import wx.grid
from pyfuncgen import FuncGenFrame
import pyagilent

PROTOCOLCOLS = [
                ('Stage', str),
                ('t, min', int), 
                ('start Upp, V', float), 
                ('start f, Hz', float), 
                ('end Upp, V', float), 
                ('end f, Hz', float),
                ('No of points', int),
                ]

class AgilentFrame(FuncGenFrame):
    """GUI to control Agilent Function Generator"""
    def __init__(self, *args, **kwargs):
        FuncGenFrame.__init__(self, *args, **kwargs)
        self.init_device_choice()
        self.init_grid()
        self.timer = wx.Timer()
        self.Bind(wx.EVT_TIMER, self.advance, self.timer)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.fg = None
        self.Layout()
        self.Fit()
        
    def init_device_choice(self):
        """Init device choise combo box"""
        self.deviceChoice.SetItems(pyagilent.get_devices())
        self.deviceChoice.SetSelection(0)
        
    def init_grid(self):
        """Init protocol grid"""
        self.protocolGrid.CreateGrid(3, len(PROTOCOLCOLS))
        self.protocolGrid.EnableDragRowSize(0)
        for i, item in enumerate(PROTOCOLCOLS):
            title, format = item
            self.protocolGrid.SetColLabelValue(i, title)
    
    def OnClose(self, evt):
        #TODO: try to poll the device if it is connected
        if self.fg:
            if self.connectBtn.GetValue():
                self.fg.disconnect()
                self.fg.clear_display()
            self.fg.close()
        evt.Skip()
        
    def OnDevListRefresh(self, evt):
        self.init_device_choice()
        evt.Skip()
        
    def OnToggleConnect(self, evt):
        """Handler for Connect/Dicsonnect device button."""
        evt.Skip()
        if self.connectBtn.GetValue():# button was pressed
            self.connect()
        else: #button was depressed
            self.disconnect()

    def connect(self):
        self.fg = pyagilent.AgilentFuncGen(self.deviceChoice.GetStringSelection())
        self.fg.connect()
        if self.fg.dev:
            if not self.connectBtn.GetValue():
                self.connectBtn.SetValue(True)
            self.connectBtn.SetLabel('disconnect')
            return True
        else:
            self.OnError('Can not connect to device %s'%self.fg.devicename)
            self.connectBtn.SetValue(0)
            return False

    def disconnect(self):
        self.fg.disconnect()
        self.fg.close()
        self.connectBtn.SetValue(False)
        self.connectBtn.SetLabel('connect')

    def OnAddRow(self, evt):
        """Handler for Add Row button."""
        mesg = self.protocolGrid.AppendRows(1)
        if not mesg:
            self.OnError('Could not append row')
        evt.Skip()
        
    def OnSaveFile(self, evt):
        """Saving grid content as CSV."""
        filedlg = wx.FileDialog(self, style=wx.FD_SAVE)
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
        filedlg = wx.FileDialog(self)
        if filedlg.ShowModal() != wx.ID_OK:
            filedlg.Destroy()
            return
        filename = filedlg.GetFilename()
        filedlg.Destroy()
        data = self.read_data(filename)
        if data:
            self.set_grid_data(data)
        
    def OnStart(self, evt):
        """Start executing protocol from the grid.
        
        several different timers one after another was too problematic,
        so the dirty hack is to inflate lists of parameters and flatten it
        to 1-dimensional list of "states" which all have the same structure. 
        """
        #check that device is connected - simply checks the widget state
        if not self.connectBtn.GetValue():
            if not self.connect():
                evt.Skip()
                return
            
        #check if the timer is already running or paused
        if self.timer.IsRunning() or self.pauseBtn.GetValue():
            evt.Skip()
            return
        
        data = self.get_grid_data()
        out = []
        
        for row in data:
            #TODO: devise smth smarter here (dict?)
            stage, T, Ustart, Fstart, Uend, Fend, Nstates = row
            if Nstates < 1:
                self.OnError('Number of states is incorrect')
                return
            elif Nstates == 1:
                if Ustart == Uend and Fstart == Fend:
                    dU = 0
                    dF = 0
                    dT = T*60
                else:
                    self.OnError("Number of states is incorrect")
                    return
            else:
                dU = (Uend - Ustart) / (Nstates - 1)
                dF = (Fend - Fstart) / (Nstates - 1)
                dT = T * 60 / Nstates
            # inflating the (multi)dimensional list of heterogenious 
            # values into 1-dim list of (similar) states
            Us = [Ustart + dU*i for i in range(Nstates)]
            Fs = [Fstart + dF*i for i in range(Nstates)]
            Tremain = [T*60 - dT*i for i in range(Nstates)]
            item = zip([stage,]*Nstates, Us, Fs, Tremain, [dT,]*Nstates)
            out.extend(item)

        self.protocol = iter(out[1:]) #returns empty iterator when len(out)==1
        stage0, U0, F0, Tremain0, dT0 = out[0]
        self.apply_state(U0, F0)
        self.fg.out_on()
        self.update_display(stage0, U0, F0, Tremain0)
        self.timer.Start(dT0*1000)
        
        evt.Skip()
        
    def OnStop(self, evt):
        self.finish()
        evt.Skip()
        
    def OnTogglePause(self, evt):
        if self.pauseBtn.GetValue():
            self.pauseBtn.SetLabel("CONTINUE")
            print 'pausing'
            self.timer.Stop()
        else:
            self.pauseBtn.SetLabel("PAUSE")
            print 'continuing'
            self.timer.Start()
        
    def OnError(self, mesg):
        if mesg:
            dlg = wx.MessageDialog(self, mesg, 'Error', style=wx.OK|wx.ICON_ERROR)
            dlg.ShowModal()
    
    def OnCleanRows(self, evt):
        self.clean_rows()
        evt.Skip()
        
    def advance(self, evt):
        """Perform next step of iteration"""
        try:
            stage, U, F, Tremain, dT = self.protocol.next()
        except StopIteration:
            self.finish()
        else:
            self.apply_state(U, F)
            self.timer.Start(dT*1000) 
            self.update_display(stage, U, F, Tremain)
    
    def finish(self):
        """Finishes the execution of the protocol"""
        self.timer.Stop()
        self.fg.out_off()
        self.fg.clear_display()
        wx.MessageBox('Finished', 'Info')

    def apply_state(self, u, f):
        self.fg.set_freq(f)
        self.fg.set_volt(u)
        
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
        self.protocolGrid.ClearGrid()
        rownumdata = len(data)
        rownumgrid = self.protocolGrid.GetNumberRows()
        if rownumdata > rownumgrid:
            toadd = rownumdata - rownumgrid
            self.protocolGrid.AppendRows(toadd)
        for rownum, row in enumerate(data):
            for colnum, value in enumerate(row):
                self.protocolGrid.SetCellValue(rownum, colnum, value)
        self.clean_rows()
                    
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
    agilentApp = wx.PySimpleApp(False)
    frame = AgilentFrame(None, -1)
    frame.Show()
    agilentApp.MainLoop()
