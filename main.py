import serial


class Catsu:
    """
    Class for interacting with the Yaesu FT-991a
    with CAT control over serial
    """

    def __init__(self, *, port, baud):
        self.port = port
        self.baud = baud

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
        with serial.Serial() as ser:
            ser.baudrate = self.baud
            ser.port = self.port
            ser.open()
            ser.write(cmd.encode("ascii"))

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

    def set_frequency_hz_vfo_a(self, setFreqHz):
        """
        Sets the frequency of VFO A

        Input is an integer in Hz
        """
        assert isinstance(setFreqHz, int)
        assert len(str(setFreqHz)) <= 9

        cmd = f"FA{str(setFreqHz).zfill(9)};"

        self.send_command(cmd=cmd)

    def set_frequency_hz_vfo_b(self, setFreqHz):
        """
        Sets the frequency of VFO B

        Input is an integer in Hz
        """
        assert isinstance(setFreqHz, int)
        assert len(str(setFreqHz)) <= 9

        cmd = f"FB{str(setFreqHz).zfill(9)};"

        self.send_command(cmd=cmd)

    def set_freq_human_readable_vfo_a(self, seqFreqStr):
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

    def set_freq_human_readable_vfo_b(self, seqFreqStr):
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
