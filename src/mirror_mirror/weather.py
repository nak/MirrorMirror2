#  Docs for jquery at http://simpleweatherjs.com
import math

from datetime import datetime
from pyggi.javascript import JavascriptClass
from pyggi import javascript

_ = None


WIND_PATHS = [
        [
          -0.7500, -0.1800, -0.7219, -0.1527, -0.6971, -0.1225,
          -0.6739, -0.0910, -0.6516, -0.0588, -0.6298, -0.0262,
          -0.6083,  0.0065, -0.5868,  0.0396, -0.5643,  0.0731,
          -0.5372,  0.1041, -0.5033,  0.1259, -0.4662,  0.1406,
          -0.4275,  0.1493, -0.3881,  0.1530, -0.3487,  0.1526,
          -0.3095,  0.1488, -0.2708,  0.1421, -0.2319,  0.1342,
          -0.1943,  0.1217, -0.1600,  0.1025, -0.1290,  0.0785,
          -0.1012,  0.0509, -0.0764,  0.0206, -0.0547, -0.0120,
          -0.0378, -0.0472, -0.0324, -0.0857, -0.0389, -0.1241,
          -0.0546, -0.1599, -0.0814, -0.1876, -0.1193, -0.1964,
          -0.1582, -0.1935, -0.1931, -0.1769, -0.2157, -0.1453,
          -0.2290, -0.1085, -0.2327, -0.0697, -0.2240, -0.0317,
          -0.2064,  0.0033, -0.1853,  0.0362, -0.1613,  0.0672,
          -0.1350,  0.0961, -0.1051,  0.1213, -0.0706,  0.1397,
          -0.0332,  0.1512,  0.0053,  0.1580,  0.0442,  0.1624,
           0.0833,  0.1636,  0.1224,  0.1615,  0.1613,  0.1565,
           0.1999,  0.1500,  0.2378,  0.1402,  0.2749,  0.1279,
           0.3118,  0.1147,  0.3487,  0.1015,  0.3858,  0.0892,
           0.4236,  0.0787,  0.4621,  0.0715,  0.5012,  0.0702,
           0.5398,  0.0766,  0.5768,  0.0890,  0.6123,  0.1055,
           0.6466,  0.1244,  0.6805,  0.1440,  0.7147,  0.1630,
           0.7500,  0.1800
        ],
        [
          -0.7500,  0.0000, -0.7033,  0.0195, -0.6569,  0.0399,
          -0.6104,  0.0600, -0.5634,  0.0789, -0.5155,  0.0954,
          -0.4667,  0.1089, -0.4174,  0.1206, -0.3676,  0.1299,
          -0.3174,  0.1365, -0.2669,  0.1398, -0.2162,  0.1391,
          -0.1658,  0.1347, -0.1157,  0.1271, -0.0661,  0.1169,
          -0.0170,  0.1046,  0.0316,  0.0903,  0.0791,  0.0728,
           0.1259,  0.0534,  0.1723,  0.0331,  0.2188,  0.0129,
           0.2656, -0.0064,  0.3122, -0.0263,  0.3586, -0.0466,
           0.4052, -0.0665,  0.4525, -0.0847,  0.5007, -0.1002,
           0.5497, -0.1130,  0.5991, -0.1240,  0.6491, -0.1325,
           0.6994, -0.1380,  0.7500, -0.1400
        ]
      ]

WIND_OFFSETS = [
        {'start': 0.36, 'end': 0.11},
        {'start': 0.56, 'end': 0.16}
      ]

class WeatherAnimator(object):

    class DrawingElement(object):

        def __init__(self, element, context, canvas, draw):
            self.element = element
            self.context = context
            self.canvas = canvas
            self.draw = draw



    KEYFRAME = 5000
    STROKE = 0.08
    TAU = 2.0 * math.pi
    TWO_OVER_SQRT_2 = 2.0/math.sqrt(2.0)

    def __init__(self, context, opts = None):
        self.context = context
        self.requestAnimationFrame = \
            context.get_jsobject("webkitRequestAnimationFrame")
        self.cancelAnimationFrame =  \
            context.get_jsobject("webkitCancelAnimationFrame")
        if not self.requestAnimationFrame and not self.cancelAnimationFrame:
            self.request_interval = context.get_jsobject("window").setInterval
            self.cancel_interval = context.get_jsobject("window").cancel_Interval
        self.loop = None
        self.drawing_elems        = []
        self.interval    = None
        self.color       = (opts or {}).get('color') or "black"
        self.resizeClear = (opts or {}).get('resizeClear') or False
        self._ = context.get_jsobject('$')
        self.prev_now = (datetime.utcnow() - datetime(1970,1,1)).total_seconds()

    def request_interval(self, func, delay):
        handle = {'value': None}
        self.nativeFuncWrapper = self.context.get_jsobject("nativeFunctionWrapper")
        def handler(x):
            handle['value'] = x
        self.handler = handler
        handle["value"] = self.nativeFuncWrapper(func, self.handler)

        return handle

    def cancel_interval(self, handle):
        self.cancelAnimationFrame(handle)
        
    def draw_circle(self, context, x, y, r):
        context.beginPath()
        context.arc(x, y, r, 0, WeatherAnimator.TAU, False)
        context.fill()
        
    def draw_line(self, context, ax, ay, bx, by):
        context.beginPath()
        context.moveTo(ax, ay)
        context.lineTo(bx, by)
        context.stroke()
        
    def draw_puff(self, context, t, cx, cy, rx, ry, rmin, rmax):
        c = math.cos(t * WeatherAnimator.TAU)
        s = math.sin(t * WeatherAnimator.TAU)
        rmax -= rmin
        self.draw_circle(context,
                        cx - s * rx,
                        cy + c * ry + rmax * 0.5,
                        rmin + (1 - c * 0.5) * rmax)

    def draw_puffs(self, context, t, cx, cy, rx, ry, rmin, rmax):
        for i in reversed(range(5)):
            self.draw_puff(context, t + i / 5, cx, cy, rx, ry, rmin, rmax)

    def draw_cloud(self, context, t, cx, cy, cw, s, color):
        t /= 30000

        a = cw * 0.21
        b = cw * 0.12
        c = cw * 0.24
        d = cw * 0.28

        context.set(self.context, 'fillStyle', color)
        self.draw_puffs(context, t, cx, cy, a, b, c, d)

        context.globalCompositeOperation = 'destination-out'
        self.draw_puffs(context, t, cx, cy, a, b, c - s, d - s)
        context.globalCompositeOperation = 'source-over'
        
    def draw_sun(self, context, t, cx, cy, cw, s, color):
        t /= 120000

        a = cw * 0.25 - s * 0.5
        b = cw * 0.32 + s * 0.5
        c = cw * 0.50 - s * 0.5
      
        context.set(self.context, 'strokeStyle', color)
        context.set(self.context, 'lineWidth', s)
        context.set(self.context, 'lineCap', "round")
        context.set(self.context, 'lineJoin', "round")

        context.beginPath()
        context.arc(cx, cy, a, 0, WeatherAnimator.TAU, False)
        context.stroke()
    
        for i in reversed(range(8)):
            p = ((t + i + 1)/ 8.0) * WeatherAnimator.TAU
            cos = math.cos(p)
            sin = math.sin(p)
            self.draw_line(context, cx + cos * b, cy + sin * b, cx + cos * c, cy + sin * c) 

    def draw_moon(self, context, t, cx, cy, cw, s, color):
        t /= 15000

        a = cw * 0.29 - s * 0.5
        b = cw * 0.05
        c = math.cos(t * WeatherAnimator.TAU)
        p = c * WeatherAnimator.TAU / -16.0

        context.set(self.context, 'strokeStyle', color)
        context.set(self.context, 'lineWidth', s)
        context.set(self.context, 'lineCap', "round")
        context.set(self.context, 'lineJoin', "round")
    
        cx += c * b
    
        context.beginPath()
        context.arc(cx, cy, a, p + WeatherAnimator.TAU / 8.0, p + WeatherAnimator.TAU * 7 / 8.0, False)
        context.arc(cx + math.cos(p) * a * WeatherAnimator.TWO_OVER_SQRT_2, cy + math.sin(p) * a * 
                WeatherAnimator.TWO_OVER_SQRT_2, a, p + WeatherAnimator.TAU * 5 / 8.0, p +
                WeatherAnimator.TAU * 3 / 8.0, True)
        context.closePath()
        context.stroke()

    def draw_rain(self, context, t, cx, cy, cw, s, color):
        t /= 1350
        a = cw * 0.16
        b = float(WeatherAnimator.TAU * 11 ) / 12.0
        c = WeatherAnimator.TAU *  7 / 12.0

        context.set(self.context, 'fillStyle', color)
    
        for i in reversed(range(4)):
            p = ((t + i +1) / 4.0) % 1
            x = cx + ((i - 1.5) / 1.5) * (i == 1 or  (-1 if i == 2 else 1)) * a
            y = cy + p * p * cw
            context.beginPath()
            context.moveTo(x, y - s * 1.5)
            context.arc(x, y, s * 0.75, b, c, False)
            context.fill()

    def draw_sleet(self, context, t, cx, cy, cw, s, color):
        t /= 750

        a = cw * 0.1875
        b = WeatherAnimator.TAU * 11 / 12.0
        c = WeatherAnimator.TAU *  7 / 12.0

        context.set(self.context, 'strokeStyle', color)
        context.set(self.context, 'lineWidth', s * 0.5)
        context.set(self.context, 'lineCap', "round")
        context.set(self.context, 'lineJoin', "round")

        for i in reversed(range(4)):
            p = ((t + i) / 4.0) % 1
            x = math.floor(cx + ((i - 1.5) / 1.5) * (i == 1 or (-1 if i == 2 else 1)) * a) + 0.5
            y = cy + p * cw
            self.draw_line(context, x, y - s * 1.5, x, y + s * 1.5)
   

    def draw_snow(self, context, t, cx, cy, cw, s, color):
        t /= 3000

        a  = cw * 0.16
        b  = s * 0.75
        u  = t * WeatherAnimator.TAU * 0.7
        ux = math.cos(u) * b
        uy = math.sin(u) * b
        v  = u + WeatherAnimator.TAU / 3.0
        vx = math.cos(v) * b
        vy = math.sin(v) * b
        w  = u + WeatherAnimator.TAU * 2 / 3.0
        wx = math.cos(w) * b
        wy = math.sin(w) * b

        context.set(self.context, 'strokeStyle', color)
        context.set(self.context, 'lineWidth', s*0.5)
        context.set(self.context, 'lineCap', "round")
        context.set(self.context, 'lineJoin', "round")

        for i in reversed(range(4)):
          p = ((t + i + 1) / 4.0) % 1
          x = cx + math.sin((p + i / 4) * WeatherAnimator.TAU) * a
          y = cy + p * cw
    
          self.draw_line(context, x - ux, y - uy, x + ux, y + uy)
          self.draw_line(context, x - vx, y - vy, x + vx, y + vy)
          self.draw_line(context, x - wx, y - wy, x + wx, y + wy)

    def draw_fog_bank(self, context, t, cx, cy, cw, s, color):
        t /= 30000

        a = cw * 0.21
        b = cw * 0.06
        c = cw * 0.21
        d = cw * 0.28

        context.set('fillStyle', color)
        self.draw_puffs(context, t, cx, cy, a, b, c, d)
    
        context.globalCompositeOperation = 'destination-out'
        self.draw_puffs(context, t, cx, cy, a, b, c - s, d - s)
        context.globalCompositeOperation = 'source-over'

    def draw_leaf(self, context, t, x, y, cw, s, color):
        a = cw / 8,
        b = a / 3,
        c = 2 * b,
        d = (t % 1) *WeatherAnimator.TAU,
        e = math.cos(d),
        f = math.sin(d)

        context.set(self.context, 'strokeStyle', color)
        context.set(self.context, 'lineWidth', s)
        context.set(self.context, 'lineCap', "round")
        context.set(self.context, 'lineJoin', "round")
        context.set(self.context, 'fillStyle', color)
    
        context.beginPath()
        context.arc(x        , y        , a, d          , d + math.PI, False)
        context.arc(x - b * e, y - b * f, c, d + math.PI, d          , False)
        context.arc(x + c * e, y + c * f, b, d + math.PI, d          , True )
        context.globalCompositeOperation = 'destination-out'
        context.fill()
        context.globalCompositeOperation = 'source-over'
        context.stroke()

    def draw_swoosh(self, context, t, cx, cy, cw, s, index, total, color):
        t /= 2500

        path = WIND_PATHS[index]
        a = (t + index - WIND_OFFSETS[index].start) % total
        c = (t + index - WIND_OFFSETS[index].end  ) % total
        e = (t + index                            ) % total
        
        context.set(self.context, 'strokeStyle', color)
        context.set(self.context, 'lineWidth', s)
        context.set(self.context, 'lineCap', "round")
        context.set(self.context, 'lineJoin', "round")

        if a < 1:
            context.beginPath()
            
            a *= len(path) / 2 - 1
            b  = math.floor(a)
            a -= b
            b *= 2
            b += 2
    
            context.moveTo(
             cx + (path[b - 2] * (1 - a) + path[b    ] * a) * cw,
             cy + (path[b - 1] * (1 - a) + path[b + 1] * a) * cw
            )
    
            if(c < 1):
                c *= len(path) / 2 - 1
                d  = math.floor(c)
                c -= d
                d *= 2
                d += 2
        
                i = b
                while i != d:
                    i += 2
                    context.lineTo(cx + path[i] * cw, cy + path[i + 1] * cw)
        
                context.lineTo(
                  cx + (path[d - 2] * (1 - c) + path[d    ] * c) * cw,
                  cy + (path[d - 1] * (1 - c) + path[d + 1] * c) * cw
                )
              
        
            else:
                i = b
                while( i != len(path)):
                    i+=2
                    context.lineTo(cx + path[i] * cw, cy + path[i + 1] * cw)
        
            context.stroke()


        elif c < 1:
            context.beginPath()
            
            c *= len(path) / 2 - 1
            d  = math.floor(c)
            c -= d
            d *= 2
            d += 2

            context.moveTo(cx + path[0] * cw, cy + path[1] * cw)
            i = 2
            while( i != d):
                i += 2
                context.lineTo(cx + path[i] * cw, cy + path[i + 1] * cw)
        
            context.lineTo(
                cx + (path[d - 2] * (1 - c) + path[d    ] * c) * cw,
                cy + (path[d - 1] * (1 - c) + path[d + 1] * c) * cw
              )
        
            context.stroke()

        if e < 1:
            e *= len(path) / 2 - 1
            f  = math.floor(e)
            e -= f
            f *= 2
            f += 2

            self.draw_leaf(
                context,
                t,
                cx + (path[f - 2] * (1 - e) + path[f    ] * e) * cw,
                cy + (path[f - 1] * (1 - e) + path[f + 1] * e) * cw,
                cw,
                s,
                color
            )
            
    def CLEAR_DAY(self, context, t, color):
        w = context.canvas.width
        h = context.canvas.height
        s = min(w, h)

        self.draw_sun(context, t, w * 0.5, h * 0.5, s, s * WeatherAnimator.STROKE, color)

    def CLEAR_NIGHT(self, context, t, color):
        w = context.canvas.width
        h = context.canvas.height
        s = min(w, h)

        self.draw_moon(context, t, w * 0.5, h * 0.5, s, s * WeatherAnimator.STROKE, color)


    def PARTLY_CLOUDY_DAY(self, context, t, color):
        w = context.canvas.width
        h = context.canvas.height
        s = min(w, h)

        self.draw_sun(context, t, w * 0.625, h * 0.375, s * 0.75, s * WeatherAnimator.STROKE, color)
        self.draw_cloud(context, t, w * 0.375, h * 0.625, s * 0.75, s * WeatherAnimator.STROKE, color)

    def PARTLY_CLOUDY_NIGHT(self, context, t, color):
        w = context.canvas.width
        h = context.canvas.height
        s = min(w, h)

        self.draw_moon(context, t, w * 0.667, h * 0.375, s * 0.75, s * WeatherAnimator.STROKE, color)
        self.draw_cloud(context, t, w * 0.375, h * 0.625, s * 0.75, s * WeatherAnimator.STROKE, color)

    def CLOUDY(self, ctx, t, color):
        w = ctx.canvas.width
        h = ctx.canvas.height,
        s = min(w, h)
    
        self.draw_cloud(ctx, t, w * 0.5, h * 0.5, s, s *WeatherAnimator.STROKE, color)
  

    def RAIN(self, ctx, t, color):
        w = ctx.canvas.width
        h = ctx.canvas.height
        s = min(w, h)

        self.draw_rain(ctx, t, w * 0.5, h * 0.37, s * 0.9, s *WeatherAnimator.STROKE, color)
        self.draw_cloud(ctx, t, w * 0.5, h * 0.37, s * 0.9, s *WeatherAnimator.STROKE, color)


    def SLEET(self, ctx, t, color):
        w = ctx.canvas.width
        h = ctx.canvas.height
        s = min(w, h)

        self.draw_sleet(ctx, t, w * 0.5, h * 0.37, s * 0.9, s *WeatherAnimator.STROKE, color)
        self.draw_cloud(ctx, t, w * 0.5, h * 0.37, s * 0.9, s *WeatherAnimator.STROKE, color)

    def SNOW(self, ctx, t, color):
        w = ctx.canvas.width
        h = ctx.canvas.height
        s = min(w, h)

        self.draw_snow(ctx, t, w * 0.5, h * 0.37, s * 0.9, s *WeatherAnimator.STROKE, color)
        self.draw_cloud(ctx, t, w * 0.5, h * 0.37, s * 0.9, s *WeatherAnimator.STROKE, color)

    def WIND(self, ctx, t, color):
        w = ctx.canvas.width
        h = ctx.canvas.height
        s = min(w, h)

        self.draw_swoosh(ctx, t, w * 0.5, h * 0.5, s, s *WeatherAnimator.STROKE, 0, 2, color)
        self.draw_swoosh(ctx, t, w * 0.5, h * 0.5, s, s *WeatherAnimator.STROKE, 1, 2, color)

    def FOG(self, ctx, t, color):
        w = ctx.canvas.width
        h = ctx.canvas.height
        s = min(w, h)
        k = s *WeatherAnimator.STROKE

        self.draw_fogbank(ctx, t, w * 0.5, h * 0.32, s * 0.75, k, color)

        t /= 5000

        a = math.cos((t       ) * WeatherAnimator.TAU) * s * 0.02
        b = math.cos((t + 0.25) * WeatherAnimator.TAU) * s * 0.02
        c = math.cos((t + 0.50) * WeatherAnimator.TAU) * s * 0.02
        d = math.cos((t + 0.75) * WeatherAnimator.TAU) * s * 0.02
        n = h * 0.936,
        e = math.floor(n - k * 0.5) + 0.5,
        f = math.floor(n - k * 2.5) + 0.5

        ctx.set(self.context, 'strokeStyle', color)
        ctx.set(self.context, 'lineWidth', k)
        ctx.set(self.context, 'lineCap', "round")
        ctx.set(self.context, 'lineJoin', "round")

        self.draw_line(ctx, a + w * 0.2 + k * 0.5, e, b + w * 0.8 - k * 0.5, e)
        self.draw_line(ctx, c + w * 0.2 + k * 0.5, f, d + w * 0.8 - k * 0.5, f)

    def _determineDrawingFunction(self, draw):
        if isinstance(draw, str):
            draw = getattr(WeatherAnimator,(draw.upper().replace("-", "_")))

        return draw

    def add(self, el, draw):

        if isinstance(el, str):
            el = self.context.get_jsobject("document").getElementById(el)

        # Does nothing if canvas name doesn't exists
        if el is None:
            return

        draw = self._determineDrawingFunction(draw)

        # Does nothing if the draw function isn't actually a function
        if not hasattr(draw, "__call__"):
            return

       # obj = WeatherAnimator.DrawingElement(el, draw)
       #
        obj={
            'element': el,
            'context': el.getContext("2d"),
            'drawing': draw,
            'canvas' : el.getContext("2d").canvas
          }

        self.drawing_elems.append(obj)
        self.draw(obj, WeatherAnimator.KEYFRAME)

    def set(self, el, draw):

        if isinstance(el, str):
            el = self.context.get_jsobject("document").getElementById(el)

        for i in reversed(range(len(self.drawing_elems))):
            if self.drawing_elems[i].element == el:
                self.drawing_elems[i].drawing = self._determineDrawingFunction(draw)
                self.draw(self.drawing_elems[i], WeatherAnimator.KEYFRAME)
                return

        self.add(el, draw)


    def  remove(self, el):

        if isinstance(el, str):
            el = self.context.get_jsobject("document").getElementById(el)

        for i in reversed(range(len(self.drawing_elems))):
            if self.drawing_elems[i].element == el:
                self.drawing_elems[i: i + 1]
                return

    def draw(self, obj, time):
        canvas = obj.get("canvas", obj["context"].canvas)
        if obj.get("canvas") is None:
            obj["canvas"] = canvas

        if self.resizeClear:
            canvas.set(self.context, 'width', canvas.width)
        else:
            obj["context"].clearRect(0, 0, canvas.width, canvas.height)

        obj["drawing"](self, obj["context"], time, self.color)

    def __drawfunct(self, *args):
        now = (datetime.utcnow() - datetime(1970,1,1)).total_seconds()
        if now - self.prev_now > 0.1:
            self.prev_now = now
            now *=10000.0
            for item in self.drawing_elems:
                self.draw(item, now)

    def play(self):
      self.pause()
      self.interval = self.request_interval(self.__drawfunct, 1000 / 60)

    def pause(self):

      if self.interval:
        self.cancel_interval(self.interval)
        self.interval = None



class WeatherUpdater(JavascriptClass):

    animations = ['sleet',  # 0
                     'sleet',  # 1
                     'sleet',  # 2
                     'sleet',  # 3
                     'sleet',  # 4
                     'snow',  # 5
                     'snow',  # 6
                     'snow',  # 7
                     'snow',  # 8
                     'rain',  # 9
                     'snow',  # 10
                     'rain',  # 11
                     'rain',  # 12
                     'snow',  # 13
                     'snow',  # 14
                     'snow',  # 15
                     'snow',  # 16
                     'sleet',  # 17
                     'sleet',  # 18
                     'fog',  # 19
                     'fog',  # 20
                     'fog',  # 21
                     'fog',  # 22
                     'wind',  # 23
                     'wind',  # 24
                     'cloudy',  # 25
                     'cloudy',  # 26
                     'partly-cloudy-night',  # 27
                     'partly-cloudy-day',  # 28
                     'partly-cloudy-night',  # 29
                     'partly-cloudy-day',  # 30
                     'clear-night',  # 31
                     'clear-day',  # 32,
                     'clear-night',  # 33
                     'clear-day',  # 34
                     'sleet',  # 35
                     'clear-day',  # 36
                     'sleet',  # 37
                     'sleet',  # 38
                     'sleet',  # 39
                     'rain',  # 40
                     'snow',  # 41
                     'snow',  # 42
                     'snow',  # 43
                     'partly-cloudy-day',  # 44
                     'sleet',  # 45
                     'snow',  # 46
                     'sleet',  # 47
                     'clear-day',  # 48 (default)
                     ]
    def __init__(self, webview):
        self.context = webview.get_main_frame().get_global_context()
        self.webview = webview

    def start(self):
        self.webview.on_view_ready(self._start)

    def _start(self):
        global _
        javascript.document = self.context.get_jsobject("document")
        _ = self.context.get_jsobject("$", can_call=True)
        print "JQ...... %s" % _
        self.ready()
        _(javascript.document).ready(self.ready)

    def ready(self):
        self.update()
        setInterval = self.context.get_jsobject("window").setInterval
        setInterval(self.update, 5 * 60 * 1000)

    def update_view(self, weather):
        global _

        #Skycons = self.context.get_jsobject("Skycons", can_call=True)
        skycons = WeatherAnimator(self.context, {"color": "white"})
        html = """<canvas id="weather-icon" width="128" height="128"></canvas><h2> %(weather_temp)s&deg %(weather_units_temp)s</h2>
                  <div id="region">%(weather_city)s, %(weather_region)s</div>
                  <div>%(weather_currently)s</div>
                  <div>%(weather_wind_direction)s %(weather_wind_speed)s %(weather_units_speed)s</div>
                  <div><i class="fa fa-angle-up"></i>  High %(weather_high)s <i class="fa fa-angle-down"></i>  Low %(weather_low)s </div>
                  """ % {'weather_city': weather.city,
                         'weather_region': weather.region,
                         'weather_currently': weather.currently,
                         'weather_wind_direction': weather.wind.direction,
                         'weather_wind_speed': weather.wind.speed,
                         'weather_temp': weather.temp,
                         'weather_units_speed': weather.units.speed,
                         'weather_units_temp': weather.units.temp,
                         'weather_high': weather.high,
                         'weather_low': weather.low}

        _("#weather").html(html)
        _("#weather").html(html)

        if int(weather.code) > 48:
            weather.code = 48
        animation = WeatherUpdater.animations[max(min(int(weather.code), 48),0)]
        skycons.remove('weather-icon')
        #  you can add a canvas by it's ID...
        # console.log(animation)
        skycons.add("weather-icon", animation)
        skycons.play()
        return True

    def update_error(self, error):
        show = self.context.get_jsobject("show")
        show(error)
        _("#weather").html('<p>' + error + '</p>')

    def update(self):
        print "WEATHER UPDATE"
        _.simpleWeather({
            'location': 'San Jose, CA',
            # 'woeid': '',
            'zipcode': '95139',
            'unit': 'f',
            'success': self.update_view,
            'error': self.update_error})

