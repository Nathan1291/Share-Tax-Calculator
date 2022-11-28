import pandas as pd
import numpy as np
import os


def processing():
    # transforming csv file into pandas dataframe
    pDir = os.path.dirname(os.getcwd())
    recordsDataframe = pd.read_csv(pDir + "\\records\\records.csv")

    # Intialising empty dataframes to store the buy records and the sell records
    buyRecords = pd.DataFrame(columns=["Date","Share", "Price","Units", "Brokerage Fee"])
    sellRecords = pd.DataFrame(columns=["Date","Share", "Price","Units", "Brokerage Fee"])


    # pulling the date, details and either debit or credit column out of the desired transactions
    for i in range(len(recordsDataframe)):
        currRecord = recordsDataframe.iloc[i]

        # Check implemented to reduce time complexity such that the code only runs if it is a buy or sell transaction
        if currRecord["Details"][0] == "B" or currRecord["Details"][0] == "S":

            # extracting stock info
            detailsList = str(currRecord["Details"]).split()
            date = currRecord["Date"]
            shareName = detailsList[2]
            price = float(detailsList[4])
            units = int(detailsList[1])

            # Finding whether the transaction is classified as a debit or a credit to help classify if it is a buy or sell transaction
            # while also knowing whether it is a buy or sell transaction
            if np.isnan(currRecord["Credit($)"]):

                # appending the current record to the appropriate location
                recordInfo = {"Date": date, "Share": shareName, "Price": price, "Units": units, "Brokerage Fee": round(currRecord["Debit($)"] - price * units, 2)}
                buyRecords = pd.concat([buyRecords, pd.DataFrame([recordInfo])], ignore_index=True)

            # Same process as buy transactions but for sell transactions
            else:
                recordInfo = {"Date": date, "Share": shareName, "Price": price, "Units": units, "Brokerage Fee": round(price * units - currRecord["Credit($)"], 2)}
                sellRecords = pd.concat([sellRecords, pd.DataFrame([recordInfo])], ignore_index=True)

    return buyRecords, sellRecords


if __name__ == "__main__":
    print(processing())
