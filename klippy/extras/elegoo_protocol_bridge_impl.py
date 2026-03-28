import json
import struct

# CRC16 Calculation
# Reference: https://en.wikipedia.org/wiki/Cyclic_redundancy_check#Calculating_the_checksum

def crc16(data: bytes) -> int:
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1
    return crc

# Variable Length Quantity (VLQ) Encoder/Decoder

def encode_vlq(value: int) -> bytes:
    if value < 0:
        raise ValueError("Value must be non-negative")
    bytes_list = []
    while True:
        byte = value & 0x7F
        value >>= 7
        if value:
            bytes_list.append(byte | 0x80)
        else:
            bytes_list.append(byte)
        if not value:
            break
    return bytes(bytes_list)

def decode_vlq(data: bytes) -> int:
    value = 0
    for byte in data:
        value = (value << 7) | (byte & 0x7F)
        if not (byte & 0x80):
            return value
    raise ValueError("Invalid VLQ data")

# JSON-RPC to Binary Protocol Conversion

def json_rpc_to_binary(json_rpc: dict) -> bytes:
    method = json_rpc.get('method')
    params = json_rpc.get('params', [])
    # Encode method name size and params
    method_bytes = method.encode('utf-8')
    params_bytes = encode_vlq(len(params)) + b''.join(param.encode('utf-8') for param in params)
    message = struct.pack('>H', len(method_bytes)) + method_bytes + params_bytes
    # Add CRC16
    crc = crc16(message)
    return message + struct.pack('>H', crc)

# Example usage
if __name__ == '__main__':
    # Sample JSON-RPC
    json_rpc_request = {'method': 'example_method', 'params': ['param1', 'param2']}
    binary_data = json_rpc_to_binary(json_rpc_request)
    print(binary_data)