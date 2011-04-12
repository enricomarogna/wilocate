#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, time, webbrowser
from core.scanHandler import *
from core.httpHandler import *
from core.optionsHandler import *
from threading import Timer


try:
  import wx
  import wx.lib.newevent
except ImportError:
  print '! Install wxPython library version 2.6 with \'sudo apt-get install python-wxgtk2.6\''
  sys.exit(1)

ID_ICON_TIMER = wx.NewId()
ID_OPEN_BROWSER=wx.NewId()
ID_START_SCAN=wx.NewId()
ID_STOP_SCAN=wx.NewId()
ID_TRIGGER_SCAN=wx.NewId()
ID_SCAN_TRIGGERED=wx.NewId()
ID_SCAN_ON_START=wx.NewId()
ID_NOT_LOC=wx.NewId()
ID_LOAD_FILE=wx.NewId()

ID_START_WEB=wx.NewId()
ID_STOP_WEB=wx.NewId()
ID_WEB_ON_START=wx.NewId()
ID_BROWSER_ON_WEB_START=wx.NewId()
ID_MENU_SCAN_STATUS=wx.NewId()
ID_MENU_SCAN=wx.NewId()

ID_MENU_OPT=wx.NewId()

ID_MENU_WEB=wx.NewId()
ID_MENU_WEB_STATUS=wx.NewId()

ID_TIMER_WEB=wx.NewId()
ID_TIMER_SCAN=wx.NewId()

WebStateUpdateEvent, WEB_STATE_EVENT = wx.lib.newevent.NewEvent()
ScanStateUpdateEvent, SCAN_STATE_EVENT = wx.lib.newevent.NewEvent()

class WilocateTaskBarIcon(wx.TaskBarIcon):

    options = {}

    def __init__(self, parent):
        wx.TaskBarIcon.__init__(self)
        self.parentApp = parent
        self.options=parent.options
        self.logoStandard = wx.Icon("html/img/logotray.png",wx.BITMAP_TYPE_PNG)
        self.CreateMenu()
        self.SetIconImage()


    def CreateMenu(self):
        self.Bind(wx.EVT_TASKBAR_RIGHT_UP, self.ShowMenu)
        self.Bind(wx.EVT_MENU, self.parentApp.OpenBrowser, id=ID_OPEN_BROWSER)
        self.Bind(wx.EVT_MENU, self.parentApp.StartWeb, id=ID_START_WEB)
        self.Bind(wx.EVT_MENU, self.parentApp.StopWeb, id=ID_STOP_WEB)
        self.Bind(wx.EVT_MENU, self.parentApp.WebOnStart, id=ID_WEB_ON_START)
        self.Bind(wx.EVT_MENU, self.parentApp.BrowserOnWebStart, id=ID_BROWSER_ON_WEB_START)
        self.Bind(wx.EVT_MENU, self.parentApp.StartScan, id=ID_START_SCAN)
        self.Bind(wx.EVT_MENU, self.parentApp.StopScan, id=ID_STOP_SCAN)
        self.Bind(wx.EVT_MENU, self.parentApp.TriggerScan, id=ID_TRIGGER_SCAN)
        self.Bind(wx.EVT_MENU, self.parentApp.TriggeredOnStart, id=ID_SCAN_TRIGGERED)
        self.Bind(wx.EVT_MENU, self.parentApp.ScanOnStart, id=ID_SCAN_ON_START)
        self.Bind(wx.EVT_MENU, self.parentApp.NotLocate, id=ID_NOT_LOC)
        self.Bind(wx.EVT_MENU, self.parentApp.LoadFile, id=ID_LOAD_FILE)
        self.Bind(wx.EVT_MENU, self.parentApp.OnExit, id=wx.ID_EXIT)
	wx.EVT_TASKBAR_LEFT_UP(self, self.parentApp.OpenBrowser)

        self.menu=wx.Menu()
        menuscan = wx.Menu()
	menuscan.Append(ID_MENU_SCAN_STATUS,"")
	menuscan.AppendSeparator()
        menuscan.Append(ID_START_SCAN, "&Start scan")
        menuscan.Append(ID_STOP_SCAN, "S&top scan")
        menuscan.AppendSeparator()
        menuscan.Append(ID_LOAD_FILE, "&Load scan from file")

        self.menu.AppendMenu(ID_MENU_SCAN, "Wifi &scan", menuscan)


        menuweb = wx.Menu()
        menuweb.Append(ID_MENU_WEB_STATUS,"")
	menuweb.AppendSeparator()
	menuweb.Append(ID_START_WEB, "&Start web interface")
        menuweb.Append(ID_STOP_WEB, "S&top web interface")
	self.menu.AppendMenu(ID_MENU_WEB, "&Web interface", menuweb)


	self.menu.AppendSeparator()

        menuopt = wx.Menu()
        menuopt.Append(ID_SCAN_ON_START, 'Run &scan at start', 'Scan at start', kind=wx.ITEM_CHECK)
        menuopt.Check(ID_SCAN_ON_START, self.options['ScanOnStart'])
	menuopt.Append(ID_NOT_LOC, 'Don\'t &locate (offline mode)', 'Don\'t locate', kind=wx.ITEM_CHECK)
        menuopt.Check(ID_NOT_LOC, self.options['NotLocate'])
	menuopt.AppendSeparator()
        menuopt.Append(ID_SCAN_TRIGGERED, "Run scan as &root at start", 'Root scan at start', kind=wx.ITEM_CHECK)
        menuopt.Check(ID_SCAN_TRIGGERED, self.options['TriggeredOnStart'])
        menuopt.AppendSeparator()
	menuopt.Append(ID_WEB_ON_START, 'Run &web interface at start', 'Web interface at start', kind=wx.ITEM_CHECK)
        menuopt.Check(ID_WEB_ON_START, self.options['WebOnStart'])
	menuopt.Append(ID_BROWSER_ON_WEB_START, 'Run &browser at start', 'Browser at start', kind=wx.ITEM_CHECK)
        menuopt.Check(ID_BROWSER_ON_WEB_START, self.options['BrowserOnWebStart'])
        self.menu.AppendMenu(ID_MENU_OPT, "&Options", menuopt)

	self.menu.AppendSeparator()
        self.menu.Append(ID_TRIGGER_SCAN, "Scan as &root")
	self.menu.AppendSeparator()
        self.menu.Append(ID_OPEN_BROWSER, "Open &browser","This will open a new Browser")
	self.menu.AppendSeparator()

	self.menu.Append(wx.ID_EXIT, "&Quit")



    def ShowMenu(self,event):
        self.PopupMenu(self.menu)

    def SetIconImage(self):
	self.SetIcon(self.logoStandard, "Wilocate")


class WilocateFrame(wx.Frame):

    scannerTimer=5

    scanRunning=False

    datahdl=None
    scanhdl=None
    httphdl=None
    httphdlfirstrun=True

    options = {}

    dialog=None
    dialogError=None
    
    browserOnStartOpened=False



    def __init__(self, parent, id, title, options):

        wx.Frame.__init__(self, parent, -1, title, size = (1, 1),
            style=wx.FRAME_NO_TASKBAR|wx.NO_FULL_REPAINT_ON_RESIZE)

	self.options = options

        self.tbicon = WilocateTaskBarIcon(self)
        self.Show(True)


	self.datahdl = dataHandler(self.options['LogPath'])
	self.scanhdl = scanHandler(self,self.options,self.datahdl)
	self.httphdl = httpHandler(self,self.datahdl,self.options['port'])

	self.scannerTimer = self.options['sleep'][0]

	self.timerweb = wx.Timer(self, -1)
	self.timerscan = wx.Timer(self, -2)
	self.Bind(wx.EVT_TIMER, self.StartWebDetached, self.timerweb)
	self.Bind(wx.EVT_TIMER, self.StartScan, self.timerscan)
	
	self.Bind(WEB_STATE_EVENT,self.WebStateUpdate)
	self.Bind(SCAN_STATE_EVENT,self.ScanStateUpdate)

	#Detach to renderize systray icon faster
	if self.options['ScanOnStart']:
	  self.scanRunning=True
	  self.timerscan.Start(self.options['sleep'][0], oneShot=True)

	if self.options['WebOnStart']:
	  self.timerweb.Start(1, oneShot=True)

    def OpenBrowser(self,event):
      webbrowser.open('http://localhost:' + str(self.options['port']))
      self.browserOnStartOpened=True

    def TriggerScan(self,event):
      """Trigger a root scan.

      It not call directly StartScan to avoid multiple scan loops.
      """

      self.GetSudoPwd()

      #newscaninfo = self.scanhdl.wifiScan(True)
      #scanthread = self.scanhdl.Scan(True)
      #scanthread.start()
      #scanthread.run()
      
      self.scanhdl.launchScan(True)
      
      #if newscaninfo:
	#scan_info = newscaninfo['timestamp'] + ' Triggered\nAPs seen ' + newscaninfo['seen'] + ', located ' + newscaninfo['located'] + '\n' + 'APs added ' + newscaninfo['newscanned'] + ', reliable ' + newscaninfo['newreliable'] + '\nNext Scan in ' + str(self.scannerTimer) + 's.'

	#itemmenu = self.tbicon.menu.FindItemById(ID_MENU_SCAN)
	#itemmenustatus = itemmenu.GetMenu().FindItemById(ID_MENU_SCAN_STATUS)
	#itemmenustatus.SetText(scan_info)


    def StartScan(self,event):
	"""Start main scan loop."""

	
	if not self.scanhdl.scanisrunning:
    
	  print 'Nuovo StartScan' 
	  self.scanhdl.scanisrunning = True
	  if self.options['TriggeredOnStart']:
	    self.GetSudoPwd()
	    #newscaninfo = self.scanhdl.
	    self.scanhdl.launchScan(self.options['TriggeredOnStart'])


	  else:
	    self.scanhdl.launchScan()
	    
	    
	    
	else:
	  print 'ANCORA NON HA FINITO'


	if self.timerscan.IsRunning():
	  self.timerscan.Stop()

	self.timerscan.Start(self.scannerTimer*1000, oneShot=True)
	print 'ASPETTO', str(self.scannerTimer*1000)
	  


    def StopScan(self,event):
      	itemmenu = self.tbicon.menu.FindItemById(ID_MENU_SCAN)
      	itemmenustatus = itemmenu.GetMenu().FindItemById(ID_MENU_SCAN_STATUS)
	itemmenustatus.SetText('Scan stopped')
	self.timerscan.Stop()
        self.scanRunning=False

	itemmenu.GetMenu().FindItemById(ID_START_SCAN).Enable(True)
	itemmenu.GetMenu().FindItemById(ID_STOP_SCAN).Enable(False)

    def ScanOnStart(self,event):
      if self.tbicon.menu.FindItemById(ID_MENU_OPT).GetMenu().FindItemById(ID_SCAN_ON_START).IsChecked():
	self.options['ScanOnStart']=True
      else:
	self.options['ScanOnStart']=False

      saveOptions()

    def WebOnStart(self,event):
      if self.tbicon.menu.FindItemById(ID_MENU_OPT).GetMenu().FindItemById(ID_WEB_ON_START).IsChecked():
	self.options['WebOnStart']=True
      else:
	self.options['WebOnStart']=False
	self.tbicon.menu.FindItemById(ID_MENU_OPT).GetMenu().Check(ID_BROWSER_ON_WEB_START, False)
	self.options['BrowserOnWebStart']=False

      saveOptions()

    def BrowserOnWebStart(self,event):
      if self.tbicon.menu.FindItemById(ID_MENU_OPT).GetMenu().FindItemById(ID_BROWSER_ON_WEB_START).IsChecked():
	self.options['BrowserOnWebStart']=True
	self.tbicon.menu.FindItemById(ID_MENU_OPT).GetMenu().Check(ID_WEB_ON_START, True)
	self.options['WebOnStart']=True
      else:
	self.options['BrowserOnWebStart']=False

      saveOptions()


    def TriggeredOnStart(self,event):
      if self.tbicon.menu.FindItemById(ID_MENU_OPT).GetMenu().FindItemById(ID_SCAN_TRIGGERED).IsChecked():
	self.options['TriggeredOnStart']=True
      else:
	self.options['TriggeredOnStart']=False

      saveOptions()

    def NotLocate(self,event):
      if self.tbicon.menu.FindItemById(ID_MENU_OPT).GetMenu().FindItemById(ID_NOT_LOC).IsChecked():
	self.options['NotLocate']=True
      else:
	self.options['NotLocate']=False

      saveOptions()

    def StartWeb(self,event):

	if not self.httphdl.isRunning():

	  if not self.timerweb.IsRunning():
	    self.timerweb.Start(1, oneShot=True)

    def StartWebDetached(self, event):

	itemmenu = self.tbicon.menu.FindItemById(ID_MENU_WEB)
	itemmenu.GetMenu().FindItemById(ID_START_WEB).Enable(False)
	itemmenu.GetMenu().FindItemById(ID_STOP_WEB).Enable(False)
	itemmenu.GetMenu().FindItemById(ID_MENU_WEB_STATUS).SetText('Starting Web interface')

	if self.httphdlfirstrun:
	  self.httphdl.start()
	  self.httphdlfirstrun=False
	else:
	  self.httphdl.run()

	#itemmenu.GetMenu().FindItemById(ID_START_WEB).Enable(False)
	#itemmenu.GetMenu().FindItemById(ID_STOP_WEB).Enable(True)

    def ScanState(self,scaninfo):
      wx.PostEvent(self, ScanStateUpdateEvent(lastscaninfo = scaninfo))

    def ScanStateUpdate(self,event):
      
      
	newscaninfo = event.lastscaninfo
	
      
	if not self.browserOnStartOpened and self.options['BrowserOnWebStart']:
	  if self.options['TriggeredOnStart']:
	    if self.options['password']:
	      self.OpenBrowser([''])
	      
	  else:
	    self.OpenBrowser([''])
	  
	scan_info = newscaninfo['timestamp'] + ' ' + newscaninfo['sudo'] + '\nAPs seen ' + newscaninfo['seen'] + ', located ' + newscaninfo['located'] + '\n' + 'APs added ' + newscaninfo['newscanned'] + ', reliable ' + newscaninfo['newreliable'] + '\nNext Scan in ' + str(self.scannerTimer) + 's.'

	itemmenu = self.tbicon.menu.FindItemById(ID_MENU_SCAN)
	itemmenustatus = itemmenu.GetMenu().FindItemById(ID_MENU_SCAN_STATUS)
	itemmenustatus.SetText(scan_info)

	itemmenu.GetMenu().FindItemById(ID_START_SCAN).Enable(False)
	itemmenu.GetMenu().FindItemById(ID_STOP_SCAN).Enable(True)

	if self.scannerTimer >= self.options['sleep'][0] and self.scannerTimer <= self.options['sleep'][1]:
	  if newscaninfo['newscanned'] == '0':
	    self.scannerTimer+=self.options['sleep'][2]
	  else:
	    self.scannerTimer=self.options['sleep'][0]

	self.scanhdl.scanisrunning = False
	print 'ok, il campo è libero'


    def WebState(self, newstate, newmsg, newdisplayerror = False):
      wx.PostEvent(self, WebStateUpdateEvent(state=newstate, msg=newmsg, displayerror=newdisplayerror))

    def WebStateUpdate(self, event):
	""" Function to update webserver state .
	
	Called by httphdl.__changeState() to notify status and message state.
	
	"""
	if event.displayerror:
	    self.dialogError = wx.MessageDialog(None, event.msg, "Error", wx.OK)
	    result = self.dialogError.ShowModal()
	    self.dialogError.Destroy()


	itemmenu = self.tbicon.menu.FindItemById(ID_MENU_WEB)
	
	if event.state:
	    self.tbicon.menu.FindItemById(ID_MENU_WEB).GetMenu().FindItemById(ID_MENU_WEB_STATUS).SetText(event.msg)
	    itemmenu.GetMenu().FindItemById(ID_MENU_WEB_STATUS).SetText(event.msg)
	    
	    itemmenu.GetMenu().FindItemById(ID_START_WEB).Enable(False)
	    itemmenu.GetMenu().FindItemById(ID_STOP_WEB).Enable(True)
	    
	    
	    if not self.browserOnStartOpened and self.options['BrowserOnWebStart']:
	      if self.options['TriggeredOnStart']:
		if self.options['password']:
		  self.OpenBrowser([''])
	      else:
		self.OpenBrowser([''])
		
	else:
	  itemmenu.GetMenu().FindItemById(ID_MENU_WEB_STATUS).SetText(event.msg)
	  itemmenu.GetMenu().FindItemById(ID_START_WEB).Enable(True)
	  itemmenu.GetMenu().FindItemById(ID_STOP_WEB).Enable(False)


    def StopWeb(self,event):
	"""Stop Web Interface"""
	if self.httphdl:
	  self.httphdl.stop()

    def GetSudoPwd(self):
      """Ask root password with a Dialog. """
      if not self.options['password']:
	self.dialog = PasswordDialog(self, -1, 'Sudo')
        result = self.dialog.ShowModal()
        self.dialog.Destroy()

    def LoadFile(self,event):

      global confdir

      dirname = confdir
      dlg = wx.FileDialog(self, "Choose a file", dirname,"", "*.*", wx.OPEN)

      if dlg.ShowModal()==wx.ID_OK:
	filename=dlg.GetFilename()
	dirname=dlg.GetDirectory()
	self.StopScan(["fakeevent"])

	scan_info="Loading file"

	itemmenu = self.tbicon.menu.FindItemById(ID_MENU_SCAN)
	itemmenustatus = itemmenu.GetMenu().FindItemById(ID_MENU_SCAN_STATUS)
	itemmenustatus.SetText(scan_info)

	itemmenu.GetMenu().FindItemById(ID_START_SCAN).Enable(False)
	itemmenu.GetMenu().FindItemById(ID_STOP_SCAN).Enable(True)

	while self.scanRunning:
	  pass

      dlg.Destroy()

    def OnExit(self,event):

      self.tbicon.RemoveIcon()
      self.tbicon.Destroy()
      self.StopWeb(["fakevent"])
      self.StopScan(["fakevent"])
      sys.exit()

class PasswordDialog(wx.Dialog):

    pwd_textctrl = None

    def __init__(self, parent, id, title):
        wx.Dialog.__init__(self, parent, id, title, size=(350,110))

        wx.StaticText(self,-1,'Insert \'sudo\' root password to run wifi scans as root.', (25, 5))
        self.pwd_textctrl = wx.TextCtrl(self, -1, '',  (100, 30), (150, -1), style=wx.TE_PASSWORD|wx.TE_PROCESS_ENTER )
        ID_PASS_BUTT = wx.NewId()
        wx.Button(self, ID_PASS_BUTT, 'Run', (130, 70))


	self.Bind(wx.EVT_TEXT_ENTER, self.PassButtPressed, self.pwd_textctrl)
	self.Bind(wx.EVT_BUTTON, self.PassButtPressed, id=ID_PASS_BUTT)
	self.parentApp = parent

    def PassButtPressed(self,event):
	pwd = self.pwd_textctrl.GetValue()
	if pwd:
	  self.parentApp.options['password']=pwd
	else:
	  wx.MessageBox('Invalid password, scan stopped.', 'Error')

	self.Hide()

def main(argv=None):

    options = loadOptions()
    options['LogPath']=genLogPath()

    app = wx.App(False)
    frame = WilocateFrame(None, -1, ' ', options)
    frame.Show(False)
    app.MainLoop()

if __name__ == '__main__':
    main()