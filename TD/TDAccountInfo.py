# -*- coding: utf-8 -*-
"""
Created on Wed Mar  3 09:35:27 2021

@author: LC
"""

import json
import pandas as pd

from datetime import datetime, timedelta
from pytz import timezone


class TDAccInf():

    def __init__(self, TDAPI, account_id = None, method='LIFO') -> None:

        """Initalizes a new instance of the Portfolio object.

        Keyword Arguments:
        ----
        TDAPI {obj} -- TD API instance object
        account_number {str} -- An accout number to associate with the Portfolio. (default: {None})
        method {str} -- 'LIFO' = Last In Fiert Out, FIFO = First in First Out. (default: {LIFO})
        """
        self.method = method
        self.account_id = account_id
        self.TDAPI = TDAPI
        self.initializing = True

        #Set time difference between local time and Eastern Standard Time
        self.deltaHours = round(((datetime.now().replace(tzinfo=None) - datetime.now(timezone('EST')).replace(tzinfo=None))).seconds/3600, 0)
        self.today = (datetime.today()-timedelta(hours=self.deltaHours)).strftime('%Y-%m-%d')

        #Positions
        self.init_positions()

        #Orders
        self.closing_orders()

        self.initializing = False

        #Balances
        self.balances_udpate()

    def __repr__(self):
        '''
            returns Account Value.
        '''

        # define the string representation
        return str(self.balances_accountValue)

    def init_positions(self) -> dict:

        self.account = self.TDAPI.get_accounts(account = self.account_id, fields = ['orders','positions'])['securitiesAccount']
        self.rawPositions = self.account['positions']
        self.todayOrders = self.account['orderStrategies']
        self.positions = {}

        # Loop through each position.
        for position in self.rawPositions:

            self.add_position(position)

    def todayOrdersToTransaction(self, symbol):
        # falta tener en cuenta las orden que abrieron y cerraron y no dejaron inguna posicion. Ver como mostralas
        todayTransactions = []

        for order in self.todayOrders:

            if order['orderLegCollection'][0]['instrument']['symbol'] == symbol:

                if (order['status'] == 'FILLED') or (order['status'] == 'QUEUED' and order['filledQuantity'] > 0):

                    for subOrder in order['orderActivityCollection']:

                        for executionLeg in subOrder['executionLegs']:
                            todayTransaction = {}
                            todayTransaction['transactionItem'] = {}
                            todayTransaction['fees'] = {}

                            if executionLeg['time'][:10] == self.today:
                                if order['orderLegCollection'][0]['instruction'] == 'BUY':
                                    todayTransaction['description'] = 'BUY TRADE'
                                    todayTransaction['transactionSubType'] = 'BY'
                                    todayTransaction['subAccount'] = 2
                                    todayTransaction['transactionItem']['instruction'] = 'BUY'
                                    sign = -1

                                elif order['orderLegCollection'][0]['instruction'] == 'SELL':
                                    todayTransaction['description'] = 'SELL TRADE'
                                    todayTransaction['transactionSubType'] = 'SL'
                                    todayTransaction['subAccount'] = 2
                                    todayTransaction['transactionItem']['instruction'] = 'SELL'
                                    sign = 1

                                elif order['orderLegCollection'][0]['instruction'] == 'SELL_SHORT':
                                    todayTransaction['description'] = 'SHORT SALE'
                                    todayTransaction['transactionSubType'] = 'SS'
                                    todayTransaction['subAccount'] = 4
                                    todayTransaction['transactionItem']['instruction'] = 'SELL'
                                    sign = 1

                                if order['orderLegCollection'][0]['instruction'] == 'BUY_TO_COVER':
                                    todayTransaction['description'] = 'CLOSE SHORT POSITION'
                                    todayTransaction['transactionSubType'] = 'CS'
                                    todayTransaction['subAccount'] = 4
                                    todayTransaction['transactionItem']['instruction'] = 'BUY'
                                    sign = -1

                                todayTransaction['transactionItem']['amount'] = executionLeg['quantity']
                                todayTransaction['transactionItem']['price'] = executionLeg['price']
                                todayTransaction['transactionItem']['accountId'] = order['accountId']
                                todayTransaction['transactionItem']['cost'] = sign * executionLeg['quantity'] * executionLeg['price']
                                todayTransaction['transactionItem']['instrument'] = order['orderLegCollection'][0]['instrument']

                                todayTransaction['fees']['regFee'] = 0.00
                                todayTransaction['fees']['secFee'] = 0.00
                                todayTransaction['fees']['additionalFee'] = 0.00
                                todayTransaction['fees']['cdscFee'] = 0.00
                                todayTransaction['fees']['commission'] = 0.00
                                todayTransaction['fees']['optRegFee'] = 0.00
                                todayTransaction['fees']['otherCharges'] = 0.00
                                todayTransaction['fees']['rFee'] = 0.00

                                todayTransaction['transactionDate'] = executionLeg['time']
                                todayTransaction['cashBalanceEffectFlag'] = True
                                todayTransaction['type'] = 'TRADE'
                                todayTransaction['orderDate'] = order['enteredTime']
                                todayTransaction['orderId'] = order['orderId'] # ver como agregar T antes del ID
                                todayTransaction['netAmount'] = todayTransaction['transactionItem']['cost']
                                todayTransaction['settlementDate'] = None
                                todayTransaction['transactionId'] = None

                                todayTransactions.append(todayTransaction)

        def get_date(todayTransaction)  :
            return todayTransaction.get('transactionDate')

        todayTransactions.sort(key=get_date, reverse=True)

        return(todayTransactions)

    def add_position(self, position):

        symbol = position['instrument']['symbol']

        quantity = position['longQuantity'] - position['shortQuantity'] ## To have positivequantity when long and negative quantity when short

        # Add the position.
        self.positions[symbol] = {}
        self.positions[symbol]['symbol'] = symbol
        self.positions[symbol]['quantity'] = quantity
        self.positions[symbol]['average_price'] = position['averagePrice']
        self.positions[symbol]['holding_date'] = None
        self.positions[symbol]['asset_type'] = position['instrument']['assetType']
        self.positions[symbol]['target_value'] = 0.00
        self.positions[symbol]['stoplose_value'] = 0.00
        self.positions[symbol]['current_value'] = 0.00
        self.positions[symbol]['breakeven_value'] = 0.00
        self.positions[symbol]['noCloseQuantity'] = 0
        self.positions[symbol]['transactions'] = []
        self.positions[symbol]['closingOrders'] = []
        self.positions[symbol]['LIFO'] = {}
        self.positions[symbol]['LIFO']['holdings'] = []
        self.positions[symbol]['LIFO']['date'] = 0
        self.positions[symbol]['LIFO']['average_price'] = 0.00
        self.positions[symbol]['LIFO']['breakeven_value'] = 0.00
        self.positions[symbol]['LIFO']['results'] = 0.00
        self.positions[symbol]['FIFO'] = {}
        self.positions[symbol]['FIFO']['holdings'] = []
        self.positions[symbol]['FIFO']['date'] = 0
        self.positions[symbol]['FIFO']['average_price'] = 0.00
        self.positions[symbol]['FIFO']['breakeven_value'] = 0.00
        self.positions[symbol]['FIFO']['results'] = 0.00
        self.positions[symbol]['rawPosition'] = position

        # Get lastes trades on the position, to create transaction list since position was 0
        trades = self.todayOrdersToTransaction(symbol)

        self.positions[symbol]['trades'] = self.TDAPI.get_transactions(account = self.account_id, transaction_type = 'TRADE', symbol = symbol)

        trades.extend(self.positions[symbol]['trades'])

        sign = quantity/quantity
        for trade in trades:
            if quantity != 0:
                orderType = trade['transactionItem']['instruction']

                if orderType == 'BUY':
                    trade_quantity = trade['transactionItem']['amount']

                else:
                    trade_quantity = -trade['transactionItem']['amount']

                self.positions[symbol]['transactions'].append(trade)

                quantity -= trade_quantity*sign

        self.positions[symbol]['transactions'].reverse()

        # Create Holding LIFO an FIFO from transactions
        quantity = position['longQuantity'] - position['shortQuantity']

        for transaction in self.positions[symbol]['transactions']:
            # print "PROCESSING TRANSACTION #{} ...".format(str(transactionNum))

            if (transaction['transactionSubType'] == 'BY') or (transaction['transactionSubType'] == 'SS'):
                # print "Transaction #{} is a buy. ADDING TO HOLDINGS ...".format(str(transactionNum))
                self.addToHoldings(transaction,symbol)
            else:
                #pass
                # print "Transaction #{} is a sell. SUBTRACTING FROM HOLDINGS ...".format(str(transactionNum))
                self.removeFromHoldings_fifo(transaction,symbol)
                self.removeFromHoldings_lifo(transaction,symbol)

        self.avgPrice(symbol)
        self.positions[symbol]['LIFO']['date'] = self.positions[symbol]['LIFO']['holdings'][0]['date']
        self.positions[symbol]['FIFO']['date'] = self.positions[symbol]['FIFO']['holdings'][0]['date']
        self.positions[symbol]['holding_date'] = self.positions[symbol][self.method]['date']

    # Add Holdings
    def addToHoldings(self, t, symbol):
        orderType = t['transactionItem']['instruction']
        if orderType == 'BUY':
            quantity = t['transactionItem']['amount']

        else:
            quantity = -t['transactionItem']['amount']

        price = t['transactionItem']['price']
        totalFees = t['fees']['regFee']+t['fees']['secFee']

        priceWithFeesPerUnit = round(((price*quantity) + totalFees) / quantity, 2)

        h = {}
        h['quantity'] = quantity
        h['price'] = t['transactionItem']['price']
        h['priceWFee'] = priceWithFeesPerUnit
        h['date'] = t['transactionDate']
        h['-sign'] = quantity/abs(quantity)
        self.positions[symbol]['FIFO']['holdings'].append(h)

        h = {}
        h['quantity'] = quantity
        h['price'] = t['transactionItem']['price']
        h['priceWFee'] = priceWithFeesPerUnit
        h['date'] = t['transactionDate']
        h['-sign'] = quantity/abs(quantity)
        self.positions[symbol]['LIFO']['holdings'].append(h)
        if not self.initializing:
            self.avgPrice(symbol)


    # Remove Holdings
    def removeFromHoldings_fifo(self, t, symbol):

        quantity = t['transactionItem']['amount']
        price = t['transactionItem']['price']
        fees = t['fees']['regFee']+t['fees']['secFee']

        gainLoss = 0

        transactionFullyAccountedFor = False
        while transactionFullyAccountedFor != True:
            # Check if there are enough in first holding
            # if exactly enough, remove first holding & done w/ removing holdings

            sign = self.positions[symbol]['FIFO']['holdings'][0]['-sign']
            holdingQuant = self.positions[symbol]['FIFO']['holdings'][0]['quantity']*sign
            holdingBasis = self.positions[symbol]['FIFO']['holdings'][0]['priceWFee']
            if holdingQuant == quantity:

                gainLoss += round(sign*(quantity*price - quantity*holdingBasis)-fees,2)
                self.positions[symbol]['FIFO']['holdings'].pop(0)
                transactionFullyAccountedFor = True # Done with removing.

            elif quantity < holdingQuant:

                gainLoss += round(sign*(quantity*price - quantity*holdingBasis)-fees,2)
                self.positions[symbol]['FIFO']['holdings'][0]['quantity'] -= quantity*sign
                transactionFullyAccountedFor = True # Done with removing.

            else: # Quantity sold exceeds value of the first remaining holding

                gainLoss += round(sign*(holdingQuant*price - holdingQuant*holdingBasis),2)
                quantity -= holdingQuant
                self.positions[symbol]['FIFO']['holdings'].pop(0)
                # NOT done with removing. Continue.

        self.positions[symbol]['FIFO']['results'] += round(gainLoss,2)
        if not self.initializing:
            self.avgPrice(symbol)

    def removeFromHoldings_lifo(self, t, symbol):

        quantity = t['transactionItem']['amount']
        price = t['transactionItem']['price']
        fees = t['fees']['regFee']+t['fees']['secFee']

        gainLoss = 0

        transactionFullyAccountedFor = False
        while transactionFullyAccountedFor != True:
            # Check if there are enough in first holding
            # if exactly enough, remove first holding & done w/ removing holdings
            sign = self.positions[symbol]['FIFO']['holdings'][0]['-sign']
            holdingQuant = self.positions[symbol]['LIFO']['holdings'][-1]['quantity']*sign
            holdingBasis = self.positions[symbol]['LIFO']['holdings'][-1]['priceWFee']
            if holdingQuant == quantity:

                gainLoss += round(sign*(quantity*price - quantity*holdingBasis)-fees,2)
                self.positions[symbol]['LIFO']['holdings'].pop(-1)
                transactionFullyAccountedFor = True # Done with removing.

            elif quantity < holdingQuant:

                gainLoss += round(sign*(quantity*price - quantity*holdingBasis)-fees,2)
                self.positions[symbol]['LIFO']['holdings'][-1]['quantity'] -= quantity*sign
                transactionFullyAccountedFor = True # Done with removing.

            else: # Quantity sold exceeds value of the first remaining holding

                gainLoss += round(sign*(holdingQuant*price - holdingQuant*holdingBasis),2)
                quantity -= holdingQuant
                self.positions[symbol]['LIFO']['holdings'].pop(-1)
                # NOT done with removing. Continue.

        self.positions[symbol]['LIFO']['results'] += round(gainLoss,2)
        if not self.initializing:
            self.avgPrice(symbol)


    # Calc AvrPrice FIFO and LIFO
    def avgPrice(self, symbol):
        CapitalLIFO = 0
        CapitalFIFO = 0
        TotalQuant = 0
        for holding in self.positions[symbol]['LIFO']['holdings']:
            CapitalLIFO += holding['priceWFee'] * holding['quantity']
            TotalQuant += holding['quantity']
        for holding in self.positions[symbol]['FIFO']['holdings']:
            CapitalFIFO += holding['priceWFee'] * holding['quantity']

        self.positions[symbol]['LIFO']['average_price'] = round(CapitalLIFO/TotalQuant,2)
        self.positions[symbol]['FIFO']['average_price'] = round(CapitalFIFO/TotalQuant,2)
        self.positions[symbol]['average_price'] = self.positions[symbol][self.method]['average_price']
        self.positions[symbol]['quantity'] = TotalQuant


   # check the closing position orders to calculate target values
    def closing_orders(self):  ### Falta para short
        queued_orders = self.TDAPI.get_orders_path(account = self.account_id, status = 'QUEUED')
        for order in queued_orders:
            if order['orderLegCollection'][0]['positionEffect'] == 'CLOSING':
                symbol = order['orderLegCollection'][0]['instrument']['symbol']
                self.positions[symbol]['closingOrders'].append(order)

        for symbol in self.positions:
            sign = self.positions[symbol]['FIFO']['holdings'][0]['-sign']
            Quantity = self.positions[symbol]['quantity']
            self.positions[symbol]['target_value'] = 0

            for order in self.positions[symbol]['closingOrders']:

                self.positions[symbol]['target_value'] += round(order['price']*order['remainingQuantity'],2)
                Quantity -= sign * order['remainingQuantity']

            if Quantity != 0:
                print("There are {} shares of {} without exit position".format(Quantity,symbol))
                self.positions[symbol]['noCloseQuantity'] = Quantity
                self.positions[symbol]['target_value'] += Quantity * self.positions[symbol]['average_price']


    def current_liquidation_price(self, symbol,quantity):
        # Returns liquidationPrice as Mark if it is between Bid and Ask or Bid/Ask depending if the position is short or long.
        quote = self.TDAPI.get_quote(instruments = symbol)
        Mark = round(quote[symbol]['mark'],2)
        Bid = round(quote[symbol]['bidPrice'],2)
        Ask = round(quote[symbol]['askPrice'],2)
        prevDayClose = round(quote[symbol]['closePrice'],2)

        if quantity > 0:
                liquidationPrice = Bid
        else:
                liquidationPrice = Ask

        if Ask>Mark and Mark>Bid:
            currentPrice =  Mark
            liquidationPrice = Mark
        elif Ask>Mark and Bid>Mark:
            currentPrice =  Bid
        else:
            currentPrice =  Ask

        return (currentPrice, liquidationPrice, prevDayClose)

    # Update all balances.
    def balances_udpate(self):
        # Updates average prices, breakeven prices, target value, curret value
        account = self.TDAPI.get_accounts(account = self.account_id, fields = ['positions'])['securitiesAccount']

        self.currentBalances = account['currentBalances']
        self.initialBalances = account['initialBalances']

        self.CashSweepVehicle = self.currentBalances['marginBalance'] + self.currentBalances['cashBalance'] + self.currentBalances['shortBalance']

        self.balances_breakeven = self.CashSweepVehicle
        self.balances_accountValue = self.CashSweepVehicle
        self.balances_target_value = self.CashSweepVehicle

        for symbol in self.positions:
            self.positions[symbol]['LIFO']['breakeven_value'] = 0
            self.positions[symbol]['FIFO']['breakeven_value'] = 0
            self.positions[symbol]['current_value'] = 0

            averagePriceLIFO = round(self.positions[symbol]['LIFO']['average_price'],2)
            averagePriceFIFO = round(self.positions[symbol]['FIFO']['average_price'],2)
            self.positions[symbol]['average_price'] = self.positions[symbol][self.method]['average_price']

            quantity = round(self.positions[symbol]['quantity'],2)

            currentPrice, liquidationPrice, prevDayClose = self.current_liquidation_price(symbol,quantity)
            if quantity<0:
                self.positions[symbol]['shortBalance'] = -prevDayClose * quantity

            self.positions[symbol]['LIFO']['breakeven_value'] += round(averagePriceLIFO*quantity,2)
            self.positions[symbol]['FIFO']['breakeven_value'] += round(averagePriceFIFO*quantity,2)
            self.positions[symbol]['breakeven_value'] = self.positions[symbol][self.method]['breakeven_value']
            self.balances_breakeven += self.positions[symbol]['breakeven_value']

            self.positions[symbol]['current_value'] = round(liquidationPrice*quantity,2)
            self.balances_accountValue += self.positions[symbol]['current_value']

            self.balances_target_value += self.positions[symbol]['target_value']

