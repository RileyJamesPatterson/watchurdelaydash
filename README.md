# WatchUrDelay

### DESCRIPTION
WatchUrDelay is web based tool that provides flight delay predictions on a rich user interface. It uses machine learning models built on ~18 million records of flights within USA to provide a probabilistic estimate of delay of a flight between two airports; upto 7 days into the future. 

The application is accesible to only the people in Georgia Institute of Technology.
We recommend using `Google Chrome` for accessing the web app.
### INSTALLATION
NOTE: Ensure that `python version >= 3.8` is installed on your local machine and accesible in terminal under the command `python3`
1. Download the contents of  [WatchUrDelay](https://gtvault.sharepoint.com/:u:/s/CSE6242-Spring23/EY3IYksgIbpIiMnGvriVuHEBXg8-XNfiZgRfe0voDj0g2w?e=ieIy18) package (must be logged in with GaTech credentials)
2. Extract the contents of the downloaded `.zip` package and open the extracted folder
3. Open the terminal in the `WatchUrDelay` directory and run the commands below:
    ``` bash
    python3 -m venv delay
    ```
    ``` bash
    source delay/bin/activate
    ```
    ``` bash
    python3 -m pip install -r requirements.txt
    ```
    ``` bash
    python3 app.py
    ```
4. Wait for the server to start. The server is ready when the following message is displayed in the terminal:
    ``` bash
    Dash is running on http://127.0.0.1:8050/
    ```
5. The webapp can now be accesed on `http://127.0.0.1:8050/`

### EXECUTION
1. On the home screen you will see a map of the USA (incl. Alaska and Hawaii) and each blue dot on it is the supported departure airport. You can hover over the dots to get more information about the airport
2. Select the Departure Airport based on the `IATA` code of that airport. [ex: ATL for Hartsfield–Jackson Atlanta International Airport]
    1. As you do that you will see that this airport is highlighted on the map as a `red` dot and the number of `blue` dots reduce to reflect the supported Arrival Airports for the selected Departure Airport
3. You can now select an Arrival Airport from prepopulated list in the dropdown. [ex: ORD for Chicago O'Hare International Airport]
    1. As you do that the Arrival Airport will be marked as a `yellow` dot on the map and the three other charts will appear as well highlighting predictive and historical delay information for those two destination. 
4. You can select a Departure Date from the widget at top roght; upto 7 days into the future. [ex: (at the time of writing): April 20, 2023]
5. You can then select Departure Hour (an integer from `0` to `23`). [ex: 13]
6. Note that the Weather widget at the bottom also updates to reflect the weather data for the two airports aggregated by hour selected.
7. In the Delay Prediction chart you can see the Probability distribution function and a bar chart indicating the probability of delays.