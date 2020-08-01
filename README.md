# Watcher
This service will analyze data from [Nigeria's Open Treasury](https://opentreasury.gov.ng).

Fetch Data from source:
- Powershell script to get data in xlsx from source

Python Script to
- Convert xlsx to csv (use pandas for this)
- Trim and feed data into Kusto database
    - define scalable schema for different types of data ( we start with payment )
        - pick out mdas, federal govt
        - what are the sample questions we want to answer

Results of analysis will be served as:
- A dashboard displaying insights on different types of data (payment etc)
    - this can be a powerbi dashoard over kusto queries or plotly

After initial visualization,
- 2nd level analysis will be done on extracted data for anomaly detection on patterns
- Twitter bot with fire alert
    - alert will contain (rough overview)
    - link to dashboard vis that represents anomaly