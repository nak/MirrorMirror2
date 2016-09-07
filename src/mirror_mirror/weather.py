#  Docs for jquery at http://simpleweatherjs.com
#  This is based on original work done for Magic Mirror I

import math

from datetime import datetime
from pyggi import javascript

from mirror_mirror import BaseUpdater

_ = None

WIND_PATHS = [
    [
        -0.7500, -0.1800, -0.7219, -0.1527, -0.6971, -0.1225,
        -0.6739, -0.0910, -0.6516, -0.0588, -0.6298, -0.0262,
        -0.6083, 0.0065, -0.5868, 0.0396, -0.5643, 0.0731,
        -0.5372, 0.1041, -0.5033, 0.1259, -0.4662, 0.1406,
        -0.4275, 0.1493, -0.3881, 0.1530, -0.3487, 0.1526,
        -0.3095, 0.1488, -0.2708, 0.1421, -0.2319, 0.1342,
        -0.1943, 0.1217, -0.1600, 0.1025, -0.1290, 0.0785,
        -0.1012, 0.0509, -0.0764, 0.0206, -0.0547, -0.0120,
        -0.0378, -0.0472, -0.0324, -0.0857, -0.0389, -0.1241,
        -0.0546, -0.1599, -0.0814, -0.1876, -0.1193, -0.1964,
        -0.1582, -0.1935, -0.1931, -0.1769, -0.2157, -0.1453,
        -0.2290, -0.1085, -0.2327, -0.0697, -0.2240, -0.0317,
        -0.2064, 0.0033, -0.1853, 0.0362, -0.1613, 0.0672,
        -0.1350, 0.0961, -0.1051, 0.1213, -0.0706, 0.1397,
        -0.0332, 0.1512, 0.0053, 0.1580, 0.0442, 0.1624,
        0.0833, 0.1636, 0.1224, 0.1615, 0.1613, 0.1565,
        0.1999, 0.1500, 0.2378, 0.1402, 0.2749, 0.1279,
        0.3118, 0.1147, 0.3487, 0.1015, 0.3858, 0.0892,
        0.4236, 0.0787, 0.4621, 0.0715, 0.5012, 0.0702,
        0.5398, 0.0766, 0.5768, 0.0890, 0.6123, 0.1055,
        0.6466, 0.1244, 0.6805, 0.1440, 0.7147, 0.1630,
        0.7500, 0.1800
    ],
    [
        -0.7500, 0.0000, -0.7033, 0.0195, -0.6569, 0.0399,
        -0.6104, 0.0600, -0.5634, 0.0789, -0.5155, 0.0954,
        -0.4667, 0.1089, -0.4174, 0.1206, -0.3676, 0.1299,
        -0.3174, 0.1365, -0.2669, 0.1398, -0.2162, 0.1391,
        -0.1658, 0.1347, -0.1157, 0.1271, -0.0661, 0.1169,
        -0.0170, 0.1046, 0.0316, 0.0903, 0.0791, 0.0728,
        0.1259, 0.0534, 0.1723, 0.0331, 0.2188, 0.0129,
        0.2656, -0.0064, 0.3122, -0.0263, 0.3586, -0.0466,
        0.4052, -0.0665, 0.4525, -0.0847, 0.5007, -0.1002,
        0.5497, -0.1130, 0.5991, -0.1240, 0.6491, -0.1325,
        0.6994, -0.1380, 0.7500, -0.1400
    ]
]

WIND_OFFSETS = [
    {'start': 0.36, 'end': 0.11},
    {'start': 0.56, 'end': 0.16}
]


class WeatherAnimator(object):
    KEYFRAME = 5000
    STROKE = 0.08
    TAU = 2.0 * math.pi
    TWO_OVER_SQRT_2 = 2.0 / math.sqrt(2.0)

    class DrawingElement(object):

        def __init__(self, jsctxt, element, color, drawfunct, resize_clear):
            self.jsctxt = jsctxt
            self.element = element
            self.context = element.getContext("2d")
            self.canvas = self.context.canvas
            self.width = self.canvas.width
            self.height = self.canvas.height
            self.drawfunct = drawfunct
            self.color = color
            self.resize_clear = resize_clear
            self.context_set = self.context.set
            self.context_set(self.jsctxt, 'strokeStyle', color)
            self.context_set(self.jsctxt, 'fillStyle', color)
            self.context_set(self.jsctxt, 'lineCap', "round")
            self.context_set(self.jsctxt, 'lineJoin', "round")
            # cache lookups to javascript, since we don't expect these
            #function attributes to change:
            self.context_arc = self.context.arc
            self.context_fill = self.context.fill
            self.context_beginPath = self.context.beginPath
            self.context_closePath = self.context.closePath
            self.context_moveTo = self.context.moveTo
            self.context_lineTo = self.context.lineTo
            self.context_stroke = self.context.stroke

        def draw_circle(self, x, y, r):
            self.context_beginPath()
            self.context_arc(x, y, r, 0, WeatherAnimator.TAU, False)
            self.context_fill()

        def draw_line(self, ax, ay, bx, by):
            self.context_beginPath()
            self.context_moveTo(ax, ay)
            self.context_lineTo(bx, by)
            self.context_stroke()

        def draw_puff(self, t, cx, cy, rx, ry, rmin, rmax):
            c = math.cos(t * WeatherAnimator.TAU)
            s = math.sin(t * WeatherAnimator.TAU)
            rmax -= rmin
            self.draw_circle(cx - s * rx,
                             cy + c * ry + rmax * 0.5,
                             rmin + (1 - c * 0.5) * rmax)

        def draw_puffs(self, t, cx, cy, rx, ry, rmin, rmax):
            for i in reversed(range(4)):
                self.draw_puff(t + i/ 5.0, cx, cy, rx, ry, rmin, rmax)

        def draw_cloud(self, t, cx, cy, cw, s):
            t /= 30000

            a = cw * 0.21
            b = cw * 0.12
            c = cw * 0.24
            d = cw * 0.28

            self.draw_puffs(t, cx, cy, a, b, c, d)

            self.context_set(self.jsctxt, 'globalCompositeOperation', 'destination-out')
            self.draw_puffs(t, cx, cy, a, b, c - s, d - s)
            self.context_set(self.jsctxt, 'globalCompositeOperation', 'source-over')

        def draw_sun(self, t, cx, cy, cw, s):
            t /= 12000

            a = cw * 0.25 - s * 0.5
            b = cw * 0.32 + s * 0.5
            c = cw * 0.50 - s * 0.5

            self.context_set(self.jsctxt, 'lineWidth', s)
            self.context_beginPath()
            self.context_arc(cx, cy, a, 0, WeatherAnimator.TAU, False)
            self.context_stroke()

            for i in reversed(range(8)):
                p = ((t + i + 1) / 8.0) * WeatherAnimator.TAU
                cos = math.cos(p)
                sin = math.sin(p)
                self.draw_line(cx + cos * b, cy + sin * b, cx + cos * c, cy + sin * c)

        def draw_moon(self, t, cx, cy, cw, s):
            t /= 15000

            a = cw * 0.29 - s * 0.5
            b = cw * 0.05
            c = math.cos(t * WeatherAnimator.TAU)
            p = c * WeatherAnimator.TAU / (-16.0)

            self.context_set(self.jsctxt, 'lineWidth', s)

            cx += c * b

            self.context_beginPath()
            self.context_arc(cx, cy, a, p + WeatherAnimator.TAU / 8.0, p + WeatherAnimator.TAU * 7 / 8.0, False)
            self.context_arc(cx + math.cos(p) * a * WeatherAnimator.TWO_OVER_SQRT_2, cy + math.sin(p) * a *
                             WeatherAnimator.TWO_OVER_SQRT_2, a, p + WeatherAnimator.TAU * 5 / 8.0, p +
                             WeatherAnimator.TAU * 3 / 8.0, True)
            self.context_closePath()
            self.context_stroke()

        def draw_rain(self, t, cx, cy, cw, s):
            t /= 1350
            a = cw * 0.16
            b = float(WeatherAnimator.TAU * 11) / 12.0
            c = WeatherAnimator.TAU * 7 / 12.0

            self.context_set(self.jsctxt, 'fillStyle', self.color)

            for i in reversed(range(4)):
                p = ((t + i + 1) / 4.0) % 1
                x = cx + ((i - 1.5) / 1.5) * (i == 1 or (-1 if i == 2 else 1)) * a
                y = cy + p * p * cw
                self.context_beginPath()
                self.context_moveTo(x, y - s * 1.5)
                self.context_arc(x, y, s * 0.75, b, c, False)
                self.context_fill()

        def draw_sleet(self, t, cx, cy, cw, s):
            t /= 750

            a = cw * 0.1875

            self.context_set(self.jsctxt, 'lineWidth', s * 0.5)

            for i in reversed(range(4)):
                p = ((t + i) / 4.0) % 1
                x = math.floor(cx + ((i - 1.5) / 1.5) * (i == 1 or (-1 if i == 2 else 1)) * a) + 0.5
                y = cy + p * cw
                self.draw_line(x, y - s * 1.5, x, y + s * 1.5)

        def draw_snow(self, t, cx, cy, cw, s):
            t /= 3000

            a = cw * 0.16
            b = s * 0.75
            u = t * WeatherAnimator.TAU * 0.7
            ux = math.cos(u) * b
            uy = math.sin(u) * b
            v = u + WeatherAnimator.TAU / 3.0
            vx = math.cos(v) * b
            vy = math.sin(v) * b
            w = u + WeatherAnimator.TAU * 2.0 / 3.0
            wx = math.cos(w) * b
            wy = math.sin(w) * b

            self.context_set(self.jsctxt, 'lineWidth', s * 0.5)

            for i in reversed(range(4)):
                p = ((t + i + 1) / 4.0) % 1
                x = cx + math.sin((p + i +1/ 4) * WeatherAnimator.TAU) * a
                y = cy + p * cw

                self.draw_line(x - ux, y - uy, x + ux, y + uy)
                self.draw_line(x - vx, y - vy, x + vx, y + vy)
                self.draw_line(x - wx, y - wy, x + wx, y + wy)

        def draw_fog_bank(self, t, cx, cy, cw, s):
            t /= 30000

            a = cw * 0.21
            b = cw * 0.06
            c = cw * 0.21
            d = cw * 0.28

            self.context_set(self.jsctxt, 'fillStyle', self.color)
            self.draw_puffs(t, cx, cy, a, b, c, d)

            self.context.globalCompositeOperation = 'destination-out'
            self.draw_puffs(t, cx, cy, a, b, c - s, d - s)
            self.context.globalCompositeOperation = 'source-over'

        def draw_leaf(self, t, x, y, cw, s):
            a = cw / 8
            b = a / 3
            c = 2 * b
            d = (t % 1) * WeatherAnimator.TAU
            e = math.cos(d)
            f = math.sin(d)

            self.context_set(self.jsctxt, 'lineWidth', s)
            self.context_set(self.jsctxt, 'fillStyle', self.color)

            self.context_beginPath()
            self.context_arc(x, y, a, d, d + math.pi, False)
            self.context_arc(x - b * e, y - b * f, c, d + math.pi, d, False)
            self.context_arc(x + c * e, y + c * f, b, d + math.pi, d, True)
            self.context_set(self.jsctxt, 'globalCompositeOperation', 'destination-out')
            self.context_fill()
            self.context_set(self.jsctxt, 'globalCompositeOperation', 'source-over')
            self.context_stroke()

        def draw_swoosh(self, t, cx, cy, cw, s, index, total):
            t /= 2500

            path = WIND_PATHS[index]
            a = (t + index - WIND_OFFSETS[index]['start']) % total
            c = (t + index - WIND_OFFSETS[index]['end']) % total
            e = (t + index) % total

            self.context_set(self.jsctxt, 'lineWidth', s)

            if a < 1:
                self.context_beginPath()

                a *= len(path) / 2 - 1
                b = int(math.floor(a))
                a -= b
                b *= 2
                b += 2

                self.context_moveTo(
                        cx + (path[b - 2] * (1 - a) + path[b] * a) * cw,
                        cy + (path[b - 1] * (1 - a) + path[b + 1] * a) * cw
                )

                if c < 1:
                    c *= len(path) / 2 - 1
                    d = int(math.floor(c))
                    c -= d
                    d *= 2
                    d += 2

                    i = b
                    while i != d:
                        i += 2
                        self.context_lineTo(cx + path[i] * cw, cy + path[i + 1] * cw)

                    self.context_lineTo(
                            cx + (path[d - 2] * (1 - c) + path[d] * c) * cw,
                            cy + (path[d - 1] * (1 - c) + path[d + 1] * c) * cw
                    )

                else:
                    i = b
                    while i < len(path):
                        i += 2
                        self.context_lineTo(cx + path[i] * cw, cy + path[i + 1] * cw)

                self.context_stroke()

            elif c < 1:
                self.context_beginPath()

                c *= len(path) / 2 - 1
                d = math.floor(c)
                c -= d
                d *= 2
                d += 2

                self.context_moveTo(cx + path[0] * cw, cy + path[1] * cw)
                i = 2
                while i < d:
                    i += 2
                    self.context_lineTo(cx + path[i] * cw, cy + path[i + 1] * cw)

                self.context_lineTo(
                        cx + (path[d - 2] * (1 - c) + path[d] * c) * cw,
                        cy + (path[d - 1] * (1 - c) + path[d + 1] * c) * cw
                )

                self.context_stroke()

            if e < 1:
                e *= len(path) / 2 - 1
                f = math.floor(e)
                e -= f
                f *= 2
                f += 2

                self.draw_leaf(
                        t,
                        cx + (path[f - 2] * (1 - e) + path[f] * e) * cw,
                        cy + (path[f - 1] * (1 - e) + path[f + 1] * e) * cw,
                        cw,
                        s
                )

        def CLEAR_DAY(self, t):
            # OK
            w = self.width
            h = self.height
            s = min(w, h)
            self.draw_sun(t, w * 0.5, h * 0.5, s, s * WeatherAnimator.STROKE)

        def CLEAR_NIGHT(self, t):
            # OK
            s = min(self.width, self.height)
            self.draw_moon(t, self.width * 0.5, self.height * 0.5, s, s * WeatherAnimator.STROKE)

        def PARTLY_CLOUDY_DAY(self, t):
            # OK
            s = min(self.width, self.height)
            self.draw_sun(t, self.width * 0.625, self.height * 0.375, s * 0.75, s * WeatherAnimator.STROKE)
            self.draw_cloud(t, self.width * 0.375, self.height * 0.625, s * 0.75, s * WeatherAnimator.STROKE)

        def PARTLY_CLOUDY_NIGHT(self, t):
            # OK
            s = min(self.width, self.height)
            self.draw_moon(t, self.width * 0.667, self.height * 0.375, s * 0.75, s * WeatherAnimator.STROKE)
            self.draw_cloud(t, self.width * 0.375, self.height * 0.625, s * 0.75, s * WeatherAnimator.STROKE)

        def CLOUDY(self, t):
            # OK
            s = min(self.width, self.height)
            self.draw_cloud(t, self.width * 0.5, self.height * 0.5, s, s * WeatherAnimator.STROKE)

        def RAIN(self, t):
            # OK
            s = min(self.width, self.height)
            self.draw_rain(t, self.width * 0.5, self.height * 0.37, s * 0.9, s * WeatherAnimator.STROKE)
            self.draw_cloud(t, self.width * 0.5, self.height * 0.37, s * 0.9, s * WeatherAnimator.STROKE)

        def SLEET(self, t):
            # OK
            s = min(self.width, self.height)
            self.draw_sleet(t, self.width * 0.5, self.height * 0.37, s * 0.9, s * WeatherAnimator.STROKE)
            self.draw_cloud(t, self.width * 0.5, self.height * 0.37, s * 0.9, s * WeatherAnimator.STROKE)

        def SNOW(self, t):
            # OK
            s = min(self.width, self.height)
            self.draw_snow(t, self.width * 0.5, self.height * 0.37, s * 0.9, s * WeatherAnimator.STROKE)
            self.draw_cloud(t, self.width * 0.5, self.height * 0.37, s * 0.9, s * WeatherAnimator.STROKE)

        def WIND(self, t):
            # OK
            s = min(self.width, self.height)
            self.draw_swoosh(t, self.width * 0.5, self.height * 0.5, s, s * WeatherAnimator.STROKE, 0, 2)
            self.draw_swoosh(t, self.width * 0.5, self.height * 0.5, s, s * WeatherAnimator.STROKE, 1, 2)

        def FOG(self, t):
            # OK
            s = min(self.width, self.height)
            k = s * WeatherAnimator.STROKE

            self.draw_fog_bank(t, self.width * 0.5, self.height * 0.32, s * 0.75, k)

            t /= 5000

            a = math.cos(t * WeatherAnimator.TAU) * s * 0.02
            b = math.cos((t + 0.25) * WeatherAnimator.TAU) * s * 0.02
            c = math.cos((t + 0.50) * WeatherAnimator.TAU) * s * 0.02
            d = math.cos((t + 0.75) * WeatherAnimator.TAU) * s * 0.02
            n = self.height * 0.936
            e = math.floor(n - k * 0.5) + 0.5
            f = math.floor(n - k * 2.5) + 0.5

            self.context_set(self.jsctxt, 'lineWidth', k)

            self.draw_line(a + self.width * 0.2 + k * 0.5, e, b + self.width * 0.8 - k * 0.5, e)
            self.draw_line(c + self.width * 0.2 + k * 0.5, f, d + self.width * 0.8 - k * 0.5, f)

        def draw(self, time):

            if self.resize_clear:
                self.canvas.set(self.jsctxt, 'width', self.width)  # force redraw
            else:
                self.context.clearRect(0, 0, self.width, self.height)
            self.drawfunct(self, time)

        @staticmethod
        def determineDrawFunct(draw):
            if isinstance(draw, str):
                draw = getattr(WeatherAnimator.DrawingElement, (draw.upper().replace("-", "_")))

            return draw

    def __init__(self, context, opts=None):
        self.context = context
        try:
            self.requestAnimationFrame = \
                context.get_jsobject("webkitRequestAnimationFrame")
            self.cancelAnimationFrame = \
                context.get_jsobject("webkitCancelAnimationFrame")
        except:
            self.requestAnimationFrame = None
            self.cancelAnimationFrame = None
        # webkit animation frame available on raspberry pi, but doesn't work!,
        # so always fall back to setInterval for now
        if True or not self.requestAnimationFrame or not self.cancelAnimationFrame:
            self.request_interval = context.get_jsobject("window").setInterval
            self.cancel_interval = context.get_jsobject("window").clearInterval
        self.loop = None
        self.drawing_elems = {}
        self.interval = None
        self.color = (opts or {}).get('color') or "black"
        self.resizeClear = (opts or {}).get('resizeClear') or False
        self._ = context.get_jsobject('$')
        self.prev_now = (datetime.utcnow() - datetime(1970, 1, 1)).total_seconds()
        self.handler = None
        self.nativeFuncWrapper = self.context.get_jsobject("nativeFunctionWrapper")

    def request_interval(self, func, _):
        def handler(x):
            self.interval = x

        self.handler = handler
        self.interval = self.nativeFuncWrapper(func, self.handler)
        return self.interval

    def cancel_interval(self, handle):
        self.cancelAnimationFrame(handle)

    def add(self, elname, draw):
        assert (isinstance(elname, str))
        el = self.context.get_jsobject("document").getElementById(elname)
        # Does nothing if canvas name doesn't exists
        if el is None:
            return

        self.drawing_elems[elname] = WeatherAnimator.DrawingElement(self.context, el, self.color,
                                                                    WeatherAnimator.DrawingElement.determineDrawFunct(
                                                                            draw),
                                                                    self.resizeClear)
        try:
            self.drawing_elems[elname].draw(WeatherAnimator.KEYFRAME)
        except:
            pass
        return self.drawing_elems[elname]

    def set(self, el, draw):
        assert (isinstance(el, str))
        self.drawing_elems.get(el, self.add(el, draw)).drawfunct = \
            WeatherAnimator.DrawingElement.determineDrawFunct(draw)

    def remove(self, el):
        assert (isinstance(el, str))
        if self.drawing_elems.get(el):
            del self.drawing_elems[el]

    def __drawfunct(self, *_):
        now = (datetime.utcnow() - datetime(1970, 1, 1)).total_seconds()

        self.prev_now = now
        now *= 1000.0  # to milliseconds
        for item in self.drawing_elems.values():
            try:
                item.draw(now)
            except:
                import traceback
                traceback.print_exc()
                print "Failed to draw %s" % item.draw

    def play(self):
        self.pause()
        if self.interval is None:
            self.interval = self.request_interval(self.__drawfunct, 1000 / 10)

    def pause(self):
        if self.interval is not None:
            self.cancel_interval(self.interval)
            self.interval = None


class WeatherUpdater(BaseUpdater):
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
        super(WeatherUpdater, self).__init__(webview,  5 * 60 * 1000)
        self.skycons = None
        self.animation = None
        self.weather_ui = None
        self.weather_temp = None
        self.html = ""

    def update_view(self, weather):
        self.html = """
<div id="region">%(weather_city)s, %(weather_region)s</div>
<div>%(weather_currently)s</div>
<div>%(weather_wind_direction)s %(weather_wind_speed)s %(weather_units_speed)s</div>
<div><i class="fa fa-angle-up"></i>  High %(weather_high)s <i class="fa fa-angle-down"></i>  Low %(weather_low)s </div>
                """ % {'weather_city': weather.city,
                       'weather_region': weather.region,
                       'weather_currently': weather.currently,
                       'weather_wind_direction': weather.wind.direction,
                       'weather_wind_speed': weather.wind.speed,
                       'weather_units_speed': weather.units.speed,
                       'weather_high': weather.high,
                       'weather_low': weather.low}
        self.weather_temp.html('%(weather_temp)s&deg %(weather_units_temp)s' % {
                       'weather_temp': weather.temp, 'weather_units_temp': weather.units.temp,
                        })
        self.weather_ui.html(self.html)

        if int(weather.code) > 48:
            weather.code = 48
        animation = WeatherUpdater.animations[max(min(int(weather.code), 48), 0)]
        if self.skycons is None:
            self.skycons = WeatherAnimator(self.context, {"color": "white"})
        if animation != self.animation:
            self.skycons.remove('weather-icon')
            #  you can add a canvas by it's ID...
            # console.log(animation)
            self.skycons.add("weather-icon", animation)
            self.skycons.play()
            self.animation = animation

    def update_error(self, error):
        self.weather_ui.html('<p>' + error + '</p>')

    def update(self):
        """
        update the weather forecast
        """
        if self.weather_ui is None:
            self.weather_ui = self._("#weather_text")
            self.weather_temp = self._('#weather_temp')
        self._.simpleWeather({
            'location': 'San Jose, CA',
            'zipcode': '95139',
            'unit': 'f',
            'success': self.update_view,
            'error': self.update_error})
