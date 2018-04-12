"""
Main module
"""

import wx

from .ui.frame import MainFrame


def run():
    """
    Create wxPython app and mainframe
    """

    app = wx.App()

    frame = MainFrame(None)
    frame.Show()

    app.MainLoop()
