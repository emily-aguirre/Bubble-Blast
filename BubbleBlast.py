from cmu_graphics.cmu_graphics import *
import random
import math

# 1D Terrain Generation: Midpoint Displacement Inspiration Reference Below
# https://ijcsit.com/docs/Volume%207/vol7issue2/ijcsit20160702114.pdf 

def onAppStart(app):
    resetApp(app)

def resetApp(app):
    app.level = 1
    app.gameOver = False
    app.paused = False
    app.startBubbles = StartBubbles(app)
    app.rock = Rock()
    app.floor = Floor(0, app.height - 150, app.width)
    app.bottomBar = BottomBar(app)
    app.timer = Timer(app)
    app.ball = Ball(110, 70, 30)
    app.player = Player(app.width//2, app.floor.top)
    app.playerStep = 7
    app.projectile = Projectile(app.player.left + ((app.player.width)//2),
                    app.player.top - app.player.height, 
                    app.player.left + ((app.player.width)//2), app.player.top)
    app.levelScreen = LevelScreen(app)
    app.bLabel = BottomLabel(app)
    app.livesLabel = LivesLabel(app)
    app.textColor = 'black'
    app.background = 'white'
    app.stopTimer = False
    app.currScreen = 'startScreen'
    app.toggle = Toggle(app)
    app.toggleTouched = False
    app.labelLevel = 1
    app.removeLevelScreen = False
    app.count = 0
    app.help = HelpScreen(app)
    app.megaD = MegaDamagePowerUp()
    app.helpClicked = False
    app.ouchScreenOn = False
    app.megaDamageInUse = False
    app.megaDShown = False
    app.megaDUsed = 0
    app.maxLevel = 11
    app.gameWon = False
    app.greatJobScreenOn = False

def onStep(app):
    if app.currScreen == 'gameScreen':
        if (not app.gameOver):
            if (not app.paused and (not app.ouchScreenOn) and
                not app.greatJobScreenOn):
                updatePlayerHeight(app)
                app.timer.moveTimer(app)
                app.ball.move(app)
                checkPlayerAndBallCollision(app)
                if (len(app.projectile.projectiles) > 0):
                    app.projectile.move()
                    app.projectile.checkProjectileInCanvas(app)
                    if (not app.megaDamageInUse):
                        checkBallAndProjectileCollision(app)
                    else:
                        checkBallAndMegaDProjectileCollision(app)
                if (len(app.ball.balls) == 0):
                    app.greatJobScreenOn = True
                if ((len(app.ball.ballLocationPopped) == 2) and app.megaDShown):
                    app.megaD.move(app)
                    checkPlayerAndPowerUpCollision(app, app.megaD.cx, 
                                                app.megaD.cy, app.megaD.r)

            if (app.ouchScreenOn):
                if (app.count >= 30):
                    app.ball.reinitializeValues(app)
                    app.player.originalLocation()
                    app.timer.resetTime()
                    app.ouchScreenOn = False
                    app.count = 0
                    app.megaDShown = False
                    app.megaDamageInUse = False
                    app.projectile.projectiles = []
                    app.projectile.megaProjectiles = []
                    app.megaDUsed = 0
                else:
                    app.count += 1
            
            if (app.greatJobScreenOn):
                if (app.count >= 30):
                    app.labelLevel += 1
                    app.currScreen = 'levelScreen'
                    app.levelScreen.reinitializeValues()
                    app.removeLevelScreen = False
                    if (app.labelLevel == app.maxLevel):
                        app.gameWon = True
                    elif (app.labelLevel > 3):
                        app.level = 2
                    elif (app.labelLevel > 6):
                        app.level = 3
                    app.greatJobScreenOn = False
                    app.count = 0
                else:
                    app.count += 1

    if app.currScreen == 'levelScreen':
        if app.count >= 30:
            app.removeLevelScreen = True
            app.levelScreen.moveScreen(app)
        else:
            app.count += 1

    if app.currScreen == 'startScreen':
        app.startBubbles.moveBubbles()
        app.startBubbles.addBubbles(app)
        app.startBubbles.removeBubbles(app)
        if app.toggleTouched:
            app.toggle.move(app.toggle.direction)
            if (app.background == 'white'):
                if (app.toggle.cx >= app.width-50):
                    app.toggle.makeColorChange(app)
                    app.toggleTouched = not app.toggleTouched
            else:
                if (app.toggle.cx <= app.width-150):
                    app.toggle.makeColorChange(app)
                    app.toggleTouched = not app.toggleTouched

def onMousePress(app, mouseX, mouseY):
    if app.currScreen == 'startScreen':
        if (mouseX <= app.width//3 + 200 and mouseX >= app.width//3 and
                mouseY <= app.height//2.5 + 100 and mouseY >= app.height//2.5):
            app.currScreen = 'levelScreen'
            app.startBubbles.bubbles = []
            app.rock.updateValues(app)
            app.rock.getValues()
            if (app.background == 'white'):
                app.background = 'lightCyan'
            else:
                app.background = 'dimGray'
        if (mouseX >= app.toggle.cx - app.toggle.r and 
            mouseX <= app.toggle.cx + app.toggle.r and
            mouseY <= app.toggle.cy + app.toggle.r and
            mouseY >= app.toggle.cy - app.toggle.r):
            app.toggle.direction *= -1
            app.toggleTouched = True
        if (mouseX >= app.help.hLeft and 
            mouseX <= app.help.hLeft + app.help.hWidth and
            mouseY >= app.help.hTop and
            mouseY <= app.help.hTop + app.help.hHeight):
            app.helpClicked = True
        if (app.helpClicked):
            if (mouseX >= app.help.sLeft and 
                mouseX <= app.help.sLeft + app.help.eWidth and
                mouseY >= app.help.sTop and
                mouseY <= app.help.sTop + app.help.eHeight):
                app.helpClicked = False

def onKeyHold(app, key):
    if app.currScreen == 'gameScreen':
        if (not app.gameOver) and (not app.ouchScreenOn):
            if 'left' in key:
                checkPlayerCollision(app, key)
                app.player.move(-app.playerStep)
            if 'right' in key:
                checkPlayerCollision(app, key)
                app.player.move(app.playerStep)

def onKeyRelease(app, key):
    if app.currScreen == 'gameScreen':
        if (not app.gameOver) and (not app.ouchScreenOn):
            if 'space' in key:
                if (app.megaDUsed == 10):
                    app.megaDamageInUse = False
                    app.megaDUsed = 0
                elif ((app.megaDamageInUse) and 
                        (app.projectile.megaProjectiles == [])
                        and (app.projectile.projectiles == [])):
                    app.projectile.addProjectile(app)
                    app.megaDUsed += 1
                elif (not app.megaDamageInUse):
                    app.projectile.addProjectile(app)

def onKeyPress(app, key):
    if app.currScreen == 'gameScreen':
        if (not app.gameOver):
            if key == 'p':
                app.paused = not app.paused
        if key == 's':
            app.greatJobScreenOn = True
        if key == 'r':
            app.gameOver = not app.gameOver
            resetApp(app)
    if app.currScreen == 'wonScreen':
        if key == 'r':
            app.gameOver = not app.gameOver
            resetApp(app)

def distance(x1, y1, x2, y2):
    distance = (((x2 - x1)**2 + (y2 - y1)**2)**0.5)
    return distance

def isColliding(bX, bY, bR, x1, y1, x2, y2):
    # math below reference: https://www.geeksforgeeks.org/check-if-any-point-overlaps-the-given-circle-and-rectangle/#:~:text=In%20order%20to%20check%20whether,that%20both%20the%20shapes%20intersect 
    x = max(x1, min(bX, x2))
    y = max(y1, min(bY, y2))
    if (distance(bX, bY, x, y) <= bR):
        return True
    return False

def checkPlayerAndPowerUpCollision(app, cx, cy, r):
    d1X, d1Y = app.player.left, app.player.top
    d2X, d2Y = app.player.left + app.player.width, app.player.top
    d3X, d3Y = app.player.left, app.player.top + app.player.height
    d4X, d4Y = (app.player.left + app.player.width, 
                                            app.player.top + app.player.height)
    if (isColliding(cx, cy, r, d1X, d1Y, d4X, d4Y) or 
                    isColliding(cx, cy, r, d2X, d2Y, d3X, d3Y)):
        app.megaDamageInUse = True
        app.megaDShown = False
        app.projectile.projectiles = []
        
def checkPlayerAndBallCollision(app):
    for ball in app.ball.balls:
        cx, cy, r = ball[0], ball[1], ball[2]
        d1X, d1Y = app.player.left, app.player.top
        d2X, d2Y = app.player.left + app.player.width, app.player.top
        d3X, d3Y = app.player.left, app.player.top + app.player.height
        d4X, d4Y = (app.player.left + app.player.width, 
                                            app.player.top + app.player.height)
        if (isColliding(cx, cy, r, d1X, d1Y, d4X, d4Y) or 
                    isColliding(cx, cy, r, d2X, d2Y, d3X, d3Y)):
            resetLevel(app)

def resetLevel(app):
    if (not app.ouchScreenOn):
        app.livesLabel.currLives = app.livesLabel.currLives[1:] + [0]
        if (1 not in app.livesLabel.currLives):
            app.gameOver = True
        else:
            app.ouchScreenOn = True

def checkPlayerCollision(app, key):
    if 'left' in key:
        playerLeft = app.player.left
        afterLeftMove = playerLeft - app.playerStep
        if afterLeftMove <= 0:
            app.player.left = 0
    if 'right' in key:
        playerRight = app.player.left + app.player.width
        afterRightMove = playerRight + app.playerStep
        if afterRightMove >= app.width:
            app.player.left = app.width - app.player.width

# Algorithm below inspired from Midpoint Algorithm Reference mentioned above
def getPoints(app):
    levelOfDetail = random.randrange(3,10)
    xWidth = app.width // levelOfDetail
    start = app.floor.top - 100
    end = app.floor.top
    height = (end - start) // 2
    center = start + height
    yCoordinates = []
    for num in range(levelOfDetail):
        if num < 3:
            y = random.randrange(start, end)
        else:
            displacement = end - start
            oldEnd = end
            oldStart = start
            change = displacement // 2
            start = center - change
            end = center + change
            y = random.randrange(start, end)
            if (num != 2 and num % 2 != 0):
                start = oldStart
                end = oldEnd
        if (y == app.floor.top):
            y -= 5
        yCoordinates.append(y)
    return yCoordinates, xWidth


# top x values: in the self.drawValues its index 0 and index 4
# top y values: in the self.drawValues its index 1 and index 5
def updatePlayerHeight(app):
    for i in range(len(app.rock.drawValues)):
        values = app.rock.drawValues[i]
        if (app.player.left + app.player.width <= values[4] and 
                                                app.player.left >= values[0]):
            m = (values[5]-values[1]) / (values[4]-values[0])
            b = values[1] - (m*values[0])
            leftX = app.player.left
            rightX = app.player.left + app.player.width
            leftY = (m * leftX) + b
            rightY = (m * (rightX)) + b
            adjacent = rightX - leftX
            opposite = rightY - leftY
            angle = math.degrees(math.atan(opposite/adjacent))
            if (angle < 0):
                angle = 360 + angle
            if (app.player.rAngle != angle):
                app.player.rAngle = angle
            app.player.top = (leftY - app.player.height)
            break

class Rock():
    def __init__(self):
        self.x1, self.x4, self.y1, self.y2 = 0, 0, 0, 0
        self.yCoordinates = []
        self.terrainW = None
        self.x2 = None
        self.y4 = None 
        self.x3 = None 
        self.y3 = None 
        self.terrainH = None
        self.drawValues = []
        self.speed = 750

    def reinitializeValues(self):
        self.x1, self.x4, self.y1, self.y2 = 0, 0, 0, 0
        self.yCoordinates = []
        self.terrainW = None
        self.x2 = None
        self.y4 = None 
        self.x3 = None 
        self.y3 = None 
        self.terrainH = None
        self.drawValues = []
        self.speed = 750

    def updateValues(self, app):
        y, x = getPoints(app)
        self.yCoordinates = y
        self.terrainW = x
        self.y4 = app.floor.top
        self.y3 = app.floor.top

    def getValues(self):
        for i in range(len(self.yCoordinates)):
            self.y1 = self.yCoordinates[i]
            if (i + 1) < len(self.yCoordinates):
                self.y2 = self.yCoordinates[i+1]
            self.x2 = self.x1 + self.terrainW
            self.x3 = self.x2
            self.x4 = self.x1
            self.drawValues.append([self.x1, self.y1, self.x4, self.y4, 
                                    self.x2, self.y2, self.x3, self.y3]) 
            self.y1 = self.y2
            self.x1 = self.x2

    def draw(self):
        for value in self.drawValues:
            x1, y1, x4, y4, x2, y2, x3, y3 = value
            drawPolygon(x1, y1, x2, y2, x3, y3, x4, y4, fill='lightGray')

class Floor():
    def __init__(self, left, top, width):
        self.height = 50
        self.left = left
        self.top = top
        self.width = width

    def draw(self):
        drawRect(self.left, self.top, self.width, self.height)

class Player():
    def __init__(self, left, top):
        self.width = 50
        self.height = 50
        self.moveX = 0
        self.left = left
        self.oLeft = left
        self.top = top - self.height
        self.oTop = top - self.height
        self.color = 'red'
        self.rAngle = 0

    def originalLocation(self):
        self.top = self.oTop
        self.left = self.oLeft

    def update(self):
        self.left = self.left + self.moveX
        self.top = self.top
        self.moveX = 0
        return self.left, self.top

    def move(self, x):
        self.moveX = x

    def draw(self):
        drawRect(self.left, self.top, self.width, self.height,
                    fill=self.color, border='black', borderWidth=2,
                    rotateAngle=self.rAngle)

def checkBallAndMegaDProjectileCollision(app):
    ballCopy = []
    for ball in app.ball.balls:
        ballCopy.append(ball)
    for i in range(len(app.ball.balls)):
        if (ballCopy != app.ball.balls):
            app.ball.balls = ballCopy
            cx, cy, r, vx, vy, g = temp
            if (r >= 10):
                direction = -1
                for _ in range(2):
                    app.ball.addBall(cx, cy, r, vx, vy, g, direction)
                    direction *= -1
            break
        ball = app.ball.balls[i]
        cx, cy, r, vx, vy, g = ball
        for j in range (len(app.projectile.megaProjectiles)):
            projectile = app.projectile.megaProjectiles[j]
            x1, y1, x2, y2  = projectile
            if isColliding(cx, cy, r, x1, y1, x2, y2):
                temp = [cx, cy, r, vx, vy, g]
                app.projectile.megaProjectiles = []
                app.projectile.projectiles = []
                ballCopy.pop(i)
                break
    if (ballCopy != app.ball.balls):
        app.ball.balls = ballCopy
        cx, cy, r, vx, vy, g = temp
        if (r >= 10):
            direction = -1
            for _ in range(2):
                app.ball.addBall(cx, cy, r, vx, vy, g, direction)
                direction *= -1

def checkBallAndProjectileCollision(app):
    ballCopy = []
    for ball in app.ball.balls:
        ballCopy.append(ball)
    for i in range(len(app.ball.balls)):
        if (ballCopy != app.ball.balls):
            app.ball.balls = ballCopy
            cx, cy, r, vx, vy, g = temp
            if not (app.megaDShown):
                app.ball.ballLocationPopped = [cx, cy]
                app.megaD.changeValues(app)
            if (r >= 10):
                direction = -1
                for _ in range(2):
                    app.ball.addBall(cx, cy, r, vx, vy, g, direction)
                    direction *= -1
            break
        ball = app.ball.balls[i]
        cx, cy, r, vx, vy, g = ball
        for j in range (len(app.projectile.projectiles)):
            projectile = app.projectile.projectiles[j]
            x1, y1, x2, y2  = projectile
            if isColliding(cx, cy, r, x1, y1, x2, y2):
                temp = [cx, cy, r, vx, vy, g]
                app.projectile.projectiles.pop(j)
                ballCopy.pop(i)
                break
    if (ballCopy != app.ball.balls):
        app.ball.balls = ballCopy
        cx, cy, r, vx, vy, g = temp
        if not (app.megaDShown):
            app.ball.ballLocationPopped = [cx, cy]
            app.megaD.changeValues(app)
        if (r >= 10):
            direction = -1
            for _ in range(2):
                app.ball.addBall(cx, cy, r, vx, vy, g, direction)
                direction *= -1

class Ball():
    def __init__(self, cx, cy, r):
        self.cx = cx
        self.originalCx = cx
        self.cy = cy
        self.originalCy = cy
        self.highest = cy
        self.r = r
        self.color = 'orange'
        self.velocityX = 2
        self.originalVelocityX = 2
        self.velocityY = 0
        self.originalVelocityY = 0
        self.gravity = 2
        self.originalGravity = 2
        self.balls = [[self.cx, self.cy, self.r, self.velocityX, 
                                            self.velocityY, self.gravity]]
        self.ballLocationPopped = []

    def reinitializeValues(self, app):
        if (not app.ouchScreenOn):
            self.r = random.randrange(15,31)
            if (app.labelLevel > 8):
                self.r = random.randrange(25,46)
            if (app.labelLevel == 10):
                self.r = 45
                app.timer.change = 0.5
            self.originalCx = random.randrange(self.r + 5, app.width//2)
            self.originalCy = (random.randrange(self.r + self.r, 
                                                            app.height//2-200))
        self.balls = [[self.originalCx, self.originalCy, self.r,
                                self.originalVelocityX, self.originalVelocityY,
                                self.originalGravity]]
        if (self.r <= 20):
            if (not app.ouchScreenOn):
                self.originalCx2 = (random.randrange(app.width//2, 
                                                            app.width - 50))
            self.balls.append([self.originalCx2, self.originalCy, self.r,
                                    self.originalVelocityX, 
                                    self.originalVelocityY,
                                    self.originalGravity])
        self.ballLocationPopped = []

    def addBall(self, cx, cy, r, vx, vy, g, direction):
        g += .5
        self.balls.append([cx, cy, r//2, vx, vy, g])
        lastBall = self.balls[-1]
        lastBall[-3] *= direction
        lastBall[0] += lastBall[-3]
        lastBall[1] += lastBall[-2]

    def move(self, app):
        for ball in self.balls:
            gravity = ball[-1]
            ball[-2] += gravity
            ball[0] += ball[-3]
            ball[1] += ball[-2]
            r = ball[2]
            if (ball[1] <= self.highest) or (ball[1] + r >= app.floor.top):
                ball[-2] *= -1
                ball[-2] -= gravity
            if (ball[0] >= app.width or ball[0] <= 0):
                ball[-3] *= -1

    def draw(self):
        for ball in self.balls:
            cx, cy, r = ball[0], ball[1], ball[2]
            drawCircle(cx, cy, r, fill = self.color)

class Projectile():
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.color = 'red'
        self.speed = -15
        self.projectiles = []
        self.megaProjectiles = [] 

    def addProjectile(self, app):
        if (app.megaDamageInUse):
            mx1, my1, mx2, my2 = (app.player.left, 
                                app.player.top - app.player.height,
                                app.player.left + app.player.width,
                                app.player.top - app.player.height)
            self.projectiles.append([mx1, my1, mx2, my2])
        x1, y1, x2, y2 = (app.player.left + ((app.player.width)//2),
                        app.player.top - app.player.height, 
                    app.player.left + ((app.player.width)//2), app.player.top)
        self.projectiles.append([x1, y1, x2, y2])
        if (app.megaDamageInUse):
            storeMegaProjectileFractal(app, app.level, mx1, my1, mx2, my2,
                                            x1, y1, x2, y2)

    def checkProjectileInCanvas(self, app):
        for i in range(len(self.projectiles)):
            projectile = self.projectiles[i]
            projectileBottomEnd = projectile[-1]
            if projectileBottomEnd <= 0:
                if (app.megaDamageInUse):
                    self.megaProjectiles = []
                    self.projectiles = []
                else:
                    self.projectiles.pop(i)
                break

    def move(self):
        for projectile in self.projectiles:
            projectile[1] += self.speed
            projectile[3] += self.speed

    def draw(self, app):
        if (app.megaDamageInUse):
            for i in range(len(self.projectiles)-1):
                hx1, hy1, hx2, hy2 = self.projectiles[i]
                vx1, vy1, vx2, vy2 = self.projectiles[i+1]
                drawMegaProjectileFractal(app, app.level, hx1, hy1, hx2, hy2,
                                            vx1, vy1, vx2, vy2)
        else:
            for projectile in self.projectiles:
                drawLine(projectile[0], projectile[1], projectile[2], 
                                        projectile[3], fill = self.color)

class StartBubbles():
    def __init__(self, app):
        self.cx = random.randrange(app.width)
        self.r = random.randrange(5, 50)
        self.cy = -self.r
        self.colors = ['lightSalmon',  'khaki', 'yellowGreen', 'powderBlue',
                        'lightSteelBlue', 'cadetBlue', 'lavender', 'thistle',
                        'plum', 'darkSlateBlue', 'PaleVioletRed', 'darkMagenta',
                        'burlyWood', 'sandyBrown', 'peru', 'sienna',
                        'slateGray', 'gainsboro', 'mistyRose',
                        'aliceBlue', 'silver', 'pink', 'rosyBrown',
                        'goldenRod', 'saddleBrown', 'midnightBlue', 'skyBlue',
                        'blue', 'darkOliveGreen', 'forestGreen',
                        'mediumSeaGreen', 'darkSeaGreen', 'darkKhaki',
                        'moccasin', 'orange', 'crimson', 'fireBrick']
        self.color = random.choice(self.colors)
        self.speed = random.randrange(2, 40)
        self.bubbles = [[self.cx, self.cy, self.r, self.color, self.speed]]

    def moveBubbles(self):
        for bubble in self.bubbles:
            speed = bubble[-1]
            bubble[1] += speed

    def removeBubbles(self, app):
        for i in range(len(self.bubbles)):
            bubble = self.bubbles[i]
            cy, r = bubble[1], bubble[2] 
            if cy - r > app.height:
                self.bubbles.pop(i)
                break

    def addBubbles(self, app):
        cx, r = random.randrange(app.width), random.randrange(5, 50)
        cy = -r
        color = random.choice(self.colors)
        speed = random.randrange(2, 40)
        self.bubbles.append([cx, cy, r, color, speed])

    def draw(self):
        for bubble in self.bubbles:
            cx, cy, r, color = bubble[0], bubble[1], bubble[2], bubble[3]
            drawCircle(cx, cy, r, fill=color)

def greatJobScreen(app):
    drawRect(app.width//2 - 200, app.height//2.5, 400, 100, fill=app.textColor, 
                                                                    opacity=50)
    drawLabel('Great Job!', app.width//2, app.height//2.5 + 50,
                        size=50, bold=True, font='monospace')

def gameOverScreen(app):
    drawRect(app.width//2 - 200, app.height//2.5, 400, 100, fill=app.textColor, 
                                                                    opacity=50)
    drawLabel('GAME OVER', app.width//2, app.height//2.5 + 35,
                        size=50, bold=True, font='monospace')
    drawLabel('''Press 'R' to RESTART''', app.width//2, app.height//2.5 + 75,
                        size=25, font='monospace')

def pauseScreen(app):
    drawRect(app.width//2 - 200, app.height//2.5, 400, 100, fill=app.textColor, 
                                                                    opacity=50)
    drawLabel('GAME PAUSED', app.width//2, app.height//2.5 + 35,
                        size=50, bold=True, font='monospace')
    drawLabel('''Press 'P' again to unpause''', app.width//2, 
                app.height//2.5 + 75, size=25, font='monospace')

def ouchScreen(app):
    drawRect(app.width//2 - 200, app.height//2.5, 400, 100, fill=app.textColor, 
                                                                    opacity=50)
    drawLabel('Ouch!', app.width//2, app.height//2.5 + 50,
                        size=50, bold=True, font='monospace')

class Toggle():
    def __init__(self, app):
        self.cx = app.width-150
        self.cy = app.height-30
        self.r = 10
        self.speed = 10
        self.direction = -1
    
    def move(self, direction):
        self.cx += self.speed * direction

    def makeColorChange(self, app):
        if (app.background == 'white'):
            app.background = 'black'
            app.textColor = 'white'
        else:
            app.background = 'white'
            app.textColor = 'black'

    def draw(self, app):
        drawCircle(self.cx, self.cy, self.r, fill=app.background)

class BottomBar():
    def __init__(self, app):
        self.width = app.width
        self.left = 0
        self.top = app.floor.top + app.floor.height
        self.height = app.height - self.top
        self.color = 'tan'

    def draw(self):
        drawRect(self.left, self.top, self.width, self.height, fill=self.color)

class Timer():
    def __init__(self, app):
        self.left = 5
        self.top = app.floor. top + app.floor.height + 5
        self.oWidth = app.width - 10
        self.width = self.oWidth
        self.height = 20
        self.bLeft = 5
        self.bTop = app.floor. top + app.floor.height + 5
        self.bWidth = app.width - 10
        self.bHeight = 20
        self.color = 'darkRed'
        self.bColor = 'dimGray'
        self.change = 1

    def resetTime(self):
        self.width = self.oWidth

    def moveTimer(self, app):
        if (self.width - self.change <= 5):
            self.width = self.change
            resetLevel(app)
        elif (not app.stopTimer):
            self.width -= self.change

    def draw(self):
        drawRect(self.bLeft, self.bTop, self.bWidth, self.bHeight, 
                    fill=self.bColor, border='black', borderWidth = 2)
        drawRect(self.left, self.top, self.width, self.height, 
                    fill=self.color, border='black', borderWidth = 2)

class HelpScreen():
    def __init__(self, app):
        # values for help screen that pops up
        self.sLeft = 100 
        self.sTop = 200
        self.sWidth = app.width - 200
        self.sHeight = app.height - 400
        # values for help icon
        self.hLeft = app.width-160
        self.hTop = 10
        self.hWidth = 150
        self.hHeight = 60
        self.eWidth = 50
        self.eHeight = 30

    def draw(self, app):
        drawRect(self.hLeft, self.hTop, self.hWidth, self.hHeight, 
                    border='tomato', borderWidth=10, dashes=(20,5),
                                            fill=app.textColor)
        drawLabel('HELP', self.hLeft + (self.hWidth//2), 
                        self.hTop + (self.hHeight)//2, font='monospace', 
                        size=25, bold=True, fill=app.background)
        if (app.helpClicked):
            drawRect(self.sLeft, self.sTop, self.sWidth, self.sHeight, 
                        fill=app.textColor, border='crimson', 
                        borderWidth=2)
            drawLabel('''Press 'P' to Pause''', app.width//2, 
                        (self.sTop+(self.sHeight//5)), size = 20, 
                        font='monospace', fill=app.background)
            drawLabel('''Press 'R' to Restart''', app.width//2, 
                        (self.sTop+(self.sHeight//3.80)), size = 20, 
                        font='monospace', fill=app.background)
            drawLabel('''Press 'Space' to Shoot''', app.width//2, 
                    (self.sTop+(self.sHeight//3)), size = 20, 
                        font='monospace', fill=app.background)
            drawLabel('Use LEFT and RIGHT arrow keys', app.width//2, 
                    (self.sTop+self.sHeight//2.25), size = 20, font='monospace', 
                            fill=app.background)
            drawLabel('to move player', app.width//2, 
                    (self.sTop+self.sHeight//2), size = 20, font='monospace', 
                            fill=app.background)
            drawLabel('Get PowerUps before they touch the rocks', app.width//2, 
                    (self.sTop+self.sHeight//1.65), size = 20, font='monospace', 
                            fill=app.background)
            drawLabel('Star = Fractal PowerUp', app.width//2, 
                    (self.sTop+self.sHeight//1.45), size = 20, font='monospace', 
                            fill=app.background)
            drawLabel('Note: For balls not bouncing on floor,', app.width//2, 
                    (self.sTop+self.sHeight//1.20), size = 20, font='monospace', 
                            fill=app.background)
            drawLabel('red projectiles can only be used', app.width//2, 
                    (self.sTop+self.sHeight//1.10), size = 20, font='monospace', 
                            fill=app.background)
            drawRect(self.sLeft, self.sTop, self.sWidth, self.eHeight,
                        fill=None, border='crimson')
            drawRect(self.sLeft, self.sTop, self.eWidth, self.eHeight, 
                                                                fill='crimson')
            drawLine(self.sLeft, self.sTop, self.sLeft + self.eWidth,
                        self.sTop + self.eHeight)
            drawLine(self.sLeft, self.sTop + self.eHeight,
                        self.sLeft + self.eWidth, self.sTop)

class LevelScreen():
    def __init__(self, app):
        # Initialization below is for changing values
        self.lLeft = 0
        self.rLeft = app.width // 2
        self.lTop, self.rTop = 0, 0
        self.lWidth = app.width - (app.width//2) 
        self.rWidth = app.width - (app.width//2)
        self.lHeight = app.height
        self.rHeight = app.height
        # Initialization below is for maintaining values
        self.oLWidth = app.width - (app.width//2) 
        self.oRWidth = app.width - (app.width//2)
        self.oLHeight = app.height
        self.oRHeight = app.height
        self.oLLeft = 0
        self.oRLeft = app.width // 2
        self.oLTop, self.oRTop = 0, 0
        self.curtain = [[self.lLeft, self.lTop, self.lWidth, self.lHeight],
                        [self.rLeft, self.rTop, self.rWidth, self.rHeight]]
        self.color = 'darkSeaGreen'

    def reinitializeValues(self):
        self.lLeft, self.lTop = self.oLLeft, self.oLTop
        self.lWidth, self.lHeight = self.oLWidth, self.oLHeight
        self.rLeft, self.rTop = self.oRLeft, self.oRTop
        self.rWidth, self.rHeight = self.oRWidth, self.oRHeight
        self.curtain.append([self.lLeft, self.lTop, self.lWidth, self.lHeight])
        self.curtain.append([self.rLeft, self.rTop, self.rWidth, self.rHeight])

    def moveScreen(self, app):
        direction = -1
        for section in self.curtain:
            section[0] += 10 * direction
            direction *= -1
        if ((self.curtain[0][0] + self.curtain[0][2]) <= 0 and 
            self.curtain[1][0] >= app.width):
            self.curtain= []
            if (app.gameWon):
                app.currScreen = 'wonScreen'
            else:
                app.currScreen = 'gameScreen'
                app.count = 0
                updatePlayerHeight(app)
                if (app.labelLevel > 1):
                    app.ball.reinitializeValues(app)
                    app.player.originalLocation()
                    app.timer.resetTime()
                    app.ouchScreenOn = False
                    app.megaDShown = False
                    app.megaDamageInUse = False
                    app.projectile.projectiles = []
                    app.projectile.megaProjectiles = []
                    app.megaDUsed = 0
                    app.rock.reinitializeValues()
                    app.rock.updateValues(app)
                    app.rock.getValues()
                    updatePlayerHeight(app)

    def draw(self, app):
        for section in self.curtain:
            l, t, w, h = section
            drawRect(l, t, w, h, fill=self.color)
        if (not app.removeLevelScreen) and (not app.gameWon):
            drawRect(app.width//2 - 100, app.height//2.5, 200, 100, 
                        fill=app.textColor, opacity=50, dashes=True,
                        border='black', borderWidth=8)
            drawLabel(f'LEVEL {app.labelLevel}', app.width//2, 
                            app.height//2.5 + 50, size=30, font='monospace')

class BottomLabel():
    def __init__(self, app):
        self.left = app.width//1.5
        self.top = app.bottomBar.top+(app.bottomBar.height//2)-5
        self.width = app.width - (app.width//1.5) - 5
        self.height = app.bottomBar.height//3
        self.lColor = 'white'

    def draw(self, app):
        drawRect(self.left, self.top, self.width, self.height)
        drawLabel(f'LEVEL {app.labelLevel}', self.left + (self.width//2),
                    self.top + (self.height//2), size=20, font='monospace',
                    fill=self.lColor)

class LivesLabel():
    def __init__(self, app):
        self.left = 5
        self.top = app.bottomBar.top+(app.bottomBar.height//2)-5
        self.width = app.width - (app.width//2) + 49
        self.height = app.bottomBar.height//3
        self.lColor = 'crimson'
        self.currLives = [1, 1, 1, 1, 0, 0, 0, 0]
        self.maxLives = 8
        self.size = self.width // self.maxLives
        self.getCenters = []
        self.getTopLeft = []

    def draw(self):
        drawRect(self.left, self.top, self.width, self.height)
        for num in range(self.maxLives):
            newWidth = self.size
            drawRect(self.left + (newWidth*num), self.top+5, newWidth, 
                    self.height-10, fill='snow', border='black', borderWidth=2)
            self.getCenters.append(self.left + (newWidth*num) + (newWidth//2))
            self.getTopLeft.append(self.left + (newWidth*num))
        for i in range(len(self.currLives)):
            if (self.currLives[i] == 1):
                drawRect(self.getTopLeft[i] + 10, self.top+10, self.size-20,
                            self.height-20, fill=self.lColor)
            else:
                drawLine(self.getTopLeft[i], self.top+5, 
                        self.getTopLeft[i] + self.size, 
                        self.top+5 + self.height-10, lineWidth=2)

def storeMegaProjectileFractal(app, level, hx1, hy1, hx2, hy2,
                                            vx1, vy1, vx2, vy2):        
    if (level == 0):
        app.projectile.megaProjectiles.append([hx1, hy1, hx2, hy2])
        app.projectile.megaProjectiles.append([vx1, vy1, vx2, vy2])
    else:
        height = vy2 - vy1
        newHeight = height
        width = hx2 - hx1
        newWidth = width
        storeMegaProjectileFractal(app, level-1, (hx1-newWidth//2)+5, 
                                    hy1-newHeight+5,(hx2-(width//2))-5, 
                                    hy2-newHeight+5,
                                    hx1, hy1-newHeight+5, hx1, hy1)
        storeMegaProjectileFractal(app, level-1, (hx1+newWidth//2)+5, 
                                    hy1-newHeight+5,(hx2+(width//2))-5, 
                                    hy2-newHeight+5,
                                    hx2, hy1-newHeight+5, hx2, hy1)
        storeMegaProjectileFractal(app, level-1, hx1, hy1, hx2, hy2,
                                            vx1, vy1, vx2, vy2)

def drawMegaProjectileFractal(app, level, hx1, hy1, hx2, hy2,
                                            vx1, vy1, vx2, vy2):
    if (level == 0):
        drawLine(hx1, hy1, hx2, hy2, fill=app.megaD.color)
        drawLine(vx1, vy1, vx2, vy2, fill=app.megaD.color)
    else:
        height = vy2 - vy1
        newHeight = height
        width = hx2 - hx1
        newWidth = width
        drawMegaProjectileFractal(app, level-1, (hx1-newWidth//2)+5, 
                                    hy1-newHeight+5,(hx2-(width//2))-5, 
                                    hy2-newHeight+5,
                                    hx1, hy1-newHeight+5, hx1, hy1)
        drawMegaProjectileFractal(app, level-1, (hx1+newWidth//2)+5, 
                                    hy1-newHeight+5,(hx2+(width//2))-5, 
                                    hy2-newHeight+5,
                                    hx2, hy1-newHeight+5, hx2, hy1)
        drawMegaProjectileFractal(app, level-1, hx1, hy1, hx2, hy2,
                                            vx1, vy1, vx2, vy2)

class MegaDamagePowerUp():
    def __init__(self):
        self.cx = None
        self.cy = None
        self.r = 15
        self.points = 5
        self.color = 'mediumAquamarine'
        self.roundness = 50

    def move(self, app):
        if (self.cy >= app.player.top):
            app.megaDShown = False
            app.ball.ballLocationPopped = []
        else:
            self.cy += 5

    def changeValues(self, app):
        if (len(app.ball.ballLocationPopped) == 2):
            self.cx = app.ball.ballLocationPopped[0]
            self.cy = app.ball.ballLocationPopped[1]
            app.megaDShown = True

    def draw(self, app):
        if (not app.megaDamageInUse) and (app.megaDShown):
            drawStar(self.cx, self.cy, self.r, self.points, 
                        roundness=self.roundness, fill=self.color)

def redrawAll(app):
    if app.currScreen == 'startScreen':
        app.startBubbles.draw()
        if (app.background == 'white'):
            # Images used is art created by myself (Emily Aguirre)
            drawImage('DaySquare.png', app.width//1.4, app.height//1.65)
        else:
            drawImage('NightSquare.png', app.width//1.4, app.height//1.65)
        drawRect(app.width//2 - 100, app.height//2.5, 200, 100, fill='turquoise',
                    border='black', borderWidth=8, dashes=True)
        drawRect(0, app.height//4 - 50, app.width, 100, 
                    opacity=50, fill=app.background)
        drawLabel('RECT TIME', app.width//2, app.height//2.5 + 50,
                            size=30, font='monospace')
        drawLabel('Bubble Blast', app.width//2, app.height//4, size=75, 
                    font='monospace', bold=True,italic=True, fill=app.textColor)
        drawRect(app.width-150, app.height-50, 100, 40, fill=app.textColor)
        drawArc(app.width-150, app.height-30, 50, 40, 90, 360,
                                                        fill=app.textColor)
        drawArc(app.width-50, app.height-30, 50, 40, 0, 180,
                                                        fill=app.textColor)
        app.toggle.draw(app)
        app.help.draw(app)
    elif app.currScreen == 'levelScreen':
        app.levelScreen.draw(app)
    elif app.currScreen == 'wonScreen':
        drawLabel('!!!YOU DID IT!!!', app.width//2, app.height//4.5, 
                size=50, font='monospace', bold=True, fill=app.textColor)
        drawLabel('Bubble Blast', app.width//2, app.height//3, 
                size=50, font='monospace', bold=True, fill=app.textColor)
        drawLabel('Master', app.width//2, app.height//2.5, 
                size=50, font='monospace', bold=True, fill=app.textColor)
        drawLabel('''Press 'R' to Play Again''', app.width//2, app.height//2, 
                size=20, font='monospace', bold=True, fill=app.textColor)
        drawLabel('''perhaps victory was luck...''', app.width//2, 
                    app.height//1.85, size=20, font='monospace',
                    bold=True, fill=app.textColor)
        if (app.background == 'lightCyan'):
            # Images used is art created by myself (Emily Aguirre)
            drawImage('MasterDaySquare.png', app.width//3, app.height//1.7)
        else:
            drawImage('MasterNightSquare.png', app.width//3, app.height//1.7)
    else:
        app.bottomBar.draw()
        app.timer.draw()
        app.rock.draw()
        app.floor.draw()
        app.player.update()
        app.player.draw()
        app.ball.draw()
        app.projectile.draw(app)
        app.bLabel.draw(app)
        app.livesLabel.draw()
        app.megaD.draw(app)
        if (app.gameOver):
            gameOverScreen(app)
        if (app.paused):
            pauseScreen(app)
        if (app.ouchScreenOn):
            ouchScreen(app)
        if (app.greatJobScreenOn):
            greatJobScreen(app)

runApp(width=750, height=750)




























