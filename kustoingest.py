import os
import glob
import re
import pprint
from datetime import datetime, timezone
import pandas as pd
from azure.kusto.data import KustoConnectionStringBuilder
from azure.kusto.ingest import (
    KustoIngestClient,
    IngestionProperties,
    FileDescriptor,
    BlobDescriptor,
    StreamDescriptor,
    DataFormat,
    ReportLevel,
    IngestionMappingType,
    KustoStreamingIngestClient,
)
from azure.kusto.ingest.status import KustoIngestStatusQueues

################################################################
# Initialize Kusto Ingest Client
################################################################
client_id = "<REGISTERED_APP_CLIENT_ID>"
client_secret = "<REGISTERED_APP_CLIENT_SECRET>"
cluster = "<KUSTO_CLUSTER_INGEST_URL>"
authority_id = "<REGISTERED_APP_TENANT_ID>"

kcsb = KustoConnectionStringBuilder.with_aad_application_key_authentication(
    cluster, client_id, client_secret, authority_id)
kusto_ingest_client = KustoIngestClient(kcsb)
kusto_status_queue = KustoIngestStatusQueues(kusto_ingest_client)


def main():
    """
    Loops through records in data path & feed into Kusto
    """
    # get a list of all files in directory
    datasources = [f for f in glob.glob(os.getcwd() + "/data/*.xlsx")]

    with open("parse_failures.log", "w+") as parse_failure:
        for sourcepath in datasources:
            # open the xlsx file with pandas
            singlesource_df = pd.read_excel(sourcepath)

            # get the date which is a part of the filename
            sourcepath_suffix = re.findall(r'[\d-]+.xlsx', sourcepath)
            entry_day = re.sub('.xlsx', '', sourcepath_suffix[0])

            # find valid entries in source
            valid_entries = None
            for i in range(len(singlesource_df.index)):
                if not is_header(singlesource_df.iloc[i]):
                    continue
                else:
                    # trim the data frame for data with content
                    valid_entries = singlesource_df.iloc[i+1:, :6]
                    break

            if not isinstance(valid_entries, pd.DataFrame):
                error_message = f"Source data for {entry_day} is invalid - Could not find headers"
                parse_failure.write(error_message)
                print(error_message)
                print("Continuing to the new candidate source entry")
                continue

            print(f"Source data for {entry_day} is valid")
            # add headers that match with destination kusto table
            valid_entries.columns = ['PaymentNo', 'PayerCode',
                                    'OrganizationName', 'BeneficiaryName', 'Amount', 'Description']
            # add Timestamp, Source & IngestTimestamp to dataframe
            valid_entries['Timestamp'] = datetime.strptime(
                entry_day, "%m-%d-%y").isoformat()
            valid_entries['Source'] = 'FGN'
            valid_entries['IngestTimestamp'] = datetime.now(
                timezone.utc).isoformat()

            # print(f"Saving pre-processed data for {entry_day} csv data")
            # csvpath = os.getcwd() + "/data/" + entry_day + ".csv"
            # valid_entries.to_csv(csvpath, index=False)

            print(f"Pre-processed data for {entry_day} to kusto")
            feed_into_kusto(valid_entries)

            print(f"Write to Kusto for {entry_day} complete, going to next source")


def is_header(entry):
    """
    Checks if the string is a candidate for a payment entry header 
    TODO: this function can be updated to match other record types

    Payment record headers
    Payment No, Payer Code, Organization Name, Beneficiary Name, Amount, Description
    """
    if ((str(entry[0]).upper().find("PAYMENT") != -1) and
        (str(entry[1]).upper().find("PAYER") != -1) and
        (str(entry[2]).upper().find("ORGANIZATION") != -1) and
        (str(entry[3]).upper().find("BENEFICIARY") != -1) and
        (str(entry[4]).upper().find("AMOUNT") != -1) and
            (str(entry[5]).upper().find("DESCRIPTION") != -1)):
        return True
    else:
        return False


def feed_into_kusto(df):
    """
    Writes entry into Kusto database
    """
    ingestion_props = IngestionProperties(
        database="ngwatcher",
        table="Payments",
        data_format=DataFormat.CSV,
        reportLevel=ReportLevel.FailuresAndSuccesses,
    )

    kusto_ingest_client.ingest_from_dataframe(
        df, ingestion_properties=ingestion_props)

    # success_messages = kusto_status_queue.success.pop(10)
    # failure_messages = kusto_status_queue.failure.pop(10)

    # pprint.pprint("SUCCESS : {}".format(success_messages))
    # pprint.pprint("FAILURE : {}".format(failure_messages))


if __name__ == "__main__":
    main()
