import struct

DEFAULT_MPS7_FILE = 'txnlog.dat'
MPS7_FILE_TYPE_HEADER = 'MPS7'
SPECIFIC_USER_ID = 2456938384156277127

MINIMUM_RECORD_SIZE_IN_BYTES = 13
FILE_TYPE_SIZE = 4
FILE_VERSION_SIZE = 1
NUMBER_OF_RECORDS_SIZE = 4

TYPE_ENUM_SIZE = 1
UNIX_TIMESTAMP_SIZE = 4
USER_ID_SIZE = 8
AMOUNT_IN_DOLLARS_SIZE = 8

RECORD_TYPES = {
    b'\x00': 'DEBIT',
    b'\x01': 'CREDIT',
    b'\x02': 'START_AUTOPAY',
    b'\x03': 'END_AUTOPAY'
}

ADDITIONAL_PARAMETER_RECORD_TYPES = ['DEBIT', 'CREDIT']


def parse_mps7(file_name=DEFAULT_MPS7_FILE):
    records = []

    with open(file_name, "rb") as binary_file:
        binary_file.seek(0)

        file_type = binary_file.read(FILE_TYPE_SIZE).decode('utf-8')

        if not file_type == MPS7_FILE_TYPE_HEADER:
            raise Exception('Invalid file type, does not have correct header')

        version = binary_file.read(FILE_VERSION_SIZE)
        number_of_records = int.from_bytes(
            binary_file.read(NUMBER_OF_RECORDS_SIZE),
            byteorder='big',
            signed=False)

        while len(records) < number_of_records:
            record_type = RECORD_TYPES[binary_file.read(TYPE_ENUM_SIZE)]
            unix_timestamp = int.from_bytes(
                binary_file.read(UNIX_TIMESTAMP_SIZE),
                byteorder='big',
                signed=False)
            user_id = int.from_bytes(
                binary_file.read(USER_ID_SIZE), byteorder='big', signed=False)
            amount = None

            if record_type in ADDITIONAL_PARAMETER_RECORD_TYPES:
                amount = struct.unpack(
                    '>d', binary_file.read(AMOUNT_IN_DOLLARS_SIZE))[0]

            records.append({
                'type': record_type,
                'timestamp': unix_timestamp,
                'user_id': user_id,
                'amount': amount
            })

    return records


def record_analysis(records):
    analysis_data = {
        'total_debits': 0,
        'total_credits': 0,
        'autopays_started': 0,
        'autopays_ended': 0,
        'specific_user_balance': 0
    }

    for record in records:
        if record['type'] == 'CREDIT':
            analysis_data['total_credits'] += record['amount']

            if record['user_id'] == SPECIFIC_USER_ID:
                analysis_data['specific_user_balance'] += record['amount']
        if record['type'] == 'DEBIT':
            analysis_data['total_debits'] += record['amount']

            if record['user_id'] == SPECIFIC_USER_ID:
                analysis_data['specific_user_balance'] -= record['amount']
        if record['type'] == 'START_AUTOPAY':
            analysis_data['autopays_started'] += 1
        if record['type'] == 'END_AUTOPAY':
            analysis_data['autopays_ended'] += 1

    return analysis_data


parsed_records = parse_mps7()
print(parsed_records)
print(len(parsed_records))
analysis_data = record_analysis(parsed_records)
print(analysis_data)