from mesa import Agent, Model
import random
import numpy as np

class InitAgent(Agent):
    def __init__(self,unique_id, model):
        super().__init__(unique_id, model)

        self.hour = 0
        self.day = 0
        self.week = 0

        self.price = 0
        self.other_price = 0
        self.number_of_cars = 0

    def calculatePrice(self):
        self.price = round(random.uniform(50,200),1)
        print("Price {}".format(self.price))

    def priceForOtherParkings(self):
        self.other_price = round(random.uniform(100,200),1)
        print("Other Parking price {}".format(self.price))

    def step(self):
        print("Hour {}".format(self.hour))
        print("Day {}".format(self.day))
        print("Week {}".format(self.week))
        self.calculatePrice()
        self.priceForOtherParkings()

        self.hour += 1

        if self.hour > 23:
            self.day += 1
            self.hour = 0

        if self.day > 7:
            self.week += 1
            self.day = 0

class TradeInterface(Agent):
    def __init__(self,unique_id, model):
        super().__init__(unique_id, model)
        self.hour = 0
        self.day = 0
        self.week = 0

        self.buyers = []
        self.sellers = []

        self.demands = []
        self.productions = []

        self.demandPrice = []
        self.supplyPrice = []

        self.historyDemands = []
        self.historyProductions = []

        self.distributedDemands = []
        self.summedDemands = []

        self.buyerPriceList = []
        self.clearPriceList = []
        self.satisfiedDemands = []

        self.demandCount = 0

        self.dealCount = 0
        self.noDealCount = 0

        self.dealsList = []
        self.noDealsList = []

        self.buyerPrices = []
        self.sellerPrices = []

        self.commonPrice = 0
        self.clearPrice = 0

        self.numberOfBuyers = 0
        self.numberOfSellers = 0

    def getSellers(self):
        self.sellers = []
        self.numberOfSellers = 0
        for agent in self.model.schedule.agents:
            if (isinstance(agent, ParkingSlotAgent)):
                if agent.readyToSell is True:
                    self.numberOfSellers += 1
                    self.sellers.append(agent.unique_id)
        self.historyProductions.append(self.numberOfSellers)
        print("Sellers {}".format(self.sellers))
        print("Number of sellers {}".format(self.numberOfSellers))

    def getBuyres(self):
        self.buyers = []
        self.numberOfBuyers = 0
        for agent in self.model.schedule.agents:
            if (isinstance(agent, CarAgent)):
                if agent.readyToBuy is True:
                    self.numberOfBuyers += 1
                    self.buyers.append(agent.unique_id)
        self.historyDemands.append(self.numberOfBuyers)
        print("Buyers {}".format(self.buyers))
        print("Number of buyers {}".format(self.numberOfBuyers))


    def updatePrice(self,new_price):
        for agent in self.model.schedule.agents:
            if (isinstance(agent, ParkingSlotAgent) and agent.readyToSell is True):
                agent.price = new_price

    def chooseSeller(self,buyer,price=None,amount = None):
        if len(self.sellers) > 0:
            seller = np.random.choice(self.sellers)
        for agent in self.model.schedule.agents:
            if (isinstance(agent, ParkingSlotAgent) and agent.readyToSell is True):
                if  agent.unique_id == seller:
                    print("Seller {}".format(agent.unique_id))
                    print("Seller price {}".format(agent.price))

                    if buyer.price >= agent.price:
                        print("Deal !")
                        agent.status = 'busy'
                        agent.readyToSell = False
                        agent.busyTime = buyer.parkingTime

                        buyer.status = 'busy'
                        buyer.readyToBuy = False
                        buyer.busyTime = buyer.parkingTime

                        self.buyerPrices.append(buyer.price)
                        self.sellerPrices.append(agent.price)

                        print("Car busy time {}".format(buyer.busyTime))
                        print("Slot busy time {}".format(agent.busyTime))

                        self.numberOfBuyers -= 1
                        self.numberOfSellers -= 1
                        self.demandCount += 1

                        self.dealCount += 1

                        #write to queue
                        agent.queue.append(buyer.unique_id)
                        print("Queue {}".format(agent.queue))

                        #update price for all other parking slots
                        new_price = round(np.mean([agent.price, buyer.price]),1)

                        self.clearPriceList.append(new_price)
                        self.updatePrice(new_price)

                        self.buyers.remove(buyer.unique_id)
                        self.sellers.remove(agent.unique_id)

                    else:
                        print('No deal')
                        new_price = round(np.mean([agent.price, buyer.price]), 1)
                        self.updatePrice(new_price)

                        self.noDealCount += 1
                        buyer.calculatePrice()

    def distributeParking(self):
        self.sellPrice = 0
        self.buyPrice = 0
        self.demandCount = 0
        self.dealCount = 0
        self.noDealCount = 0
        while(not(self.numberOfSellers <= 0 or self.numberOfBuyers <= 0)):
            buyer_id = np.random.choice(self.buyers)
            print("Buyer Random ID {}".format(buyer_id))
            for agent in self.model.schedule.agents:
                if (isinstance(agent, CarAgent) and agent.readyToBuy is True):
                    if agent.unique_id == buyer_id:
                        self.buyPrice = agent.price
                        print("Buyer {}".format(agent.unique_id))
                        print("Buy price {}".format(agent.price))
                        self.chooseSeller(agent)

        if self.numberOfBuyers > 0 and self.numberOfSellers <= 0:
            print("Not enough place")
            car_list = []
            for agent in self.model.schedule.agents:
                if (isinstance(agent, CarAgent)):
                    if agent.readyToBuy is True:
                        car_list.append(agent.unique_id)
            print("Cars left {}".format(car_list))


        elif self.numberOfBuyers == 0 and self.numberOfSellers > 0:
            print("Place left")

        else:
            print("No sellers and No buyers")
        self.dealsList.append(self.dealCount)
        self.noDealsList.append(self.noDealCount)

    def step(self):
        print("Trade")
        self.getBuyres()
        self.getSellers()
        self.distributeParking()

        self.hour += 1

        if self.hour > 23:
            self.day += 1
            self.hour = 0

        if self.day > 7:
            self.week += 1
            self.day = 0


class CarAgent(Agent):
    def __init__(self,unique_id, model):
        super().__init__(unique_id, model)
        self.hour = 0
        self.day = 0
        self.week = 0
        self.statusPriority = None
        self.needToWash = False
        self.wantToPark = True
        self.traided = None
        self.parkingTime = 0#demand

        self.busyTime = 0

        self.status = 'free'

        self.priceHistory = []
        self.priorityHistorySell = []
        self.priorityHistoryBuy = []

        self.readyToSell = False
        self.readyToBuy = True

    def checkBusyTime(self):
        if self.busyTime > 0:
            self.status = 'busy'
            self.wantToPark = False
            self.busyTime -= 1
        else:
            self.busyTime = 0
            self.status = 'free'
        print("Busy time {}".format(self.busyTime))

    def getParkingTime(self): #demand for parking, hourly
        if not self.wantToPark:
            self.parkingTime = 0
        else:
            self.parkingTime = random.randint(1,5) #from 1 to max available time of parking
        print("Desirable parking time {}".format(self.parkingTime))

    def name_func(self):
        print("Agent {}".format(self.unique_id))

    def checkIfPark(self):
        if self.status == 'free':
            if self.hour >= 7 and self.hour <= 9:
                self.wantToPark = np.random.choice([True, False], p=[0.9, 0.1])
            elif self.hour >= 15 and self.hour <= 17:
                self.wantToPark = np.random.choice([True, False], p=[0.9, 0.1])
            else:
                self.wantToPark = np.random.choice([True, False])
        print("Want to park {}".format(self.wantToPark))

    def getParkingStatus(self):
        self.status = 'free'
        print("Status {}".format(self.status))

    def getTradeStatus(self):
        if self.wantToPark:
            self.readyToBuy = True
        else:
            self.readyToBuy = False

    def calculatePrice(self):
        self.price = round(random.uniform(50,200),1) #price for parking, NOK
        print("Price {}".format(self.price))

    def step(self):
        self.name_func()
        self.checkBusyTime()
        self.checkIfPark()
        self.getTradeStatus()
        self.getParkingTime()
        self.calculatePrice()
        self.hour += 1

        if self.hour > 23:
            self.day += 1
            self.hour = 0

        if self.day > 7:
            self.week += 1
            self.day = 0

class ParkingSlotAgent(Agent):
    def __init__(self,unique_id, model):
        super().__init__(unique_id, model)
        self.hour = 0
        self.day = 0
        self.week = 0

        self.price = 0
        self.status = 'free' #can be free or busy
        self.queue = []
        self.amountOfHours = 0
        self.readyToSell = True

        self.availableTime = 0
        self.busyTime = 0

    def updateQueue(self):
        if self.status == 'free':
            self.queue = []

    def checkBusyTime(self):
        if self.busyTime > 0:
            self.status = 'busy'
            self.wantToPark = False
            self.busyTime -= 1
        else:
            self.busyTime = 0
            self.status = 'free'
        print("Busy time {}".format(self.busyTime))

    def getSellStatus(self):
        if self.status == 'free':
            self.readyToSell = True
        else:
            self.readyToSell = False
        print("Ready to Sell {}".format(self.readyToSell))

    def getStatus(self):
        self.status = random.choice(['free','busy'])
        print(self.status)

    def calculatePrice(self):
        self.price = round(random.uniform(50,200),1) #price for parking, NOK
        print("Price {}".format(self.price))

    def setPrice(self):
        for agent in self.model.schedule.agents:
            if (isinstance(agent, InitAgent)):
                self.price = agent.price
        print("Price {}".format(self.price))

    def name_func(self):
        print("Agent {}".format(self.unique_id))

    def step(self):
        self.name_func()
        self.checkBusyTime()
        self.updateQueue()
        self.getSellStatus()
        self.setPrice()
        self.hour += 1

        if self.hour > 23:
            self.day += 1
            self.hour = 0

        if self.day > 7:
            self.week += 1
            self.day = 0