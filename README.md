# WheresWaldo
App to track family whereabouts using AWS 1-Click IoT service &amp; buttons  

##Background
At the end of 2017, AWS announced the availability of a new service called AWS IoT 1-Click.  The service allows users to deploy push-button devices throughout their environment that can initiate actions in the cloud when the buttons are activated.  The service currently supports two types of buttons: one that relies on WiFi (sold by Amazon), and another that uses LTE-M (sold by AT&T).  The LTE-M button is particularly powerful since it can connect to the network wherever it is - there's no need to tether it to a local WiFi source.  Moreover, the LTE-M button will report the cell tower that it's currently connected to (more on that later...)  AT&T's LTE-M button is currently marketed to enterprise business customers, but there are compelling use-cases for the consumer market as well.  One of these is an app to track family whereabouts.  The use case is very simple... Each family member is issued an AT&T LTE-M button for personal use, and an Amazon button for use in the home:  

* When someone departs from a location, they press their button once (a "SINGLE" click to AWS)
* After they arrive at their destination, they press their button twice (a "DOUBLE" click).
* If for some reason they need to alert folks ASAP, they give the button a long press (a "LONG" click)  

Each button press is delivered to the AWS IoT 1-Click service, which invokes the button_handler lambda function to process the event.  The handler forwards the button press to a backend server that hosts the button.cgi script.  The script records the button press, and then sends notifcations to a specified set of recipients associated with each button press.  In the case of AT&T's LTE-M button, the device reports the "cellid" to which it's currently connected, together with the observed signal strength.  That information can be used to roughly geolocate the device.  In particular, UnwiredLabs offers a free API (https://unwiredlabs.com/api) that will map a cellid - together with a MCC, MNC, and LAC - to the address of the connected cell tower.
