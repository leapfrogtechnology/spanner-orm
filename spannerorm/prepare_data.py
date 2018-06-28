from google.cloud import spanner


class PrepareData:
    def __init__(self, table_name):
        self.table_name = str(table_name)

    def get_data(self):
        # Todo
        # ('id', 'name', 'address', 'points', 'is_active', 'join_date', 'modified_at')
        data = [
            ('148fb5b0-c562-4292-904c-b773486dae6a', 'Sabina Maharjan', 'Satungal', 150, True, '2018-01-20',
             spanner.COMMIT_TIMESTAMP),
            ('f10a7b7d-8849-4d5b-ae3f-7fce2a68e6a2', 'Pradeep Shrestha', 'kalimati', 500, False, '2018-01-25',
             spanner.COMMIT_TIMESTAMP),
            ('abebf825-cb7e-47e4-a193-a678d2c8718a', 'Rasna Shakya', 'kalanki, Kathmandu', 200, True, '2018-01-25',
             spanner.COMMIT_TIMESTAMP),
            ('8921e454-7161-44af-9b8b-1b84f81a22bc', 'Dinesh Thapa', 'kathmandu', 150, True, '2018-02-20',
             spanner.COMMIT_TIMESTAMP),
            ('d0415371-2c8b-4a16-b7ae-a3146c218525', 'Sonny Tv', 'Airport', 225, True, '2018-02-20',
             spanner.COMMIT_TIMESTAMP)
        ]
        return data
