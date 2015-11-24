To get started, find a Steam Market item URL for the skin you want.
Then:
	1) Paste the URL into the Market URL box
	2) Select the number of items to retrieve (1-3000)
		NOTE: Using a high number such as 3000 will take a while, and using 3000 may cause Steam to throttle your connection for a few minutes.
		      The Steam website only allows 100 results at a time, so 3000 items will query Steam 30 times.
	3) Choose a currency and press 'Retrieve Items'
	4) Now that the program has gathered the data it will store it until you gather more data or close the program. Open CS:GO and once you have reached the main menu, alt-tab out.
	5) Next, choose a Time Delay for each item in the process. If the time delay is too low you will see float values start to repeat, this is because the skin has not loaded into the game yet, so the program is taking the previous skin's float value. If this occurs, raise the Time Delay and try again. A default value can be set in the settings.txt file.
	6) Wait until the processing finishes. You may pause the program and continue by pressing 'Pause' and 'Start'.
	7) Once the processing has finished you need to filter by float value to find the lowest one, and then take note of that item's position.
	   The position represents the item's place in the Steam market at the time of gathering the data. If this position says '27' for example, it will be on the second page since Steam displays 10 items per page.
	8) To get around this 10 item limit, add '?query=&start=0&count=100' to the end of the market URL in your browser. This will make Steam display 100 items per page.
	   Now if your item is position '27' it will be shown on the first page. This makes using the Javascript market link easy.
	9) The Javascript Market Link can be pasted into your browser address bar, but first you must manually type 'javascript:'. This is due to browser security reasons. If the Steam item is on the current page, the Javascript link
	   will bring up a dialog to buy the item. If this dialog does not come up, the item has either moved page since gathering data, or has already been sold.

Addition Features:
	- Export as .CSV can be used to export the current contents of the table into a spreadsheet.
	- Parse Single Item:
				This option brings up a menu that allows you to enter an 'Inspect in game' link, and returns the float value for that skin. This can be used to find the float value for items from outside of the Steam Market.
				You should not use this while processing market data, as this could mix the results up. Pause any processing first, and resume it after.
	- Settings:
				The settings file contains a few lines that the program reads from on startup.
				The User Settings contain default settings for the program. The currency is set to 0 (USD) buy default, but numbers 1-5 correspond with the currencies in the program. 1 being GBP etc.
				
				The Program Settings contain settings for the memory addresses of the float value. These may need to be changed if an update to CSGO breaks the program. Email or Steam Message me if this happens and I will tell you what to update these values to.
