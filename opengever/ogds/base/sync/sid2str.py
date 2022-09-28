import struct


def sid2str(sid):
    """Converts a binary sid to string representation"""
    if len(sid) < 8:
        return ''
    # The revision level (typically 1)
    revision = ord(sid[0])
    # The number of dashes minus 2
    number_of_sub_ids = ord(sid[1])
    # Identifier Authority Value
    # (typically a value of 5 representing "NT Authority")
    # ">Q" is the format string. ">" specifies that the bytes are big-endian.
    # The "Q" specifies "unsigned long long" because 8 bytes are being decoded.
    # Since the actual SID section being decoded is only 6 bytes, we must
    # precede it with 2 empty bytes.
    iav = struct.unpack('>Q', b'\x00\x00' + sid[2:8])[0]
    # The sub-ids include the Domain SID and the RID representing the object
    # '<I' is the format string. "<" specifies that the bytes are
    # little-endian. "I" specifies "unsigned int".
    # This decodes in 4 byte chunks starting from the 8th byte until the last
    # byte.
    if len(sid) - 8 < number_of_sub_ids * 4:
        return ''
    sub_ids = [struct.unpack('<I', sid[8 + 4 * i:12 + 4 * i])[0]
               for i in range(number_of_sub_ids)]
    return 'S-{0}-{1}-{2}'.format(
        revision, iav, '-'.join([str(sub_id) for sub_id in sub_ids]))
