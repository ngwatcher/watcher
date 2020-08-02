import os
import glob
import pandas as pd

"""
Loops through records in data path & feed into Kusto
"""
def main():
    # get a list of all files in directory
    datasources = [f for f in glob.glob(os.getcwd() + "/data/*.xlsx")]

    for sourcepath in datasources:
        # open the xlsx file with pandas
        singlesource_df = pd.read_excel( sourcepath )

        # TODO: this has to be a method that manages parsing xlsx
        # we need to loop through the source file to only get valid content
        for i in range(len(singlesource_df.index)):
            if not is_header(singlesource_df.iloc[i]):
                continue
            else:
                print("Header found with index" + str(i))
                # get the index
                # trim the data frame for data with content 
                valid_content = singlesource_df.iloc[i+1:, :5]
                print(valid_content)

                # feed data with timestamp "from name" into kusto store
                # TODO: build kusto client, define schema too a bit & write to it
                # TODO: call the client with data

                break

"""
Checks if the string is a candidate for a payment entry header 

Payment record headers
Payment No, Payer Code, Organization Name, Beneficiary Name, Amount, Description

TODO: this function can be updated to match other record types
"""
def is_header( entry ):
    print("Evaluating entry")
    print(entry)
    if ( (str(entry[0]).upper().find("PAYMENT") != -1) and
        (str(entry[1]).upper().find("PAYER") != -1) and
        (str(entry[2]).upper().find("ORGANIZATION") != -1) and
        (str(entry[3]).upper().find("BENEFICIARY") != -1) and
        (str(entry[4]).upper().find("AMOUNT") != -1) and
        (str(entry[5]).upper().find("DESCRIPTION") != -1) ):
        return True
    else:
        return False
        
if __name__ == "__main__":
    main()