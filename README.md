# ITk Timebased reporting

This is a quick tool to query the ITkdb and make live population timeline reports. Included is some basic code that should get the job done just make sure you get the paths right and download the right dependencies. I would recommend ```python3.9``` or above as some of the suff dosent work other wise. Try the tutorial first to see how the pipline works. Have a look at ```component migration plotting.pdf``` for some more info.

---
## Live reports
- [UK-CHINA cluster component population](https://cloud.datapane.com/apps/9ArQjrk/component-migration-strips/)
- [RAL Strips Stage population](https://cloud.datapane.com/apps/XknbLgk/component-stage-population-strips/)
- [RAL Strips Stage, Type and Trashed](https://cloud.datapane.com/apps/dA9o997/component-stage-population-with-trashed-strips/)
- [IZM Pixels Stage population](https://cloud.datapane.com/apps/Xknbv9k/component-stage-population-pixels/)
---
## Here's a quick start guide:


1. Run the tutorial this will give you the dependencies and walk you through the pulling the data from the itkdb,setting up and using [Influxdb](https://docs.influxdata.com/influxdb/v2.0/install/) to time stamp the data, then pulling the time stamped data in a pandas dataframe, building a basic plot in [Altair](https://altair-viz.github.io/index.html) and finally build a [datapane](https://docs.datapane.com) report to share the plot. This should take 10-15 minutes.
2. Try running a script, in the repo above I have included the code I have used to make the [live reports](#Live reports) linked above. just a couple things to note:
- Fill the ```myDetailes.py``` file with your access codes.
- You need to input the path to the folder in the ```function.py``` file.
- The Influx infomration: Organisation, token, bucket name ect. in the ```functions.py``` file.
- ```loopfile.py``` calls the functions from ```function.py``` and excicutes them so ```python3.9 loopfile.py``` should get the job done. you should have a datapane reoprt with your desired plot.
3. Automating, to automatically update the datapane report with the lateset data we use a little [shell script](https://github.com/ZefRozario/ITk_component_population_Timeline_reporting/blob/main/cron/reportingScriptExample.sh) to excuite the multiple ```loopfile.py``` files [crontab](https://crontab.guru/) will then excuite the shell script as frequently as you like, I'm currently doing every 3 hours so my command is ```0 */3 * * * source <path to>/QT/cron/reportingScriptExample.sh```. 
- To  crontab: in your terminal ```crontab -e``` then input your command like the one above followed by ```esc :wq```.


Finn,
God's speed ITk-er. 
