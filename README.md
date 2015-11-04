# TeamCityNotifier
A python script which sends a push notification to your smartphone when your TC build is Green/Red or TC Server is down. 

###How To Use?
  1. Pull the repository into your computer
  2. Register at https://pushover.net/
  3. Install Pushover Android or iOS app onto your smartphone from https://pushover.net/clients/ios or https://pushover.net/clients/android
  4. Supply the app with your Pushover user key
  5. Register a new Application at https://pushover.net/
  6. Edit settings.cfg
    * Supply it with your TeamCity credentials;
    * Supply it woth your Pushover Application token and devices ids
  7. Run or schedule tc_notifier.py script with your OS CRON or Scheduled Tasks service

######Dependencies 

_pip install pushover requests_
