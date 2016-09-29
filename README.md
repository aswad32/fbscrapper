# Welcome to fbscrapper , experimenting with Scrapping facebook data without using API.

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

* PhantomJs.exe (include in the source folder - phantomjs)

* moment - formatting time from epoch to mongodb utc format
```
pip install moment
```

## Configuration
Before running the scripts, please do change the configuration files inside config/config.py.

```
username = (your facebook email)
pwd = (your facebook password)
query = [(array of string query)] e.g: ['digital ocean', 'nodejs'] 
```

Once done, to start the search open up command :
```
python __botfbquery__.py
```


## Known Issues

```
WindowsError: [Error 32] The process cannot access the file because it is being used by another process: 'c:\\users\\aswad\\appdata\\local\\temp\\tmpwgs9pm'
```

Please refer to this stackoverflow link:
http://stackoverflow.com/questions/36153007/permission-error-if-to-use-phantomjs
