# -*- coding: utf-8 -*-

import wx
import random


class Tetris(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, size=(500, 680),
        style = wx.MINIMIZE_BOX |  wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)
        self.statusbar = self.CreateStatusBar()
        self.statusbar.SetFieldsCount(3)
        self.statusbar.SetStatusWidths([-1, -1, -1])

        self.statusbar.SetStatusText(u"分数："+'0',0)
        self.statusbar.SetStatusText(u"等级："+'1',1)
        self.statusbar.SetStatusText(u"速度："+u"低",2)

        self.menuBar = wx.MenuBar()
        menu = wx.Menu()
        menu.Append(100, u"详情\tF1", u"")
        self.Bind(wx.EVT_MENU, self.OnBox, id=100)
        self.menuBar.Append(menu, u"帮助")
        
        menu1 = wx.Menu()
        menu1.Append(200, u"开始\tF2", u"")
        self.Bind(wx.EVT_MENU, self.Onbegin, id=200)
        self.menuBar.Append(menu1, u"重新开始")
        
        self.SetMenuBar(self.menuBar)



        self.board = Board(self)
        self.board.SetFocusIgnoringChildren()
        self.board.start()

        self.Centre()
        self.Show(True)
        
        
    def OnBox(self, evt):
      wx.MessageBox(u"使用方法：\n上键：旋转            下键：加速\n左右键：左右移动    p：暂停/开始\n空格键：直接到底部\n",
           u"详情", wx.OK | wx.ICON_INFORMATION, self)
    
    def Onbegin(self, evt):
         self.board.restart()





class Board(wx.Panel):
    BoardWidth = 10
    BoardHeight = 22
    Speed = 600
    ID_TIMER = 1
    i=0
    k=0
    next=0

    def __init__(self, parent):
        wx.Panel.__init__(self, parent,style=wx.WANTS_CHARS )
        self.timer = wx.Timer(self, Board.ID_TIMER)
        self.isWaitingAfterLine = False
        self.curPiece = Shape(self)
        self.nextPiece = Shape(self)
        self.nextone = Shape(self)
        self.next=random.randint(1, 7)
        self.curX = 0
        self.curY = 0
        self.nScore = 0
        self.board = [0 for i in range(220)]
       

        self.isStarted = False
        self.isPaused = False
        self.isreStarted = False
        
        button = wx.Button(self, label = u'暂停/开始', pos = (390, 450), size = (75, 45))
        self.Bind(wx.EVT_BUTTON, self.Onbutton, button)

        self.InitBuffer()

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.Bind(wx.EVT_TIMER, self.OnTimer, id=Board.ID_TIMER)


        self.clearBoard()

    def Onbutton(self, evt):
        self.pause()
        self.SetFocusIgnoringChildren()

    def shapeAt(self, x, y):
        return self.board[(y * Board.BoardWidth) + x]

    def setShapeAt(self, x, y, shape):
        self.board[(y * Board.BoardWidth) + x] = shape

    def squareWidth(self):
        return 350 / Board.BoardWidth

    def squareHeight(self):
        return 680 / Board.BoardHeight
    
    def start(self):
        if self.isPaused:
            return

        self.isStarted = True
        self.isWaitingAfterLine = False
        self.nScore = 0
        self.clearBoard()
        
        statusbar = self.GetParent().statusbar
        statusbar.SetStatusText(u"分数："+str(self.nScore*10),0)
        statusbar.SetStatusText(u"等级："+'1',1)
        statusbar.SetStatusText(u"速度："+u"低",2)

        self.newPiece()
        self.timer.Start(Board.Speed)
        
    def restart(self):
        self.timer.Stop()
        if wx.MessageBox(u"确定要重新开始吗？",u"Confirmation",wx.YES_NO|wx.ICON_QUESTION,self)==wx.YES:
            self.start()
            self.SetFocusIgnoringChildren()
        else:
            self.timer.Start(Board.Speed)
        self.Refresh()
        
    def pause(self):
        if not self.isStarted:
            return

        self.isPaused = not self.isPaused
        statusbar = self.GetParent().statusbar

        if self.isPaused:
            self.timer.Stop()
            statusbar.SetStatusText('paused',0)
        else:
            self.timer.Start(Board.Speed)
            statusbar.SetStatusText(u"分数："+str(self.nScore*10),0)
        self.Refresh()
    
    def clearBoard(self):
        self.board= [0 for i in range(220)]


    def InitBuffer(self):
        size = self.GetClientSize()
        self.buffer = wx.EmptyBitmap(500, 680)
        dc = wx.BufferedDC(None, self.buffer)
        dc.SetBackground(wx.Brush(self.GetBackgroundColour()))
        dc.Clear()

        
        boardTop = size.GetHeight() - Board.BoardHeight * self.squareHeight()
        for i in range(Board.BoardHeight):
            for j in range(Board.BoardWidth):
                shape = self.shapeAt(j, Board.BoardHeight - i - 1)
                if shape != Tetrominoes.NoShape:
                    self.drawSquare(dc,
                        0 + j * self.squareWidth(),
                        boardTop + i * self.squareHeight(), shape)
             
                        
        pen=wx.BLACK_PEN
        pen.SetWidth(1)
        dc.SetPen(pen)
        while i<350:
            dc.DrawLine(i+14, 0, i+14, 680)
            i=i + self.squareWidth()

        if self.curPiece.shape() != Tetrominoes.NoShape:
            for i in range(4):
                x = self.curX + self.curPiece.x(i)
                y = self.curY - self.curPiece.y(i)
                self.drawSquare(dc, 0 + x * self.squareWidth(),
                    boardTop + (Board.BoardHeight - y - 1) * self.squareHeight(),
                    self.curPiece.shape())

               
        if self.nextone.shape() != Tetrominoes.NoShape:
            for i in range(4):
                x =   self.nextone.x(i)
                y = - self.nextone.y(i)
                self.drawSquare(dc, 0 + x * self.squareWidth()+395,
                     (Board.BoardHeight - y - 1) * self.squareHeight()-460,
                    self.next)   
        
                
        dc.DrawText(u"下一个：",365,120)        
        dc.DrawText(u"了解更多使用方法",365,380)         
        dc.DrawText(u"请阅读帮助(详情)",365,400)



    def OnPaint(self, event):
         dc = wx.BufferedPaintDC(self, self.buffer)

        
    def OnKeyDown(self, event):
        if not self.isStarted or self.curPiece.shape() == Tetrominoes.NoShape:
            event.Skip()
            return

        keycode = event.GetKeyCode()
        if keycode == ord('P') or keycode == ord('p'):
            self.pause()
            return
        if self.isPaused:
            return
        elif keycode == wx.WXK_LEFT:
            self.tryMove(self.curPiece, self.curX - 1, self.curY)
        elif keycode == wx.WXK_RIGHT:
            self.tryMove(self.curPiece, self.curX + 1, self.curY)
        elif keycode == wx.WXK_DOWN:
            self.oneLineDown()
        elif keycode == wx.WXK_UP:
            self.tryMove(self.curPiece.rotatedLeft(), self.curX, self.curY)
        elif keycode == wx.WXK_SPACE:
            self.dropDown()
        
        else:
            event.Skip()
  

    def OnTimer(self, event):
        if event.GetId() == Board.ID_TIMER:
            if self.isWaitingAfterLine:
                self.isWaitingAfterLine = False
                self.newPiece()
            else:
                self.oneLineDown()
        else:
            event.Skip()


    def dropDown(self):
        newY = self.curY
        while newY > 0:
            if not self.tryMove(self.curPiece, self.curX, newY - 1):
                break
            newY -= 1

        self.pieceDropped()

    def oneLineDown(self):
        if not self.tryMove(self.curPiece, self.curX, self.curY - 1):
            self.pieceDropped()


    def pieceDropped(self):
        for i in range(4):
            x = self.curX + self.curPiece.x(i)
            y = self.curY - self.curPiece.y(i)
            self.setShapeAt(x, y, self.curPiece.shape())

        self.removeFullLines()

        if not self.isWaitingAfterLine:
            self.newPiece()


    def removeFullLines(self):
        numFullLines = 0

        statusbar = self.GetParent().statusbar

        rowsToRemove = []

        for i in range(Board.BoardHeight):
            n = 0
            for j in range(Board.BoardWidth):
                if not self.shapeAt(j, i) == Tetrominoes.NoShape:
                    n = n + 1

            if n == 10:
                rowsToRemove.append(i)

        rowsToRemove.reverse()

        for m in rowsToRemove:
            for k in range(m, Board.BoardHeight-1):
                for l in range(Board.BoardWidth):
                        self.setShapeAt(l, k, self.shapeAt(l, k + 1))

            numFullLines = numFullLines + len(rowsToRemove)
             
            if numFullLines > 0:
                self.nScore = self.nScore + numFullLines
                statusbar.SetStatusText(u"分数："+str(self.nScore*10),0) 
                self.isWaitingAfterLine = True
                self.Refresh()

        if self.nScore > 4 and self.nScore <= 8:
            self.timer.Stop()
            Board.Speed=500
            self.timer.Start(Board.Speed)
            statusbar.SetStatusText(u"等级："+'2',1)
            statusbar.SetStatusText(u"速度："+u"较低",2)
            self.isWaitingAfterLine = True

        elif self.nScore > 8 and self.nScore <= 12:
            self.timer.Stop()
            Board.Speed=400
            self.timer.Start(Board.Speed)
            statusbar.SetStatusText(u"等级："+'3',1)
            statusbar.SetStatusText(u"速度："+u"中",2)
            self.isWaitingAfterLine = True

        elif self.nScore > 12 and self.nScore <= 16:
            self.timer.Stop()
            Board.Speed=300
            self.timer.Start(Board.Speed)
            statusbar.SetStatusText(u"等级："+'4',1)
            statusbar.SetStatusText(u"速度："+u"较高",2)
            self.isWaitingAfterLine = True

        elif self.nScore > 16:
            self.timer.Stop()
            Board.Speed=200
            self.timer.Start(Board.Speed)
            statusbar.SetStatusText(u"等级："+'5',1)
            statusbar.SetStatusText(u"速度："+u"高",2)
            self.isWaitingAfterLine = True

    def newPiece(self):
        self.curPiece = self.nextPiece
        statusbar = self.GetParent().statusbar
        self.nextPiece.setRandomShape()
        self.next=(random.randint(1,7))
        self.nextone.setShape(self.next)
        self.curX = Board.BoardWidth / 2 + 1
        self.curY = Board.BoardHeight - 1 + self.curPiece.minY()

        if not self.tryMove(self.curPiece, self.curX, self.curY):
            self.curPiece.setShape(Tetrominoes.NoShape)
            self.timer.Stop()
            self.isStarted = False
            statusbar.SetStatusText('Game over',0)
            self.restart()

    def tryMove(self, newPiece, newX, newY):
        for i in range(4):
            x = newX + newPiece.x(i)
            y = newY - newPiece.y(i)
            if x < 0 or x >= Board.BoardWidth or y < 0 or y >= Board.BoardHeight:
                return False
            if self.shapeAt(x, y) != Tetrominoes.NoShape:
                return False

        self.curPiece = newPiece
        self.curX = newX
        self.curY = newY
        self.InitBuffer()
        self.Refresh()
        return True


    def drawSquare(self, dc, x, y, shape):
        colors = ['#000000', '#CC6666', '#66CC66', '#6666CC',
                  '#CCCC66', '#CC66CC', '#66CCCC', '#DAAA00']

        light = ['#000000', '#F89FAB', '#79FC79', '#7979FC', 
                 '#FCFC79', '#FC79FC', '#79FCFC', '#FCC600']

        dark = ['#000000', '#803C3B', '#3B803B', '#3B3B80', 
                 '#80803B', '#803B80', '#3B8080', '#806200']

        pen = wx.Pen(light[shape])
        pen.SetCap(wx.CAP_PROJECTING)
        dc.SetPen(pen)

        dc.DrawLine(x, y + self.squareHeight() - 1, x, y)
        dc.DrawLine(x, y, x + self.squareWidth() - 1, y)

        darkpen = wx.Pen(dark[shape])
        darkpen.SetCap(wx.CAP_PROJECTING)
        dc.SetPen(darkpen)

        dc.DrawLine(x + 1, y + self.squareHeight() - 1,
            x + self.squareWidth() - 1, y + self.squareHeight() - 1)
        dc.DrawLine(x + self.squareWidth() - 1, 
        y + self.squareHeight() - 1, x + self.squareWidth() - 1, y + 1)

        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.SetBrush(wx.Brush(colors[shape]))
        dc.DrawRectangle(x + 1, y + 1, self.squareWidth() - 2, 
        self.squareHeight() - 2)


class Tetrominoes(object):
    NoShape = 0
    ZShape = 1
    SShape = 2
    LineShape = 3
    TShape = 4
    SquareShape = 5
    LShape = 6
    MirroredLShape = 7


class Shape(object):
    coordsTable = (
        ((0, 0),     (0, 0),     (0, 0),     (0, 0)),
        ((0, -1),    (0, 0),     (-1, 0),    (-1, 1)),
        ((0, -1),    (0, 0),     (1, 0),     (1, 1)),
        ((0, -1),    (0, 0),     (0, 1),     (0, 2)),
        ((-1, 0),    (0, 0),     (1, 0),     (0, 1)),
        ((0, 0),     (1, 0),     (0, 1),     (1, 1)),
        ((-1, -1),   (0, -1),    (0, 0),     (0, 1)),
        ((1, -1),    (0, -1),    (0, 0),     (0, 1))
    )

    def __init__(self,b):
        self.coords = [[0,0] for i in range(4)]
        self.pieceShape = Tetrominoes.NoShape
        self.board=b
        self.setShape(Tetrominoes.NoShape)

    def shape(self):
        return self.pieceShape

    def setShape(self, shape):
        table = Shape.coordsTable[shape]
        for i in range(4):
            for j in range(2):
                self.coords[i][j] = table[i][j]

        self.pieceShape = shape

    def setRandomShape(self):
        self.setShape(self.board.next)

    def x(self, index):
        return self.coords[index][0]

    def y(self, index):
        return self.coords[index][1]

    def setX(self, index, x):
        self.coords[index][0] = x

    def setY(self, index, y):
        self.coords[index][1] = y

    def minX(self):
        m = self.coords[0][0]
        for i in range(4):
            m = min(m, self.coords[i][0])

        return m

    def maxX(self):
        m = self.coords[0][0]
        for i in range(4):
            m = max(m, self.coords[i][0])

        return m

    def minY(self):
        m = self.coords[0][1]
        for i in range(4):
            m = min(m, self.coords[i][1])

        return m

    def maxY(self):
        m = self.coords[0][1]
        for i in range(4):
            m = max(m, self.coords[i][1])

        return m

    def rotatedLeft(self):
        if self.pieceShape == Tetrominoes.SquareShape:
            return self

        result = Shape(self.board)
        result.pieceShape = self.pieceShape
        for i in range(4):
            result.setX(i, self.y(i))
            result.setY(i, -self.x(i))

        return result

    def rotatedRight(self):
        if self.pieceShape == Tetrominoes.SquareShape:
            return self

        result = Shape(self.board)
        result.pieceShape = self.pieceShape
        for i in range(4):
            result.setX(i, -self.y(i))
            result.setY(i, self.x(i))

        return result


app = wx.App()
Tetris(None, -1, 'Tetris')
app.MainLoop()

