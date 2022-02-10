import json
from datetime import datetime
import yfinance as yf
import os.path

class EquiStrat():

    json_list = []
    targetEquityPercent = .60
    targetCashPercent = .40

    # --- CHANGE THESE VALUES ---
    fileName = "testing_intervals/07-15.json"
    startDate = "2007-01-03" #start date is the day money is deposited into account, change it to 
    endDate = "2015-01-03"
    initialEquity = 600000.0
    initialCash = 400000.0
    spFileName = 'testing_intervals/sp500_07-15.csv'
    # --- END CHANGE VALUES ---

    def __init__(self):

        self.writeInitialJson()

        self.grabJson()
        previousDay = self.json_list[-1]
        
        run = previousDay["run"]
        equity = previousDay["equity"]
        cash = previousDay["cash"]
        accountTwo = previousDay["accountTwo"]

        snpPercentChangeDate = self.fetchMarketData(run)
        snpPercentChange = snpPercentChangeDate[0]
        date=snpPercentChangeDate[1]

        postMarketEquity = self.equityChange(equity, snpPercentChange)
        postMarketAccountTwo = self.equityChange(accountTwo, snpPercentChange)

        if snpPercentChange<0:
            a = self.transferCash(cash, postMarketEquity)
            newEquity = a[0]
            newCash = a[1]
            newAccountOne = a[2]
            newAccountTwo = postMarketAccountTwo
        else:
            a = self.transferEquity(cash, postMarketEquity, equity, postMarketAccountTwo)
            newEquity = a[0]
            newCash = a[1]
            newAccountOne = a[2]
            newAccountTwo = a[3]

        self.writeToJson(run, newEquity, newCash, newAccountOne, newAccountTwo, date)
        #end init

    def writeInitialJson(self):

        file_exists = os.path.exists(self.fileName)
        if file_exists:
            return

        
        f = open(self.fileName, "w")
        initial_data = {
            "run": 1,
            "dateTime": self.startDate,
            "equity": self.initialEquity,
            "cash": self.initialCash,
            "accountOne": self.initialCash+self.initialEquity,
            "accountTwo": 0.0,
            "netWorth": self.initialEquity+self.initialCash
        }
        self.json_list.append(initial_data)
        json.dump(self.json_list, f, indent=4)
        f.close()
        return

    def grabJson(self):

        with open(self.fileName, "r") as openfile:
            json_object = json.load(openfile)
            for i in json_object:
                self.json_list.append(i)
        openfile.close()
        return

    def fetchMarketData(self, run):

        file_exists = os.path.exists(self.spFileName)
        if file_exists != True:
            sp500 = yf.Ticker('^GSPC')
            sp500_hist = sp500.history(start=self.startDate, end=self.endDate)
            sp500_hist.to_csv(self.spFileName)
        
        f=open(self.spFileName, "r")
        bigList=f.readlines()
        f.close()

        currentDay = bigList[run+1]
        previousDay = bigList[run]

        currentValues=currentDay.split(",")
        previousValues = previousDay.split(",")

        date = currentValues[0]
        newPrice = currentValues[4]
        previousPrice = previousValues[4]

        percentChange = (float(newPrice)-float(previousPrice))/float(previousPrice)*100
        print("S&P Percent Change for", date, ": ", percentChange)
        #percentChange = 2.5
        return percentChange, date

    def equityChange(self, equity, spPercentChange):
        newEquity = (equity*(spPercentChange/100))+equity
        return newEquity

    def transferCash(self, previousCash, postMarketEquity):
        #add cash to get to 60 40 again
        print("Negative Change, Add Cash to Get 60/40")
        newCashPercentAllocation = previousCash/(previousCash+postMarketEquity)
        percentDifference = newCashPercentAllocation - self.targetCashPercent

        total = postMarketEquity+previousCash
        
        diff = percentDifference*total

        newCashAmt = previousCash - diff
        newEquityAmt = postMarketEquity + diff

        newAccountOne = newCashAmt + newEquityAmt

        return newEquityAmt, newCashAmt, newAccountOne

    def transferEquity(self, cash, postEquity, preEquity, accountTwo):
        print("Positive Change, Tranfser Extra to Other Account")
        #move extra amt over 60% into 2nd account, still invested in snp

        extra = postEquity - preEquity

        newEquityAmt = postEquity - extra
        newAccountTwoAmt = accountTwo + extra
        newAccountOneAmt = newEquityAmt + cash

        return newEquityAmt, cash, newAccountOneAmt, newAccountTwoAmt

    def writeToJson(self, run, equity, oldCash, oldA1, oldA2, date):

        #dt=self.getDateTime()

        new_data={
            "run":run+1,
            "dateTime":date,
            "equity":(float("{:.3f}".format(equity))),
            "cash":(float("{:.3f}".format(oldCash))),
            "accountOne":(float("{:.3f}".format(oldA1))),
            "accountTwo":(float("{:.3f}".format(oldA2))),
            "netWorth":(float("{:.3f}".format(oldA1+oldA2)))
        }

        #new_json = json.dumps(new_data)

        with open(self.fileName, "r+") as file:
            file_data = json.load(file)
            file_data.append(new_data)
            file.seek(0)
            json.dump(file_data, file, indent=4)

        file.close()
        
        return


#while True:
    #instance = EquiStrat()

#instance = EquiStrat()