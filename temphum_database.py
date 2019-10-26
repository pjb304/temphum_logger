"""
    Philip Basford
    October 2019
"""
from datetime import datetime
from configobj import ConfigObj

import MySQLdb

class TempHumDatabase:
    """
        Handle the database I/O for the temperature/Humidity logger
    """

    def __init__(self, filename):
        """
            Read the config and connect to the database
        """
        self.filename = filename
        self.read_config()
        self.connect_database()

    def read_config(self):
        """
            Parse the required config file
        """
        config = ConfigObj(self.filename)
        self.host = config["host"]
        self.user = config["user"]
        self.password = config["password"]
        self.database = config["database"]


    def connect_database(self):
        """
            Open the connection to the database
        """
        self.db = MySQLdb.connect(
            host=self.host,
            user=self.user,
            passwd=self.password,
            db=self.database)

    def store_reading(self, device, temperature, humidity=None, retry=False):
        """
            Store the reading into the database
            Uses the current timestamp for the reading
            humidity can be None
            By default it will retry once if the connection to the database fails
            The is handled recursively - it will set the retry flag to true on 2nd attempt
        """
        try:
            cursor = self.db.cursor()
            cursor.execute(
                "INSERT INTO temphum_readings (timestamp, device, temperature, humidity) VALUES (%s, %s, %s, %s);",
                (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), device, temperature, humidity))
            cursor.close()
            self.db.commit()
        except MySQLdb.OperationalError:
            if not retry:
                self.connect_database()
                self.store_reading(device, temperature, humidity, True)
            else:
                raise
