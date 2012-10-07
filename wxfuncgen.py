#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""wxPython application for controlling a function generator.

    Needs two parameters - a class to instantiate 
    a function generator representation, and a function returning list of 
    currently available/connected devices.
    
    The function generator object is expected to provide the following API:
        dev - actual lower-level representation of the device, 
            used to see if the device is connected
        connect() - connect to the device
        disconnect() - disconnect from the device
        close() - close all connections to the device 
            (possibly removing the device at all)
        set_display(*lines) - set display of the device, 
            possibly in multiple lines
        clear_display() - clear the display of the device
        ampl - set/read the current voltage amplitude
        freq - set/get the current frequency
        apply(freq, ampl) - set both amplitude and frequency at once
        output - set/get the state of device's output (on or off)
        whoami() - get some identification from the device
        minampl, maxout, ampldigits - device's min/max/precision on voltage
        freqrange, freqdigits - device's max/min/precision on frequency
        mode - get/set current output mode of the device (waveform)
"""

from __future__ import division
import csv
from math import sqrt

import wx
import wx.grid

from funcgengui import FuncGenFrame

PROTOCOLCOLS = [
                ('Stage', str),
                ('t, min', float), 
                ('start U, Vpp', float), 
                ('start F, Hz', float), 
                ('end U, Vpp', float), 
                ('end F, Hz', float),
                ('No of points', int),
                ]

class AgilentFrame(FuncGenFrame):
    """GUI to control Agilent Function Generator"""
    def __init__(self, devclass, devlist, *args, **kwargs):
        FuncGenFrame.__init__(self, *args, **kwargs)
        self.fg = None
        self.devclass = devclass
        self.devlist = devlist
        
        self.SetTitle('wxFuncGen')
        self.init_device_choice()
        self.init_grid()
        #FIXME: auto layout and fit instead of setting the frame size by hand
        self.SetSize((690,390))
        self.basetitle = self.GetTitle()
        ib = wx.Icon('res/Function_generator.png')
        self.SetIcon(ib)
        
        self.timer = wx.Timer(self, -1)
        self.Bind(wx.EVT_TIMER, self.advance, self.timer)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
        self.inactivewhenrun = [self.amplCtrl, self.freqCtrl, 
                                self.protocolGrid, self.addRowBtn,
                                self.cleanRowsBtn, self.openFileBtn,
                                self.saveFileBtn, self.connectBtn,
                                self.applyBtn, self.toggleOutputBtn,
                                self.startBtn]
        self.activewhenrun = [self.stopBtn, self.pauseBtn]
        
        
    def init_device_choice(self):
        """Init device choise combo box"""
        self.deviceChoice.SetItems(self.devlist())
        self.deviceChoice.SetSelection(0)
        
    def init_grid(self):
        """Init protocol grid"""
        self.protocolGrid.CreateGrid(3, len(PROTOCOLCOLS))
        self.protocolGrid.EnableDragRowSize(0)
        for i, item in enumerate(PROTOCOLCOLS):
            title, format = item
            self.protocolGrid.SetColLabelValue(i, title)
        
    def OnClose(self, evt):
        if self.fg:
            self.fg.clear_display()
            self.disconnect()
        evt.Skip()
        
    def OnDevListRefresh(self, evt):
        self.init_device_choice()
        evt.Skip()
        
    def OnToggleConnect(self, evt):
        """Handler for Connect/Dicsonnect device button."""
        evt.Skip()
        if self.connectBtn.GetValue():# button was pressed
            self.connect()
            self.OnApply(evt)
        else: #button was depressed
            self.disconnect()

    def connect(self):
        devname = self.deviceChoice.GetStringSelection()
        self.fg = self.devclass(devname)
        if bool(self.fg.dev):
            self.fg.connect()
            if not self.connectBtn.GetValue():
                self.connectBtn.SetValue(True)
            self.connectBtn.SetLabel('Disconnect')
            self.amplCtrl.SetDigits(self.fg.ampldigits)
            self.amplCtrl.SetRange(self.fg.minampl, 2*self.fg.maxout)
            self.freqCtrl.SetDigits(self.fg.freqdigits)
            self.freqCtrl.SetRange(*self.fg.freqrange)
            u = self.fg.ampl
            f = self.fg.freq
            self.amplCtrl.SetValue(u)
            self.freqCtrl.SetValue(f)
            self.update_display('manual')
            if self.fg.output:
                self.toggleOutputBtn.SetValue(True)
                self.toggleOutputBtn.SetLabel("Output OFF")
            else:
                self.toggleOutputBtn.SetValue(False)
                self.toggleOutputBtn.SetLabel("Output ON")
#            title = self.GetTitle()
            self.SetTitle('%s - %s'%(self.basetitle, self.fg.whoami()))
            return True
        else:
            self.fg = None
            self.OnError('Can not connect to device %s'%devname)
            self.connectBtn.SetValue(0)
            return False

    def disconnect(self):
        self.fg.disconnect()
        self.fg.close()
        self.fg = None
        self.connectBtn.SetValue(False)
        self.connectBtn.SetLabel('Connect')
        self.SetTitle(self.basetitle)
    
    def OnApply(self, evt):
        evt.Skip()
        u = self.amplCtrl.GetValue()
        f = self.freqCtrl.GetValue()
        if self.fg:
            self.fg.apply(f,u)
            self.update_display('manual')
        else:
            self.OnError('Could not apply values.\nCheck if the device is connected.')
        
    def OnToggleOutput(self, evt):
        evt.Skip()
        if self.toggleOutputBtn.GetValue():
            if not self.output_on():
                self.toggleOutputBtn.SetValue(False)
                self.OnError("Could not turn output on.\nCheck device state.")
        else:
            if not self.output_off():
                self.toggleOutputBtn.SetValue(True)
                self.OnError("Could not turn output off.\nCheck device state.")

    def output_on(self):
        try:
            self.fg.output = True
        except:
            return False
        else:
            self.toggleOutputBtn.SetValue(True)
            self.toggleOutputBtn.SetLabel('Output OFF')
            return True
        
    def output_off(self):
        try:
            self.fg.output = False
        except:
            return False
        else:
            self.toggleOutputBtn.SetValue(False)
            self.toggleOutputBtn.SetLabel('Output ON')
            return True
        
    def OnAddRow(self, evt):
        """Handler for Add Row button."""
        mesg = self.protocolGrid.AppendRows(1)
        if not mesg:
            self.OnError('Could not append row')
        evt.Skip()
        
    def OnSaveFile(self, evt):
        """Saving grid content as CSV."""
        filedlg = wx.FileDialog(self, style=wx.FD_SAVE|wx.FD_CHANGE_DIR|wx.FD_OVERWRITE_PROMPT)
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
        filedlg = wx.FileDialog(self, style = wx.FD_OPEN|wx.FD_CHANGE_DIR)
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
            #trying to connect if not yet connected
            if not self.connect():
                evt.Skip()
                return
            
        #check if the timer is already running or paused
        if self.timer.IsRunning() or self.pauseBtn.GetValue():
            evt.Skip()
            return
        
        data = self.get_grid_data()
        if len(data) == 0:
            self.OnError("No protocol specified")
            return
        out = []
        
        for item in self.inactivewhenrun:
            item.Enable(False)
        for item in self.activewhenrun:
            item.Enable(True)
        
        for row in data:
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
            # inflating the (multi)dimensional list of heterogeneous 
            # values into combined 1-dim list of states
            Us = [Ustart + dU*i for i in range(Nstates)]
            Fs = [Fstart + dF*i for i in range(Nstates)]
            Tremain = [T*60 - dT*i for i in range(Nstates)]
            item = zip([stage,]*Nstates, Us, Fs, Tremain, [dT,]*Nstates)
            out.extend(item)

        self.protocol = iter(out[1:]) #returns empty iterator when len(out)==1
        stage0, u0, f0, Tremain0, dT0 = out[0]
        self.fg.apply(f0, u0)
        self.output_on()
        self.update_display(stage0, Tremain0, dT0)
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
            if not self.leaveOutPauseCb.GetValue():
                if not self.output_off():
                    self.OnError("Could not turn output off.\nCheck device state.")
        else:
            self.pauseBtn.SetLabel("PAUSE")
            print 'continuing'
            self.timer.Start()
            if not self.leaveOutPauseCb.GetValue():
                if not self.output_on():
                    self.OnError("Could not turn output on.\nCheck device state.")
        
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
            stage, u, f, Tremain, dT = self.protocol.next()
        except StopIteration:
            self.finish()
            self.update_display('manual')
        else:
            self.fg.apply(f, u)
            self.timer.Start(dT*1000) 
            self.update_display(stage, Tremain, dT)
    
    def finish(self):
        """Finishes the execution of the protocol"""
        self.timer.Stop()
        if not self.leaveOutFinishCb.GetValue():
            self.output_off()
        wx.MessageBox('Finished', 'Info')
        for item in self.inactivewhenrun:
            item.Enable(True)
        for item in self.activewhenrun:
            item.Enable(False)
        
    def update_display(self, mesg, t=None, dt=None):
        """Updates display of function generator"""
        f = self.fg.freq
        u = self.fg.ampl
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
        if dt:
            DT = '%.3f'%dt
        else:
            DT = '--'
        line1 = "%s - %s"%(mesg, T)
        line2 = '%s Vpp | %s Hz'%(U,F)
        self.fg.set_display(line1, line2)
        self.stageDisplay.SetLabel(mesg)
        self.timeDisplay.SetLabel(T)
        self.intervalDisplay.SetLabel(DT)
        self.amplCtrl.SetValue(u)
        self.freqCtrl.SetValue(f)
        self.amplVrmsDisplay.SetLabel('%.2f Vrms'%(u/sqrt(2)/2))
        self.Layout()
        
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
    
    from devices import implemented
    agilentApp = wx.App(False)
    start_dlg = wx.SingleChoiceDialog(None,
                                      message='Choose a Function Generator',
                                      caption='Generator choice',
                                      choices=implemented)
    
    if start_dlg.ShowModal() == wx.ID_OK:
        device = start_dlg.GetStringSelection()
        start_dlg.Destroy()

        exec("from devices.%s import get_devices"%device)
        exec("from devices.%s import %s as device"%(device, device))
        
        frame = AgilentFrame(device, get_devices, parent=None, id=-1)
        frame.Show()
        agilentApp.MainLoop()
    else:
        start_dlg.Destroy()

