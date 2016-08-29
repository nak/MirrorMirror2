#!/usr/bin/env python

from pyggi.gtk3 import GtkWindow, GtkScrolledWindow
from pyggi import gtk3
from pyggi.webkit3 import WebKitWebView
from mirror_mirror import server
from mirror_mirror.weather import WeatherUpdater
from mirror_mirror.clock import Clock
from mirror_mirror.calendardisplay import Calendar
from mirror_mirror.news import NewsUpdater
from mirror_mirror.events import EventsUpdater
from mirror_mirror.motd import MOTDUpdater

srvr = server.HTTPServer.start()

window = GtkWindow( gtk3.GTK_WINDOW_TOPLEVEL )
window.set_default_size( 1200, 800 )
window.set_title("Mirror Mirror On The Wall")
scrolled = GtkScrolledWindow( None, None )
window.add( scrolled )
webview = WebKitWebView()
scrolled.add( webview )

html="""
<html class="no-js" lang="">
    <head>
        <meta charset="utf-8">
        <meta http-equiv="x-ua-compatible" content="ie=edge">
        <title>Mirror Mirror on the Wall</title>
        <meta name="description" content="Mirror mirror on the wall...">
        <meta name="viewport" content="width=device-width, initial-scale=1">

        <link rel="stylesheet" href="css/normalize.css">
        <link rel="stylesheet" href="css/main.css">
        <!-- Fonts -->
        <link href='https://fonts.googleapis.com/css?family=Neucha' rel='stylesheet' type='text/css'>
        <script src="/js/vendor/jquery-1.11.3.min.js"></script>

<script src="https://ajax.googleapis.com/ajax/libs/jqueryui/1.11.4/jquery-ui.min.js"></script>
    <script src="/js/vendor/jquery.simpleWeather.min.js"></script>
        <script src="/js/vendor/js/jquery-ui-datepicker.min.js"></script>
        <script src="js/plugins.js"></script>
          <script src="js/main.js"></script>
   </head>
    <body >
    <div style='width:100%'>
        <div style='width:50%;float:left;z-index:5;displayh:inline-block'>
        <div id="weather">
            <canvas id="weather-icon" width="128" height="128"></canvas><h2 id='weather_temp'> %(weather_temp)s&deg %(weather_units_temp)s</h2>
            <div id='weather_text'></div>
        </div>
        <br/>
        <h2><i>News</i></h2>
        <div id="news" style='width:60%'>
        </div>
        </div>
        <div  style='width:25%;float:right;z-index:10; display:inline-block'>
          <div id='date'></div>
          <div id='calendar'></div>
          <h2><i>Upcoming Events</i></h2>
          <div id='events'></div>
        </div>
        </div>
        <p id="greeting">
            You look amazing today.
        </p>
        <script>


        </script>
    </body>
</html>
"""
webview.load_string(html, "text/html", "UTF-8", "http://localhost:%d" % server.HTTPServer.PORT)
window.show_all()
window.connect("delete-event", gtk3.main_quit )
WeatherUpdater(webview).start()
Clock(webview).start()
Calendar(webview).start()
NewsUpdater(webview).start()
EventsUpdater(webview).start()
MOTDUpdater(webview).start()

def main():
    gtk3.main()

if __name__ == "__main__":
    try:
        main()
    finally:
        srvr.stop()