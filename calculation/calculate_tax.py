import pandas as pd
from calculation.calculate_taxable_components import calculate_taxable_components

def calculate_tax(FYBuyRecords, FYSellRecords, FY):
    taxableComponents = {"CG > 1 Yr": 0,"CG < 1 Yr": 0, "CL": 0}

    # Keep a tracker of the current buy transaction we are at (starting at the first transaction)
    buyRecordTracker =  len(FYBuyRecords) - 1

    # Iterating through the sell records to link up appropriate buy records
    for i in range(len(FYSellRecords)):
        # Creating a dataframe to hold the buy records that we want to calculate
        buyRecordsTC = pd.DataFrame(columns=["Date", "Units", "Value"])

        # starting from the latest share sold and goes to the earliest share sold (0 index is the latest share sold)
        currSellTransaction = FYSellRecords.iloc[len(FYSellRecords) - (i + 1)]

        sellTransactionDate = currSellTransaction["Date"]
        sellTransactionUnits = currSellTransaction["Units"]

        # keeping a tracker of how many units are left
        remainingUnits = sellTransactionUnits

        # find the execution date, month and year from current sell transaction
        [day, month, year] = list(map(int, currSellTransaction["Date"].split("/")))

        # if sell date is inside of the current FY
        if year == FY and month < 7 or year == (FY - 1) and month > 6:
            # if there sell transaction has not been fully
            while remainingUnits > 0:
                # find the current buy record and its information
                currBuyTransaction = FYBuyRecords.iloc[buyRecordTracker]
                buyTransactionDate = currBuyTransaction["Date"]
                buyTransactionUnits = currBuyTransaction["Units"]

                # if the buy transaction is fully exhausted on the sell transaction, use all units and move to the next transaction,  then add to the transaction records
                if remainingUnits >= buyTransactionUnits:
                    remainingUnits -= buyTransactionUnits
                    buyRecordTracker -= 1

                    # Creating a pandas dataframe of date, units and value to add to the records of buy transactions to be calculated
                    processedBuyTransaction = pd.DataFrame({"Date": [currBuyTransaction["Date"]],
                                                            "Units": [currBuyTransaction["Units"]],
                                                            "Value": [currBuyTransaction["Units"] * currBuyTransaction["Price"] + currBuyTransaction["Brokerage Fee"]]})

                    # add the transaction to the records with the related information, used up all buy units therefore no use in messing with fees]
                    buyRecordsTC = pd.concat([buyRecordsTC, processedBuyTransaction])

                # If the buy transaction isn't fully exhausted on the sell transaction
                elif remainingUnits < buyTransactionUnits:
                    unitsUsed = remainingUnits
                    unitDifference = buyTransactionUnits - remainingUnits
                    remainingUnits = 0

                    # Value has to be manipulated to suit the mismatch between sale units and buy units
                    processedBuyTransaction = pd.DataFrame({"Date": [currBuyTransaction["Date"]],
                                                            "Units": [unitsUsed],
                                                            "Value": [(currBuyTransaction["Units"] * currBuyTransaction["Price"] + currBuyTransaction["Brokerage Fee"]) *  (unitsUsed/buyTransactionUnits)]})

                    # Add the transaction to the records with the related information
                    buyRecordsTC = pd.concat([buyRecordsTC, processedBuyTransaction])

                    # Changing the values of the original dataframe to make the fees associated with transactions match up
                    FYBuyRecords.at[buyRecordTracker, "Brokerage Fee"] = FYBuyRecords.iloc[buyRecordTracker]["Brokerage Fee"] * (unitDifference / buyTransactionUnits)
                    FYBuyRecords.at[buyRecordTracker, "Units"] = unitDifference

                # Calculate capital changes for the current sell transaction and add that to the total taxable components
            CG_after_1Yr, CG_Before_1Yr, CL = calculate_taxable_components(buyRecordsTC, currSellTransaction)
            taxableComponents["CG > 1 Yr"] += CG_after_1Yr
            taxableComponents["CG < 1 Yr"] += CG_Before_1Yr
            taxableComponents["CL"] += CL

        # If sell date is outside of current FY, no need to calculate change in value, just need to find and remove associated buy transactions
        else:
            # if there sell transaction has not been fully
            while remainingUnits > 0:
                # find the current buy record and its information
                buyTransaction = FYBuyRecords.iloc[buyRecordTracker]
                buyTransactionDate = buyTransaction["Date"]
                buyTransactionUnits = buyTransaction["Units"]


                # if the buy transaction is fully exhausted on the sell transaction, use all units and move to the next transaction
                if remainingUnits >= buyTransactionUnits:
                    remainingUnits -= buyTransactionUnits
                    buyRecordTracker -= 1


                # if the buy transaction is not fully exhausted on the sell transaction, use up all units and deduct the appropriate fee
                elif remainingUnits < buyTransactionUnits:
                    unitDifference = buyTransactionUnits - remainingUnits
                    remainingUnits = 0
                    # changing the values of the original dataframe to make the fees associated with transactions match up
                    FYBuyRecords.at[buyRecordTracker, "Brokerage Fee"] = FYBuyRecords.iloc[buyRecordTracker]["Brokerage Fee"] * (unitDifference / buyTransactionUnits)
                    FYBuyRecords.at[buyRecordTracker, "Units"] = unitDifference

    return taxableComponents
