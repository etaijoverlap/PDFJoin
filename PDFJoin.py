#!/usr/bin/env python3

# This program was started as a basic graphical front-end for
# a PDF joining code I found on stackexchange:
# https://stackoverflow.com/questions/3444645/merge-pdf-files/60013100
#
# (c) 2020 Franz Schanovsky


import sys
import os
import os.path as path

sys.path.append(path.join(os.getcwd(),"env", "Lib", "site-packages"))

import wx
import wx.lib.scrolledpanel

try:
    from PyPDF2 import PdfFileReader, PdfFileWriter
except ImportError: 
    from pyPdf import PdfFileReader, PdfFileWriter

def pdf_cat(input_files, output_stream):
    writer = PdfFileWriter()
    for input_file in input_files:
        reader = PdfFileReader(input_file, strict=False)
        for n in range(reader.getNumPages()):
            writer.addPage(reader.getPage(n))
    writer.write(output_stream)

class PdfJoin(object):
    def __init__(self):
        self.window = wx.Frame(None, title = "PDF Join 4 Nicky", size=(800,600))

        self.window.SetFont(wx.Font(wx.FontInfo(15)))
        self.vsizer = wx.BoxSizer( orient=wx.VERTICAL)
        self.window.SetSizer(self.vsizer)
        self.joinsizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        self.joinbutton = wx.Button(self.window, -1, label="Join!")

        self.outfilebox = wx.StaticText(self.window, -1, "Please select a file.")
        self.outfilebox.SetBackgroundColour(wx.Colour(200,200,200))
        self.joinsizer.Add(self.outfilebox, 1, wx.ALIGN_LEFT | wx.EXPAND , 1)
        self.joinsizer.AddStretchSpacer()
        self.joinsizer.Add(self.joinbutton, 1, wx.ALIGN_RIGHT, 1)
        self.joinbutton.Disable()
        self.joinbutton.Bind(wx.EVT_BUTTON, self.do_join)

        self.addremovesizer = wx.BoxSizer(orient=wx.HORIZONTAL)
#        self.addfilebutton = wx.Button(self.window, wx.ID_ADD, label="Add file(s)")
        plusbitmap = wx.ArtProvider.GetBitmap(id=wx.ART_PLUS, client=wx.ART_BUTTON, size=wx.Size(30,30))
        self.addfilebutton = wx.BitmapButton(self.window, -1, bitmap=plusbitmap, size=wx.Size(40, 40))
        self.addfilebutton.SetBitmapPosition(wx.LEFT)
        self.addfilebutton.Bind(wx.EVT_BUTTON, self.add_file)
        self.removefilesbutton = wx.Button(self.window, -1, label="Remove all files.")
        self.removefilesbutton.Bind(wx.EVT_BUTTON, self.remove_all_files)
        self.addremovesizer.Add(self.addfilebutton, 0, wx.ALIGN_LEFT, 1)
        self.addremovesizer.AddStretchSpacer(10)
        self.addremovesizer.Add(self.removefilesbutton, 1, wx.ALIGN_RIGHT, 1)

        self.inputvsizer = wx.BoxSizer(orient=wx.VERTICAL)
        self.scrollregion = wx.lib.scrolledpanel.ScrolledPanel(self.window, style=wx.VSCROLL)
        self.scrollregion.SetSizer(self.inputvsizer)
        self.scrollregion.SetupScrolling()
        self.vsizer.Add(self.addremovesizer, 0, wx.ALIGN_TOP, 1)
        self.vsizer.Add(self.scrollregion, 1, wx.ALL | wx.EXPAND, 5)
        self.vsizer.Add(self.joinsizer, 0, wx.ALIGN_BOTTOM | wx.EXPAND, 0)

        self.input_files = []
        self.input_file_elems = [] 
        self.update_label()

    def show(self):
        self.window.Show()

    def update_label(self):
        if len(self.input_files) > 0:
            self.outfilebox.SetLabel("Join %d files." % len(self.input_files))
            self.joinbutton.Enable(True)
            self.removefilesbutton.Enable(True)
        else:
            self.outfilebox.SetLabel("Please add PDF files.")
            self.joinbutton.Enable(False)
            self.removefilesbutton.Enable(False)


    def remove_all_files(self, event):
        self.input_files.clear()
        self.inputvsizer.Clear(delete_windows=True)
        self.input_files.clear()
        self.update_label()

    def remove_file(self, event):
        filebox = event.GetEventObject().toremove
        filename = event.GetEventObject().filename
        filebox.Clear(delete_windows=True)
        filebox.removeline.Destroy()
        self.inputvsizer.Remove(filebox)
        self.input_files.remove(filename)
        self.input_file_elems.remove(filebox)
        self.show()
        self.update_label()
        self.window.Layout()

    def add_file(self, event):
        with wx.FileDialog(self.window, "Please choose a file.", wildcard="PDF files (*.pdf)|*.pdf",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_MULTIPLE) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return     # the user changed their mind

            # save the current contents in the file
            for filename in fileDialog.GetPaths():
                if filename in self.input_files:
                    continue
                self.input_files.append(filename)
                filebox = wx.BoxSizer(orient=wx.HORIZONTAL)
                filelabel = wx.StaticText(self.scrollregion, -1, path.basename(filename))
                filelabel.SetBackgroundColour(wx.Colour(230,230,230))
                filelabel.SetToolTip(filename)
                fileremovebutton = wx.BitmapButton(self.scrollregion, -1, bitmap=wx.ArtProvider.GetBitmap(wx.ART_DELETE, client=wx.ART_BUTTON, size=wx.Size(30,30)), size=wx.Size(40,40))
                fileremovebutton.toremove = filebox
                fileremovebutton.filename = filename
                filebox.Add(filelabel, 1, wx.ALIGN_LEFT | wx.EXPAND)
                #filebox.AddStretchSpacer()
                filebox.Add(fileremovebutton, 0, wx.ALIGN_RIGHT)
                self.inputvsizer.Add(filebox, 0, wx.EXPAND)
                filebox.removeline = wx.StaticLine(self.scrollregion)
                self.inputvsizer.Add(filebox.removeline, 0, 0 )
                fileremovebutton.Bind(wx.EVT_BUTTON, self.remove_file)
                self.input_file_elems.append(filebox)
        self.update_label()
        self.scrollregion.Fit()
        self.window.Layout()

    def do_join(self, event):
        with wx.FileDialog(self.window, "Please choose a file.", wildcard="PDF files (*.pdf)|*.pdf",
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return     # the user changed their mind

            # save the current contents in the file
            filename = fileDialog.GetPath()
         
            try:
                stream = open(filename, "wb")
                pdf_cat(self.input_files, stream)
                wx.MessageBox("Joined data written to %s" % filename, "SUCCESS", wx.OK, self.window)
                self.remove_all_files(None)
            except Exception as e:
                wx.MessageBox("Failed to write data to %s: %s" % (filename, str(e)), "FAILED",  wx.OK, self.window)
                raise

if __name__ == '__main__':
    app = wx.App()    
    window = PdfJoin()
    window.show()
    app.MainLoop()


    