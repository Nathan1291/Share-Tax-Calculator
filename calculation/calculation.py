import pandas as pd
from calculation.calculate_tax import calculate_tax

# Takes the records of purchase and sale trasnactions as well as the financial year to calculate on as the parameters
def calculation(buyRecords, sellRecords, FY):
    # Finding the share sales that have occured in the desired financial year to calculate on
    FYSellRecords = pd.DataFrame(columns=["Date","Share", "Price","Units", "Brokerage Fee"])
    for i in range(len(sellRecords)):
        [day, month, year] = list(map(int, sellRecords.iloc[i]["Date"].split("/")))
        # Check if transaction is in the desired financial year
        if year == FY and month < 7 or year == (FY - 1) and month > 6:
            FYSellRecords = pd.concat([FYSellRecords, pd.DataFrame([sellRecords.iloc[i]])], ignore_index=True)

    # Extract the specific shares that were sold in the desired financial year to a set
    FYShares = set()
    for name in FYSellRecords["Share"]:
        FYShares.add(name)

    # Prepare variables for the separate tax components depending on how long they were held
    totalTaxableComponents = {"CG > 1 Yr": 0,"CG < 1 Yr": 0, "CL": 0}


    # Going through each share sold in
    for share in FYShares:
        # Getting all buy and sell records associated with the given share
        FYBuyRecords = pd.DataFrame(columns=["Date","Share", "Price","Units", "Brokerage Fee"])

        for i in range(len(buyRecords)):
            if buyRecords.iloc[i]["Share"] == share:
                FYBuyRecords = pd.concat([FYBuyRecords, pd.DataFrame([buyRecords.iloc[i]])], ignore_index=True)

        FYSellRecords = pd.DataFrame(columns=["Date","Share", "Price","Units", "Brokerage Fee"])

        for i in range(len(sellRecords)):
            if sellRecords.iloc[i]["Share"] == share:
                FYSellRecords = pd.concat([FYSellRecords, pd.DataFrame([sellRecords.iloc[i]])], ignore_index=True)

        taxableComponents = calculate_tax(FYBuyRecords, FYSellRecords, FY)

        totalTaxableComponents["CG > 1 Yr"] += taxableComponents["CG > 1 Yr"]
        totalTaxableComponents["CG < 1 Yr"] += taxableComponents["CG < 1 Yr"]
        totalTaxableComponents["CL"] += taxableComponents["CL"]

    return totalTaxableComponents





if __name__ == "__main__":
    buyRecords = pd.read_pickle("buyRecords.pkl")
    sellRecords = pd.read_pickle("sellRecords.pkl")
    calculation(buyRecords, sellRecords, 2021)
