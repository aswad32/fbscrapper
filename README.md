# Welcome to fbscrapper , experimenting with Scrapping facebook data without using API.

## Important
Please refer facebook Automated Data Collection Terms here https://www.facebook.com/apps/site_scraping_tos_terms.php?hc_location=ufi before you decide to use this script for automation. I will not responsible for anythings because I purposedly write this script for educational.

## Prerequisite:

* Python 2.7

* Mongodb

* Pymongo
``` 
pip install pymongo
```

* Selenium Web Driver
```
pip install selenium
```

* Beautiful Soup 
``` 
pip install beautifulsoup4
```

* PhantomJs.exe (include in the source folder - phantomjs, this is for windows only, if you want to run it on linux, please check your package manager for phantomjs)

* moment - formatting time from epoch to mongodb utc format
```
pip install moment
```

## Configuration
Before running the scripts, please do change the configuration files inside config/config.py.

```
username = (your facebook email)
pwd = (your facebook password)
```

Once done, to start the search open up command :
```
python __botfbquery__.py --qs "donal trump, digital ocean" --scroll 1
```


## Known Issues

```
WindowsError: [Error 32] The process cannot access the file because it is being used by another process: 'c:\\users\\aswad\\appdata\\local\\temp\\tmpwgs9pm'
```
Please refer to this stackoverflow link:
http://stackoverflow.com/questions/36153007/permission-error-if-to-use-phantomjs

This tools highly depends on Facebook layout, if there's a change on that, we need to revise back the code.
