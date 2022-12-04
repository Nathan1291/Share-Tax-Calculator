import pandas as pd
import os
import calculation.calculation as calculation
import record_processing.record_processing as record_processing

if __name__ == "__main__":
    # Checking if records file exists in recrods folder
    if not os.path.exists("records/records.csv"):
        print("Records file not found! Please place the csv file of transactions from commsec into the records folder under the name records.csv")

    else:
        FY = int(input("\n\nRecords file found! Please enter which financial year you would like to calculate on: "))
        buyRecords, sellRecords = record_processing()

        totalTaxableComponents = calculation(buyRecords, sellRecords, FY)

        CG_after_1Yr = totalTaxableComponents["CG > 1 Yr"]
        CG_before_1Yr = totalTaxableComponents["CG < 1 Yr"]
        CL = totalTaxableComponents["CL"]

        # calculate the final change in capital
        netCapitalChange = 0
        capitalLossTracker = CL

        # if the capital loss is fully exhausted on capital gains before 1 year
        if CG_before_1Yr > capitalLossTracker:
            netCapitalChange = round(CG_before_1Yr + CL + CG_after_1Yr * 0.5, 2)
        else:
            capitalLossTracker += CG_before_1Yr

            # if the capital loss is fully exhausted on capital gains after 1 year
            if CG_after_1Yr > capitalLossTracker:
                netCapitalChange = round((CG_after_1Yr + capitalLossTracker) * 0.5, 2)

            # if there is a net capital loss
            else:
                netCapitalChange = round(capitalLossTracker + CG_after_1Yr, 2)
                
        print("\nYour net capital change is:", round(netCapitalChange, 2))
        print("Your capital gains where the asset is held for more than a year (viable for CGT discount) is:", round(CG_after_1Yr, 2))
        print("Your capital gains where the asset is held less than a year is:", round(CG_before_1Yr, 2))
        print("Your viable capital loss is:", round(CL, 2))
