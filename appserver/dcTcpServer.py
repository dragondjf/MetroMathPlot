#!/usr/bin/python
# -*- coding: utf-8 -*-
import SocketServer
import socket
import ipkt
import struct
import algorithm


class ErrorPacket(Exception):
    pass


class ErrorConnect(Exception):
    pass


class ErrorConnectClose(Exception):
    pass


class ErrorHead(Exception):
    pass


class DCTcpServer(SocketServer.ThreadingTCPServer):

    def __init__(server_address, RequestHandlerClass):

        SocketServer.ThreadingTCPServer.__init__(server_address, RequestHandlerClass)

    def verify_request(self, request, client_address):
        return True


class DcHandler(SocketServer.BaseRequestHandler):

    HEAD_SIZE = 6

    def setup(self):
        self.data = algorithm.creat_data(algorithm.Names)

    def handle(self):
        while True:
            self.tcp_deal()

    def tcp_deal(self):

        """接收并处理一个完整的TCP应用层报文"""

        recv_head = None
        recv_body = None
        body_len = 0
        cid = 0

        try:
            #接收包头
            recv_head = ""  # zzh debug
            while len(recv_head) < self.HEAD_SIZE:
                recv_t = self.request.recv(self.HEAD_SIZE - len(recv_head))
                if not recv_t:
                    raise ErrorHead("can not recv head:" + str(recv_head))
                else:
                    recv_head = recv_head + recv_t
            if not recv_head or len(recv_head) == 0:
                raise ErrorConnectClose(self.client_address[0] + "connection is close.")

            elif len(recv_head) != DcHandler.HEAD_SIZE:
                # logger.info(repr(recv_head))
                # logger.info(len(recv_head))
                raise ErrorPacket("invalid head length.")
            else:
                body_len, cid = struct.unpack_from(">HB", recv_head)
                recv_body = ""

                if body_len > 4096:
                    raise ErrorConnect("recv head error:%d" % (body_len))
                elif body_len > 0:

                    #接收包体
                    while len(recv_body) < body_len:
                        recv_t = self.request.recv(body_len - len(recv_body))

                        if not recv_t:
                            raise ErrorConnect("can not recv body:" + str(recv_t))
                        else:
                            recv_body = recv_body + recv_t

                    #检查包完整性
                    if len(recv_body) != body_len:
                        raise ErrorConnect("recv body error! recv_len is %d" % len(recv_body))
                else:
                    recv_body = ""

            # 解析报文
            header, body = ipkt.unpack(recv_head + recv_body, ver=self.collector.dc.protocol_ver)

            self.pkt_handle(header, body)

        except socket.timeout:
            raise ErrorConnect("tcp timeout: " + str(self.client_address[0]))

        except ipkt.ErrorUnknownType, e:
            # logger.warn(e)
            print e

        return

    def pkt_handle(self, header, body):

        # if header.cmd == ipkt.GET_BASE_INFO_RSP:
        #     logger.info("recv packet from " + self.client_address[0] + ": " + repr((header, body)))
        #     self.collector.dc.mac = ":".join(["%02x" % ord(t) for t in body.mac])
        #     #self.collector.dc.protocol_ver = body.proto_version
        #     self.collector.dc.hw_version = "v" + ".".join(["%d" % ord(t) for t in body.hw_version])
        #     self.collector.dc.sw_version = "v" + ".".join(["%d" % ord(t) for t in body.sw_version]) + '-r' + str(body.sw_revision)
        #     if self.collector.dc.protocol_ver == 2:
        #         self.proto_mode = body.proto_mode
        #         self.ip_num = body.ip_num
        #         self.channel_num = body.channel_num
        #         self.collector.dc.slot_id = body.slot_id
        #         self.collector.dc.machine_id = body.machine_id
        if header.cmd == ipkt.NOTIFY_PREPARE_SIMPLING_DATA:
            # self.collector.sampling(header.channel, body.min, body.max, body.avg, body.variance,body.compression, body.data)
            self.data['max'][-1] = body.max
            self.data['min'][-1] = body.min

            for key in algorithm.Names:
                self.data[key][:-1] = self.data[key][1:]
        # elif header.cmd == ipkt.NOTIFY_RAW_DATA:
        #     FFT_SIZE = 1024
        #     data_size = len(body.data) / 2
        #     t_raw_data = list(struct.unpack_from('>' + 'H' * data_size, body.data))
        #     if len(self.raw_data[header.channel - 1]) + len(t_raw_data) >= FFT_SIZE:
        #         self.collector.raw_sampling(header.channel, self.raw_data[header.channel - 1] + t_raw_data)
        #         self.raw_data[header.channel - 1] = []
        #     else:
        #         self.raw_data[header.channel - 1] = t_raw_data

        #     self.wav_dump(header.channel, t_raw_data)

        # elif header.cmd == ipkt.NOTIFY_SYS_FAIL:
        #     logger.info("recv packet from " + self.client_address[0] + ": " + repr((header, body)))
        #     if header.ret == 0x04:
        #         self.collector.changeSystemStatus(collector.Collector.STATUS_LID_OPEN)
        # elif header.cmd == ipkt.NOTIFY_SYS_FAIL_RECOVERY:
        #     logger.info("recv packet from " + self.client_address[0] + ": " + repr((header, body)))
        #     if header.ret == 0x04:
        #         self.collector.changeSystemStatus(collector.Collector.STATUS_LID_CLOSE)
        # else:
        #     logger.warn("ignore packet from " + self.client_address[0] + ": " + repr((header, body)))
        #     pass

    def finish():
        pass
