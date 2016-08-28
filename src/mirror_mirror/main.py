#!/usr/bin/env python
import gobject

from pyggi.gtk3 import GtkWindow, GtkScrolledWindow
from pyggi import gtk3
from pyggi.webkit3 import WebKitWebView
from mirror_mirror import server
from mirror_mirror.weather import WeatherUpdater
from mirror_mirror.clock import Clock
from mirror_mirror.calendar import Calendar
from mirror_mirror.events import Events

srvr = server.HTTPServer.start()

window = GtkWindow( gtk3.GTK_WINDOW_TOPLEVEL )
window.set_default_size( 1200, 800 )
window.set_title("Mirror Mirror On The Wall")
scrolled = GtkScrolledWindow( None, None )
window.add( scrolled )
webview = WebKitWebView()
scrolled.add( webview )

#webview.open( "http://www.python.org" )
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
        <script src="/js/skycons.js"></script>
        <script src="js/plugins.js"></script>
        <script type="text/javascript">

      /**
       * Check if current user has authorized this application.
       */
       function handleResult(res){
        alert(JSON.stringify(res));
       }

        function myauth(d, func){
            alert("" + JSON.stringify(d) + "    " + d["immediate"] + "     " +func);

            gapi.auth.authorize({'client_id': d["client_id"],
                                 'scope': d["scope"],
                                 'immediate': d["immediate"]},
                                 d["immediate"]?func:handleResult);
        }

      function checkAuth() {
         mirror_mirror.events.Events.new_();
        /* client_id = "845856401252-hv7tno9akjgipl2kl2669fqpe4pg7qqa.apps.googleusercontent.com";
         scopes = ["https://www.googleapis.com/auth/calendar.readonly"];
        gapi.auth.authorize({'client_id': client_id,
                             'scope': scopes[0],
                             'immediate': true},
                             handleResult);*/
        }
      </script>
         <script src="https://apis.google.com/js/client.js?onload=checkAuthNOT"></script>
          <script src="js/main.js"></script>
   </head>
    <body >
    <div style='width:100%'>
        <div id="weather" style='width:50%;display:inline-block'>

        </div>
        <div  style='width:25%;float:right;z-index:10; display:inline-block'>
          <div id='date'></div>
          <div id='calendar'></div>
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
#Events.set_view(webview)

def main():
    gtk3.main()

if __name__ == "__main__":
    try:
        main()
    finally:
        srvr.stop()