#!/usr/bin/env python
# coding: interpy

import sqlite3,os,re

from modules.db import db 
from modules.db import user 

import modules.logging.logger as logger

def fileExists(_file):
    return os.path.exists(_file)

def writeToDB(location_bool, coordinates, ip_addr): 
    if location_bool is None or coordinates is None or ip_addr is None:
        return
    elif not re.search("true|false", location_bool, re.I|re.M):
        logger.log("#{location_bool} is not a known mode.")
    elif not re.search("\A\((\d|\-\d)+\.\d+,\s(\d|\-\d)+\.\d+\)", coordinates, re.M | re.I): 
        logger.log("Improper coordinate format -> #{coordinates}.")
    elif not re.search("\A\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}$", ip_addr, re.M|re.I):
        logger.log("Improper ip address format -> #{ip_addr}.") 
    else:
        coor = re.sub("[\(\)]", "", str(coordinates))
        db.execute("insert into connected (location_bool, coordinates, ip_addr) values(\"#{location_bool}\", \"#{coor}\", \"#{ip_addr}\")")
        db.commit()

def readFromDB(column):
    query = db.execute("select * from connected")
    for row in query:
        if column == 'location_bool' and row[1] is not None:
            return str(row[1])
        elif column == 'coordinates' and row[2] is not None:
            return str(row[2])
        elif column == 'ip_addr' and row[3] is not None:
            return str(row[3])
        else:
            logger.log("Not a known column or DB is empty.") 
            return

def updateDB(column,value):
    if column is None or value is None:
        return
    try:
        if readFromDB('location_bool') is None or readFromDB('coordinates') is None or readFromDB('ip_addr') is None:
            logger.log("You must write to the database first before updating!")
            return
        elif re.search("true|false", value, re.I|re.M) and column == 'location_bool':
            db.execute("update connected set location_bool = \"#{value}\"")
            db.commit()
        elif re.search("\A(\d|\-\d)+\.\d+,\s(\d|\-\d)+\.\d+", value, re.M | re.I) and column == 'coordinates':    
            db.execute("update connected set coordinates = \"#{value}\"")
            db.commit()
        elif re.search("\A\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}$", value, re.M|re.I) and column == 'ip_addr':
            db.execute("update connected set ip_addr = \"#{value}\"")
            db.commit()
        else:
            logger.log("#{column} is not a known column for the connected table in the imagecapture db.")
            return
    except sqlite3.OperationalError:
      logger.log("The database is lock, could not add coordinates to DB.")

def addLocationToDB(location_bool):
    try:
        if readFromDB('location_bool') is None:
            writeToDB('NULL','NULL', location_bool)
        elif readFromDB('location_bool') is not location_bool and readFromDB('location_bool') is not None:
            updateDB('location_bool', location_bool)
    except sqlite3.OperationalError:
      logger.log("The database is lock, could not add location to DB.")

def addCoordinatesToDB(coordinates):
    try:
        if readFromDB('coordinates') is None:
            writeToDB('NULL','NULL', coordinates)
        elif readFromDB('coordinates') is not coordinates and readFromDB('coordinates') is not None:
            updateDB('coordinates', ip_addr)
    except sqlite3.OperationalError:
      logger.log("The database is lock, could not add coordinates to DB.")

def addIpToDB(ip_addr):
    try:
        if readFromDB('ip_addr') is None:
            writeToDB('NULL','NULL', ip_addr)
        elif readFromDB('ip_addr') is not ip_addr and readFromDB('ip_addr') is not None:
            updateDB('ip_addr', ip_addr)
    except sqlite3.OperationalError:
      logger.log("The database is lock, could not add IP address to DB.")
