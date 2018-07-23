import socket


class UDPClient:
    def __init__(self, remote_ip, remote_port, local_ip, local_port):
        self.address = (remote_ip, remote_port)
        self.recv_buffer_size = 20480
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((local_ip, local_port))

    def Send(self, message):
        self.sock.sendto(message, self.address)

    def Receive(self):
        data, addr = self.sock.recvfrom(self.recv_buffer_size)
        return data

class Message:
    def __init__(self, text):
        self.incomming = False
        self.is_request = False
        self.name = ""
        self.raw_body = text
        self.cseq = 0
        self.call_id = "0"
        self.to_name = ""
        self.to_number = ""
        self.to_domain = ""
        self.from_name = ""
        self.from_domain = ""
        self.from_number = ""
        self.contact = ""
        self.to_tag = ""
        self.from_tag = ""
        self.pai = ""
        self.sdp = ""
        self.local_port = 0
        self.remote_port = 0
        self.message_lines = []
        self.ParseText()
        #print(self.message_lines)

    def ParseText(self):
        line_body = self.raw_body.split("\n")
        line_index = 0
        field_name = ""
        for line in line_body:
            print("Line> ", line)
            if line != "":
                if line_index == 0: 
                    if line[0] == "<":
                        line = line[1:]
                        self.incomming = False
                    elif line[0] == ">":
                        line = line[1:]
                        self.incomming = True
                    elif line[0] != ">" or line[0] != "<":
                        self.incomming = True
                    self.ParseMethodName(line)
                else:
                    if line[0] == ">" or line[0] == "<":
                        line = line[1:]
                    field_name = self.GetFieldName(line)
                    self.ParseFieldInfo(field_name, line)
                #print(line)
                self.message_lines.append(line)
                line_index += 1
                
        return None

    def GetFormattedMessage(self):
        return bytes(("\r\n".join(self.message_lines) + "\r\n\r\n").format(**dictionar), "ascii")

    def ParseFieldInfo(self, field_name, line):
        #print("field_name = ", field_name)
        if field_name.lower() == "from:":
            self.from_tag = self.ParseTag(line)
            return None
        elif field_name.lower() == "to:":
            self.to_tag = self.ParseTag(line)
            return None
        elif field_name.lower() == "cseq:":
            return None
        elif field_name.lower() == "call-id:":
            return None
        elif field_name.lower() == "contact:":
            return None
        elif field_name.lower() == "p-asserted-identity:":
            return None
        elif field_name.lower() == "content-type:":
            return None
        elif field_name.lower() == "record-route:":
            return None
        elif field_name.lower() == "allow:":
            return None
        elif field_name.lower() == "supported: ":
            return None
        elif field_name.lower() == "user-agent: ":
            return None
        elif field_name.lower() == "max-forwards:":
            return None
        elif field_name.lower() == "via:":
            return None
        elif field_name.lower() == "accept-language:":
            return None
        elif field_name.lower() == "alert-info:":
            return None
        elif field_name.lower() == "session-expires:":
            return None
        elif field_name.lower() == "min-se:":
            return None
        elif field_name.lower() == "p-av-message-id:":
            return None
        elif field_name.lower() == "endpoint-view:":
            return None
        elif field_name.lower() == "p-charging-vector:":
            return None
        elif field_name.lower() == "av-global-session-id:":
            return None
        elif field_name.lower() == "p-location:":
            return None
        elif field_name.lower() == "content-length:":
            return None
        return None

    def GetFieldName(self, line):
        field_end = line.find(": ")
        if field_end != -1:
            return line[ 0 : field_end + 1]
        else:
            return ""

    def ParseTag(self, line):
        tag_start = line.find(";tag=")
        if tag_start != -1:
            tag_start += len(";tag=")
            tag_end = line.find(";", tag_start)
            if tag_end != -1:
                return line[ tag_start : tag_end ].strip()
            else:
                return (line[ tag_start : ]).strip()
        return None

    def ParseMethodName(self, line):
        fields = line.split(" ")
        if line.find("SIP/2.0") != -1 and line.find("SIP/2.0") == 0:
            self.is_request = True
            self.name = fields[1]
        else:
            self.is_request = False
            self.name = fields[0]

    def GetByteArray(self):
        return None

    def GetString(self):
        return None


class ScenarioReader:
    def __init__(self, filename):
        self.f_source = open(filename, "r")
        self.separator = "===================="

    def GetNextMessage(self):
        new_message = ""
        for line in self.f_source:
            #print("Line = ", line)
            if line.find(self.separator) != -1:
                    break
            else:
                new_message += line.strip() + "\n"
        return new_message


dictionar = {"local_ip":                    '192.168.42.140',
             "remote_ip":                   '192.168.42.23',
             "local_port":                  '5060',
             "remote_port":                 '5060',
             "branch":                      'z9hG4bK-1234',
             "call_id":                     '000001',
             "call_id_options":             '000001X',
             "service":                     '300',
             "domain":                      'sipp',
             "from_display_name":           '"Inna SIP"',
             "pai_display_name":            '"Inna SIP"',
             "from_number":                 '1234',
             "cseq":                        '1',
             "call_id":                     '666666',
             "contact2_display_name":       '"You are now con"',
             "contact2_number":             '9007',
             }

c = UDPClient(dictionar["remote_ip"], int(dictionar["remote_port"]), dictionar["local_ip"], int(dictionar["local_port"]))
mr = ScenarioReader("messages.txt")

new_message = mr.GetNextMessage()
m = Message(new_message)
#print(new_message)
response = None

while m.raw_body != "":
    message = m.GetFormattedMessage()
    #print(message)
    print("===========================================")
    if m.incomming == False:
        c.Send(message)
    else:
        response = c.Receive()
        #print(response.decode("utf-8"))
        recv_msg = Message(response.decode("utf-8"))
        #print("to_tag =", recv_msg.to_tag)
        dictionar["to_tag"] = recv_msg.to_tag
    print("===========================================")
    new_message = mr.GetNextMessage()
    m = Message(new_message)




