"""
Borrowed from
https://forum.digikey.com/t/getting-started-with-the-ti-awr1642-mmwave-sensor/13445

Using this to establish the general structure of the Packets received from the mmWave radar chip
"""

# TODO: Need to verify if this is actually how the packets end up
import struct


class FrameError(Exception):
    def __init__(self, value):
        self.value = value


class TLVData:
    def __init__(self, serial_tlv):
        pass

    @staticmethod
    def preparsing(serial_tlv):
        # Only used if there is extra data in a frame outside of the regular objects
        return None, serial_tlv

    def __str__(self):
        result = ''
        for key in self.__dict__.keys():
            result += '{}: {}\n'.format(key, self.__dict__[key])
        return result


class DataObjDescriptor:
    def __init__(self, serial_tlv):
        elements = struct.unpack('<2h', serial_tlv)
        self.numDetectedObj = elements[0]
        self.xyzQFormat = elements[1]


class DetectedPoints(TLVData):
    NAME = 'DETECTED_POINTS'
    SIZE_BYTES = 16

    def __init__(self, serial_tlv):
        super(DetectedPoints, self).__init__(serial_tlv)
        # Unpack elements from the structure
        elements = struct.unpack('<ffff', serial_tlv)
        self.x = elements[0]
        self.y = elements[1]
        self.z = elements[2]
        self.doppler = elements[3]


class RangeProfile(TLVData):
    NAME = 'RANGE_PROFILE'
    SIZE_BYTES = 2

    def __init__(self, serial_tlv):
        super(RangeProfile, self).__init__(serial_tlv)
        # Unpack elements from the struct

        elements = struct.unpack('<H', serial_tlv)
        # self.

    pass


class NoiseFloorProfile(TLVData):
    NAME = 'NOISE_PROFILE'
    SIZE_BYTES = 2
    pass


class AzimuthStaticHeatmap(TLVData):
    NAME = 'AZIMUTH_HEATMAP'
    SIZE_BYTES = 4
    pass


class RangeDopplerHeatmap(TLVData):
    NAME = 'RANGE_HEATMAP'
    SIZE_BYTES = 4
    pass


class Stats(TLVData):
    NAME = 'MODULE_STATS'
    SIZE_BYTES = 24

    def __init__(self, serial_tlv):
        super(Stats, self).__init__(serial_tlv)
        # Unpack elements from the struct
        elements = struct.unpack('<iiii', serial_tlv)
        self.frame_time = elements[0]
        self.output_time = elements[1]
        self.inter_frame_margin = elements[2]
        self.inter_chirp_margin = elements[3]
        self.active_cpu_load = elements[4]
        self.inter_frame_cpu_load = elements[5]
    pass


class DetectedPointsSide(TLVData):
    NAME = 'SIDE_INFO_FOR_POINTS'
    SIZE_BYTES = 4

    def __init__(self, serial_tlv):
        super(DetectedPointsSide, self).__init__(serial_tlv)
        # Unpack elements from the struct
        elements = struct.unpack('<HH', serial_tlv)
        self.snr = elements[0]
        self.noise = elements[1]
    pass


class AzimuthElevationHeatmap(TLVData):
    NAME = 'AZIMUTH_ELEVATION_HEATMAP'
    SIZE_BYTES = 4
    pass


class TemperatureStats(TLVData):
    NAME = 'TEMPERATURE_STATS'
    SIZE_BYTES = 28
    pass


TLV_TYPES = {
    # Map type ID to the corresponding class
    1: DetectedPoints,
    2: RangeProfile,
    3: NoiseFloorProfile,
    4: AzimuthStaticHeatmap,
    5: RangeDopplerHeatmap,
    6: Stats,
    7: DetectedPointsSide,
    8: AzimuthElevationHeatmap,
    9: TemperatureStats,
}


class TLVHeader:
    SIZE_BYTES = 8

    def __init__(self, serial_tlv_header):
        elements = struct.unpack('<2I', serial_tlv_header)
        self.type = elements[0]
        self.length = elements[1]

    def __str__(self):
        result = 'TLV Header:\n'
        for key in self.__dict__.keys():
            result += '{}: {}\n'.format(key, self.__dict__[key])
        return result


class TLV:
    def __init__(self, serial_tlv):
        self.header = TLVHeader(serial_tlv[0:TLVHeader.SIZE_BYTES])

        # Lookup constructor for the specific type of object
        self.obj_class = TLV_TYPES[self.header.type]
        self.name = self.obj_class.NAME
        # Note this size is PER OBJECT
        self.obj_size = self.obj_class.SIZE_BYTES

        # Strip off excess headers before parsing objects
        headerless_tlv = serial_tlv[TLVHeader.SIZE_BYTES:]
        self.descriptor, processed_tlv = self.obj_class.preparsing(headerless_tlv)
        try:
            self.objects = self.parse_objects(processed_tlv)
        except struct.error as e:
            # Save whole frame from failing if one TLV is bad
            print('Exception while parsing TLV objects: ', e)
            self.objects = []

    def __str__(self):
        result = str(self.header) + 'Name: {}\n'.format(self.name)
        for each in self.objects:
            result += str(each)
        return result

    def parse_objects(self, serial_tlv):
        objects = []
        num_objects = int(self.header.length / self.obj_size)
        for i in range(0, num_objects):
            new = self.obj_class(serial_tlv[0:self.obj_size])
            objects.append(new)
            serial_tlv = serial_tlv[self.obj_size:]

        return objects


class FrameHeader:
    def __init__(self, serial_header):
        self.full_header = serial_header

    def __str__(self):
        result = 'Frame Header:\n'
        for key in self.__dict__.keys():
            result += '{}: {}\n'.format(key, self.__dict__[key])

        return result

    def verify_checksum(self):
        pass


class ShortRangeRadarFrameHeader(FrameHeader):
    SIZE_BYTES = 40
    PACKET_LENGTH_END = 16

    def __init__(self, serial_header):
        super().__init__(serial_header)
        self.sync = serial_header[0:8]
        self.version = serial_header[8:12]
        self.packetLength = struct.unpack('<I', serial_header[12:16])[0]
        self.platform = serial_header[16:20]

        values = struct.unpack('<5I', serial_header[20:40])
        self.frameNumber = values[0]
        self.timeCpuCycles = values[1]
        self.numDetectedObj = values[2]
        self.numTLVs = values[3]
        self.subFrameNumber = values[4]


class Frame:
    FRAME_START = b'\x02\x01\x04\x03\x06\x05\x08\x07'

    def __init__(self, serial_frame, frame_type):
        # Parse serial data into header and TLVs
        # Note that frames are LITTLE ENDIAN

        # Length should be > header_size
        frame_length = len(serial_frame)
        if frame_length < frame_type.SIZE_BYTES:
            raise FrameError('Frame is smaller than required header size. '
                             'Expected length {}. Measured length {}.'.format(frame_type.SIZE_BYTES, frame_length))

        # Initialize the header
        self.header = frame_type(serial_frame[0:frame_type.SIZE_BYTES])

        # Second sanity check
        if frame_length < self.header.packetLength:
            raise FrameError('Frame is too small. Expected {} bytes, '
                             'receieved {} bytes.'.format(self.header.packetLength, frame_length))

        # Convert remaining data into TLVs
        full_tlv_data = serial_frame[frame_type.SIZE_BYTES:]
        tlv_data = full_tlv_data
        self.tlvs = []
        for i in range(self.header.numTLVs):
            # Check header to get length of each TLV
            length = TLVHeader.SIZE_BYTES + TLVHeader(tlv_data[0:TLVHeader.SIZE_BYTES]).length
            # Create a 'length' bytes TLV instance
            new_tlv = TLV(tlv_data[0:length])
            self.tlvs.append(new_tlv)

            # Slice off the consumed TLV data
            tlv_data = tlv_data[length:]

    def __str__(self):
        # Print header followed by TLVs
        result = "START FRAME\n"
        result += str(self.header)
        result += 'TLVs: {\n'
        for each in self.tlvs:
            result += str(each)
        result += '}\n'
        result += 'END FRAME\n'
        return result
