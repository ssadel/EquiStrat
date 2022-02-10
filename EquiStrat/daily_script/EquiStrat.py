import json
from datetime import datetime
import yfinance as yf
import os.path


class EquiStrat():

    json_list = []
    targetEquityPercent = .60
    targetCashPercent = .40

    def __init__(self):
        print("\n-- Running EquiStrat Script --\n")
        
        self.grabJson()
        previousDay = self.json_list[-1]

        #stuff ill need to append to json later
        run = previousDay["run"]
        equity = previousDay["equity"]
        cash = previousDay["cash"]
        accountOne = previousDay["accountOne"]
        accountTwo = previousDay["accountTwo"]
        snpPercentChange = self.fetchMarketData()

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

        self.writeToJson(run, newEquity, newCash, newAccountOne, newAccountTwo)

        #end init

    def getDateTime(self):
        now = datetime.now()
        dt_string = now.strftime("%m/%d/%Y %H:%M")
        return dt_string

    def grabJson(self):
        with open("daily_script/data.json", "r") as openfile:
            json_object = json.load(openfile)
            for i in json_object:
                self.json_list.append(i)
        openfile.close()
        return

    def fetchMarketData(self):
        sp500 = yf.Ticker('^GSPC')
        sp500_hist = sp500.history(period='2d')
        sp500_hist.to_csv('daily_script/sp500_2d.csv')
        
        f=open("daily_script/sp500_2d.csv", "r")
        bigList=f.readlines()
        f.close()

        currentDay = bigList[-1]
        previousDay = bigList[-2]

        currentValues=currentDay.split(",")
        previousValues = previousDay.split(",")

        newPrice = currentValues[4]
        previousPrice = previousValues[4]

        percentChange = (float(newPrice)-float(previousPrice))/float(previousPrice)*100
        #percentChange = 2.5
        return percentChange

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

    def writeToJson(self, run, equity, oldCash, oldA1, oldA2):

        dt=self.getDateTime()

        new_data={
            "run":run+1,
            "dateTime":dt,
            "equity":(float("{:.3f}".format(equity))),
            "cash":(float("{:.3f}".format(oldCash))),
            "accountOne":(float("{:.3f}".format(oldA1))),
            "accountTwo":(float("{:.3f}".format(oldA2))),
            "netWorth":(float("{:.3f}".format(oldA1+oldA2)))
        }

        #new_json = json.dumps(new_data)

        with open("daily_script/data.json", "r+") as file:
            file_data = json.load(file)
            file_data.append(new_data)
            file.seek(0)
            json.dump(file_data, file, indent=4)

        file.close()
        
        return



instance = EquiStrat()

#print((float("{:.2f}".format(100.2353))))