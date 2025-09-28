import serial
import datetime


class Catsu:
    """
    Class for interacting with the Yaesu FT-991a
    with CAT control over serial
    """

    def __init__(self, *, port, baud):
        self.port = port
        self.baud = baud
        self.modes_dict = {
            "LSB": "1",
            "USB": "2",
            "CW-U": "3",
            "FM": "4",
            "AM": "5",
            "RTTY-LSB": "6",
            "CW-L": "7",
            "DATA-LSB": "8",
            "RTTY-USB": "9",
            "DATA-FM": "A",
            "FM-N": "B",
            "DATA-USB": "C",
            "AM-N": "D",
            "C4FM": "E",
        }

    def send_command(self, *, cmd):
        """
        Opens a serial port and sends a raw command/
        This should be of the format specified in the
        FT-991a CAT operating manual, consisting of
        an alphabetic command, a set of integers
        "the parameter" and the semicolon terminator.

        For example:
            FA014250000;

        Where FA is the command, corresponding to
        VFO A in this case, 014250000 is the parameter
        corresponding to 14.25MHz and ";" is the
        terminator.
        """
        assert cmd[-1] == ";", f"Missing terminator: {cmd}"

        with serial.Serial() as ser:
            ser.baudrate = self.baud
            ser.port = self.port
            ser.open()
            ser.write(cmd.encode("ascii"))

    def read_cmd(self, *, cmd=None):
        """
        Sends a read command to the transceiver

        Returns the result as a dictionary with
        the command and parameter as strings.
        """
        res = []

        with serial.Serial() as ser:
            ser.baudrate = self.baud
            ser.port = self.port
            ser.open()
            ser.write(cmd.encode("ascii"))

            ## read the buffer until we get
            ## a terminator character
            r = None
            while r != ";":
                r = ser.read().decode("ascii")
                res.append(r)

        res = "".join(res)
        res_command = res[:2]
        res_parameter = res[2:-1]

        return {"command": res_command, "parameter": res_parameter}

    def read_vfo_a(self):
        """
        Reads the frequency from VFO A, returns an integer
        """
        return self.read_vfo_frequency(vfo="A")

    def read_vfo_frequency(self, *, vfo=None):
        """
        Reads the frequency from VFO A or VFO B,
        returns an integer

        Parameters
        ----------
        vfo:
            "A" or "B" for VFO A or VFO B
        """
        cmd = None
        res = None

        if vfo == "A":
            cmd = "FA;"
        elif vfo == "B":
            cmd = "FB;"
        else:
            raise Exception(f"VFO {vfo} is not valid. Expected A or B")

        with serial.Serial() as ser:
            ser.baudrate = self.baud
            ser.port = self.port
            ser.open()
            ser.write(cmd.encode("ascii"))
            res = ser.read(12)

        return int(res.decode("ascii")[2:-1])

    def read_vfo_a(self):
        """
        Reads the frequency from VFO A, returns an integer
        """
        return self.read_vfo_frequency(vfo="A")

    def read_vfo_b(self):
        """
        Reads the frequency from VFO B, returns an integer
        """
        return self.read_vfo_frequency(vfo="B")

    def set_frequency_hz_vfo_a(self, setFreqHz: int):
        """
        Sets the frequency of VFO A

        Input is an integer in Hz
        """
        assert isinstance(setFreqHz, int)
        assert len(str(setFreqHz)) <= 9

        cmd = f"FA{str(setFreqHz).zfill(9)};"

        self.send_command(cmd=cmd)

    def set_frequency_hz_vfo_b(self, setFreqHz: int):
        """
        Sets the frequency of VFO B

        Input is an integer in Hz
        """
        assert isinstance(setFreqHz, int)
        assert len(str(setFreqHz)) <= 9

        cmd = f"FB{str(setFreqHz).zfill(9)};"

        self.send_command(cmd=cmd)

    def set_freq_human_readable_vfo_a(self, seqFreqStr: str):
        """
        Sets the frequency of VFO A

        Input is a string of one of the following formats:
            - "145.5M" corresponds to 145.5MHz
            - "14313K" corresponds to 14.313MHz
            - "7127000" corresponds to 7.127MHz
        """
        freq = None

        match seqFreqStr[-1]:
            case "K":
                freq = int(float(seqFreqStr[:-1]) * 1000)
            case "M":
                freq = int(float(seqFreqStr[:-1]) * 1000000)
            case _:
                freq = int(seqFreqStr)

        return self.set_frequency_hz_vfo_a(freq)

    def set_freq_human_readable_vfo_b(self, seqFreqStr: str):
        """
        Sets the frequency of VFO B

        Input is a string of one of the following formats:
            - "145.5M" corresponds to 145.5MHz
            - "14313K" corresponds to 14.313MHz
            - "7127000" corresponds to 7.127MHz
        """
        freq = None

        match seqFreqStr[-1]:
            case "K":
                freq = int(float(seqFreqStr[:-1]) * 1000)
            case "M":
                freq = int(float(seqFreqStr[:-1]) * 1000000)
            case _:
                freq = int(seqFreqStr)

        return self.set_frequency_hz_vfo_b(freq)

    def get_current_memory_channel(self):
        """
        Reads the current memory channel number
        """

        current_memory_channel = self.read_cmd(cmd="MC;")["parameter"]

        return int(current_memory_channel)

    def set_current_memory_channel(self, channelNumber: int):
        """
        Sets the current memory channel.

        001-117 are valid memory channel numbers
        001-099 are regular memory channels
        100: P-1L
        101: P-1U ~ 116: P-9L
        117: P-9U
        """
        assert isinstance(channelNumber, int)
        assert (channelNumber >= 1) and (channelNumber <= 117)

        return self.send_command(cmd=f"MC{str(channelNumber).zfill(3)};")

    def vfo_a_to_memory_channel(self):
        """
        Writes the current VFO A frequency to
        the current memory channel.
        """
        return self.send_command(cmd="AM;")

    def set_operating_mode(self, *, mode=None):
        """
        Something like set_operating_mode(mode="FM")
        """
        assert mode in self.modes_dict.keys()

        self.send_command(cmd=f"MD0{self.modes_dict[mode]};")

    def read_memory_channel(self, memoryChannel=None):
        """
        memoryChannel (int) 001-117

        Returns None if the memory channel hasn't
        been initialised
        """
        assert isinstance(memoryChannel, int)

        ## need to manually set it here
        ## because the read command doesn't seem to
        ## set it for wahtever reason
        self.set_current_memory_channel(memoryChannel)

        result = self.read_cmd(cmd=f"MR{str(memoryChannel).zfill(3)};")["parameter"]

        try:
            return_dict = {
                "memory_channel": result[0:3],  ## 001-117
                "vfo_a_frequency_hz": result[3:12],
                "clarifier_direction": result[12:17],  ## + or - and 0000-9999 (Hz)
                "rx_clar_status": result[17:18],  ## 0 off, 1 on
                "tx_clar_status": result[18:19],  ## 0 off, 1 on
                "mode": result[19:20],  ## for example, LSB or FM
                "vfo_or_memory": result[20:21],  ## 0 VFO, 1 memory
                "ctcss_dcs": result[
                    21:22
                ],  ## 0 CTCSS off, 1 CTCSS ENC/DEC, 2 CTCSS ENC, 3 DCS ENC/DEC, 4 DCS ENC
                "nothing": result[22:24],  ## always 00
                "simplex_or_plus_or_minus_shift": result[
                    24
                ],  ## 0 simplex, 1 plus shift, 2 minus shift
            }

            return return_dict
        except:
            None

    def set_display_colour(self, colour=None):
        display_colour_dict = {
            "BLUE": "0",
            "GRAY": "1",
            "GREEN": "2",
            "ORANGE": "3",
            "PURPLE": "4",
            "RED": "5",
            "SKY BLUE": "6",
        }

        self.send_command(cmd=f"EX006{display_colour_dict[colour]};")

    def read_date_and_time(self):
        """
        I'm not convinced this returns the current clock.
        
        I think it returns the time the clock was set to, and
        perhaps the difference from this is calculated internally.
        """
        return {
            "date": self.read_cmd(cmd="DT0;")["parameter"][1:],
            "time": self.read_cmd(cmd="DT1;")["parameter"][1:],
            "timezone": self.read_cmd(cmd="DT2;")["parameter"][1:],
        }

    def set_date_and_time(self):
        """
        Sets the date and time based on the current computer
        clock. Doesn't take any user input.
        
        Forces the clock to UTC-0
        """
        set_date = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d")
        set_time = datetime.datetime.now(datetime.timezone.utc).strftime("%H%M%S")

        self.send_command(cmd=f"DT0{set_date};")
        self.send_command(cmd=f"DT1{set_time};")
        self.send_command(cmd="DT2+0000;")

        return
