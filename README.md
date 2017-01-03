[![Version button](https://img.shields.io/github/release/adamb70/CSGO-Market-Float-Finder.svg)](https://github.com/adamb70/CSGO-Market-Float-Finder/releases)
[![Download button](https://img.shields.io/badge/download-here-green.svg)](http://bit.ly/CSGOmarketfloat)

# CSGO-Market-Float-Finder
Find Counter Strike: Global Offensive Steam Market skin float values, seeds, and skin type. Tabulates data for easy sorting.

![alt tag](http://i.imgur.com/q2Dqh51.png?1)

## Download

**Please read the instructions before using this program!**

- [Windows 64 bit](http://bit.ly/CSGOmarketfloat)
- [Windows 32 bit](http://bit.ly/CSGOmarketfloat32)

## Instructions
#### Signing In
**You must sign in with a Steam account that owns CS:GO!**
	
1. Launch the program and log in with your Steam account. You may check 'Remember Me' to autofill details when you launch the program, but be aware that this will store your Steam username and password **in plaintext** in the settings.txt file.

2. If it is your first time launching the program Steam will send you an authentication email, which the program will ask for. Enter this code and press 'OK'. The program will now save a 'sentry_username.bin' file which will authenticate you every time you log in from now on.

*ALTERNATIVELY* - If your account has **mobile authentication enabled** you will have to take the code from the Steam mobile app and enter it into the popup window. You will need to enter a mobile authentication code every time you start this program, unless your save your 'shared secret' key to the settings file.
	
The shared secret is used by the mobile authenticator app to generate the auth code. If you save your shared secret in the settings.txt file then this program can automatically generate and enter auth codes each time you log in. To find your shared secret code use one of these methods:

- [iOS](http://forums.backpack.tf/index.php?/topic/45995-guide-how-to-get-your-shared-secret-from-ios-device-steam-mobile/)
- [Android (rooted)](http://forums.backpack.tf/index.php?/topic/46354-guide-how-to-find-the-steam-identity-secret-on-an-android-phone/)
- [Android (not rooted)](http://forums.backpack.tf/index.php?/topic/20204-backpacktf-automatic-help-thread/page-65#entry491155)

When you have your shared secret paste in in the `settings.txt` file after `//sharedsecret=` and remove the `//` from the start of the line.


#### Finding Market Data
1. Take the Steam Market URL of the item you want.(eg. http://steamcommunity.com/market/listings/730/%E2%98%85%20Gut%20Knife%20%7C%20Doppler%20%28Factory%20New%29)

2. Paste the URL into the Market URL box

3. Select the number of items to retrieve (1-3000).
**NOTE:** Using a high number such as 3000 will take a while, and using 3000 may cause Steam to throttle your connection for a few minutes. The Steam market only allows 100 results at a time, so 3000 items will query Steam 30 times.

4. Choose a currency and press 'Retrieve Items'.

5. Choose a Time Delay for each item in the process. If the time delay is too low Steam will not respond to the message in time and no more results will be added to the table.

6. Wait until the processing finishes. You may pause the program and continue by pressing 'Pause' and 'Start'. **NOTE:** If you pause the processing and want to start processing a new set of data, clear the table first.

7. Once the processing has finished you need to filter by float value to find the lowest one, and then take note of that item's position. The position represents the item's place in the Steam market at the time of gathering the data. If this position says '27' for example, it will be on the second page since Steam displays 10 items per page.

8. To get around this 10 item limit, add **'?query=&start=0&count=100'** to the end of the market URL in your browser. This will make Steam display 100 items per page. Now if your item is position '27' it will be shown on the first page. This makes using the Javascript market link easy.

9. The Javascript Market Link can be pasted into your browser address bar, but first you must manually type **'javascript:'**. This is due to browser security reasons. If the Steam item is on the current page, the Javascript link
 will bring up a dialog to buy the item. If this dialog does not come up, the item has either moved page since gathering data (usually to the next page), or has already been sold.

#### Additional Features
* Export as .CSV can be used to export the current contents of the table into a spreadsheet.
* Parse Single Item:
     - This option brings up a menu that allows you to enter an 'Inspect in game' link, and returns the float value for that skin. This can be used to find the float value for items from outside of the Steam Market.
You should not use this while processing market data, as this could mix the results up. Pause any processing first, and resume it after.
* Settings:
    - The settings file contains default settings for the program. The currency is set to 0 (USD) by default, but can be set to:
      - 1 for GBP
      - 2 for EUR
      - 3 for CHF
      - 4 for RUB
      - 5 for BRL
      - 6 for JPY
      - 7 for SEK
      - 8 for IDR
      - 9 for MYR
      - 10 for PHP
      - 11 for SGD
      - 12 for THB
      - 13 for KRW
      - 14 for TRY
      - 15 for MXN
      - 16 for CAD
      - 17 for NZD
      - 18 for CNY
      - 19 for INR
      - 20 for CLP
      - 21 for PEN
      - 22 for COP
      - 23 for ZAR
      - 24 for HKD
      - 25 for TWD
      - 26 for SRD
      - 27 for AED
    - The settings file will also contain your Steam username and password **IN PLAINTEXT** if you choose to check 'Remember Me' on the login form. You can delete these two lines if you have checked 'Remember Me' in the past and no longer want them remembered.
    - To enable basic debug logging, change `logging=0` to `logging=1`. For more verbose logging set this to `logging=2`.

## Information
Uses **[Pysteamkit](https://bitbucket.org/AzuiSleet/pysteamkit/overview)** - A Python [SteamKit](https://github.com/SteamRE/SteamKit) port by Aziusleet

If you wish to donate CS:GO skins as thanks, you can use my [trade link](https://steamcommunity.com/tradeoffer/new/?partner=12201816&token=J4sr6Irr).
