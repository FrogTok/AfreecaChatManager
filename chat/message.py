import threading
import certifi
import ssl
import websockets
import time
import asyncio
from chat.constants import (
    CHAT_MESSAGE,
    ENTRY_AND_EXIT_MESSAGE,
    ESC,
    F,
    JOIN_THE_PAN_CLUB_MESSAGE,
    POONG_MESSAGE,
    SUBSCRIBE_PERIOD_MESSAGE,
)
from chat.requests import get_bno, get_player_live
from chat.queue import ChatQueue, MemberChatQueue
from dto import Bj, Broadcast
SEPARATOR = "+" + "-" * 70 + "+"


class MessageThread(threading.Thread):
    def __init__(self, bj: Bj, broadcast: Broadcast):
        super().__init__()
        self.bj = bj
        self.broadcast = broadcast
        self.chat_queue = ChatQueue()
        self.member_chat_queue = MemberChatQueue()
        self.stop_event = threading.Event()
        self.ssl_context = self.create_ssl_context()
        self.loop = asyncio.new_event_loop()
        self.websocket = None
        self.ping_task = None
        self.receive_task = None

    def run(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.connect_to_chat())

    def stop(self):
        self.stop_event.set()
        self.loop.call_soon_threadsafe(self.loop.create_task, self.wait_for_tasks())

    async def wait_for_tasks(self):
        tasks = [self.ping_task, self.receive_task]
        await asyncio.wait(tasks)

    def create_ssl_context(self):
        ssl_context = ssl.create_default_context()
        ssl_context.load_verify_locations(certifi.where())
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        return ssl_context

    # 메시지 디코드 및 출력
    def decode_message(self, bytes):
        parts = bytes.split(b"\x0c")
        messages = [part.decode("utf-8") for part in parts]
        print(messages)
        if messages[0].find(CHAT_MESSAGE) != -1:
            # 매니저 구독 33개월
            # ['\x1b\t000500007500', 'ㅋㅋㅋㅋㅋ', 'a0516z', '0', '0', '3', '개굴톡', '806961504|1081344', '33', 'C40F70', 'C279A1', '']

            # ['\x1b\t000500010000', 'ㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋ', 'borammylove', '0', '0', '3', '지금현재', '720928|163840', '-1', '0B6D82', '6CABCF', '']
            # ['\x1b\t000500011100', '이 속도면 무역섬 털 수 있겠는데?', 'wlaqhf3944', '0', '0', '3', '춘배의모험', '589856|163840', '-1', '0B6D82', '6CABCF', '']

            # ['\x1b\t000500007900', '낚시보단 낫네', 'popcard1203', '0', '0', '3', '삭붐', '536952832|32768', '-1', '047143', '45A48D', '']
            # ['\x1b\t000500007100', '리겜같넼ㅋㅋ', 'nsaebin', '0', '0', '3', '빼꼼_', '82432|32768', '-1', '0C61E1', '5C82E3', '']
            # ['\x1b\t000500008900', '크레이지갈치구이정식', 'nill225(2)', '0', '0', '3', '느루임', '65536|163840', '-1', '6518C8', '9568CD', '']
            # ['\x1b\t000500007000', '크갈', 'qlsths2000', '0', '0', '3', 'SINACHANDETH', '65536|33718272', '-1', 'A90A0A', 'CD5D5D', '']
            # ['\x1b\t000500007700', '우편함 볼까', 'kjeongwoomon', '0', '0', '3', '신살성', '65536|163840', '-1', '158304', '63B566', '']
            # ['\x1b\t000500009100', 'ㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋ', 'kjeongwoomon', '0', '0', '3', '신살성', '65536|163840', '-1', '158304', '63B566', '']
            # ['\x1b\t000500007300', 'ㅁㅇㅁㅇ', 'kjeongwoomon', '0', '0', '3', '신살성', '65536|163840', '-1', '158304', '63B566', '']
            # message[1]이 채팅, message[2]가 아이디, message[6]이 닉네임, message[8]이 구독 개월수
            user_id, comment, user_nickname = messages[2], messages[1], messages[6]
            self.chat_queue.enqueue_message(f"{user_nickname}[{user_id}] - {comment}")
        elif messages[0].find(ENTRY_AND_EXIT_MESSAGE) != -1 and messages[1] == "1":
            # 입장
            pass
        elif messages[0].find(ENTRY_AND_EXIT_MESSAGE) != -1 and messages[1] == "-1":
            # ['\x1b\t000400004100', '-1', 'kywuni', 'Snowpiano', '2', '1', '606208|33554432', ''] 강퇴
            # ['\x1b\t000400004200', '-1', 'ekdms0405', '널징', '1', '-1', '606752|33554432', ''] 일반 퇴장
            # 퇴장 message[2]는 아이디, message[3]은 닉네임
            pass
        elif messages[0].find(SUBSCRIBE_PERIOD_MESSAGE) != -1:
            # message[1]이 닉네임, message[2]에 'fw=1'이런식으로 구독 개월수 나옴. 'fw=-1'이면 건빵
            pass
        elif messages[0].find(POONG_MESSAGE) != -1:
            # ['\x1b\t001800005700', '243000', 'a0516z', '개굴톡', '50', '0', '0', '1323', '50', '0', '0', 'kor_custom09', '']
            # ['\x1b\t001800005500', '243000', 'kjnu508', '모시모시깽_', '100', '0', '0', '1323', '100', '0', '0', '', '']
            # ['\x1b\t001800007000', '243000', 'kddingjune', '이탈리안BMT', '30', '4529', '0', '1323', '30', '0', '0', 'kor_custom07', '']
            # ['\x1b\t001800005300', '243000', 'baesoun1010', '대롱머롱', '50', '0', '0', '1323', '50', '0', '0', '', '']
            # ['\x1b\t001800004500', '243000', 'nwsw00251', 'DOFKG', '1', '4531', '0', '1323', '1', '0', '0', '', '']
            # ['\x1b\t001800005800', '243000', 'gydls7284', '송도동얼짱', '1000', '0', '0', '1323', '1000', '0', '0', '', '']
            # message[1] 받는 방송인 아이디
            # message[2] 풍쏜사람 아이디
            # message[3] 쏜사람 닉네임
            # message[4] 풍갯수
            # message[5] 처음 풍쏘면 몇번째 팬클럽 가입인지
            # message[7] CHATNO
            # message[8] 풍갯수
            # message[11]이 풍그림 파일명같은건가?
            pass
        elif messages[0].find(JOIN_THE_PAN_CLUB_MESSAGE) != -1:
            # ['\x1b\t001200006400', '537477152|32768', 'kddingjune', '이탈리안BMT', '0', '0', '537477120|32768', '']
            # ['\x1b\t001200004900', '589856|163840', 'nwsw00251', 'DOFKG', '0', '0', '589824|163840', '']
            # ['\x1b\t001200005400', '720928|33718272', 'ropen9772', '롤펭', '0', '0', '589856|33718272', '']
            pass
        else:
            # 채팅 뿐만 아니라 다른 메세지도 동시에 내려옵니다.
            pass

    def calculate_byte_size(self, string):
        return len(string.encode("utf-8")) + 6

    async def connect_to_chat(self):
        try:
            CHDOMAIN, CHATNO, FTK, TITLE, BJID, CHPT = get_player_live(self.broadcast.broad_no, self.bj.id)
            print(
                f"{SEPARATOR}\n"
                f"  CHDOMAIN: {CHDOMAIN}\n  CHATNO: {CHATNO}\n  FTK: {FTK}\n"
                f"  TITLE: {TITLE}\n  BJID: {BJID}\n  CHPT: {CHPT}\n"
                f"{SEPARATOR}"
            )
            self.chat_queue.enqueue_message(
                f"{SEPARATOR}\n"
                f"  CHDOMAIN: {CHDOMAIN}\n  CHATNO: {CHATNO}\n  FTK: {FTK}\n"
                f"  TITLE: {TITLE}\n  BJID: {BJID}\n  CHPT: {CHPT}\n"
                f"{SEPARATOR}"
            )
        except Exception as e:
            self.chat_queue.enqueue_message(f"  ERROR: API 호출 실패 - {e}")
            print(f"  ERROR: API 호출 실패 - {e}")
            return

        uri = f"wss://{CHDOMAIN}:{CHPT}/Websocket/{self.bid}"

        CONNECT_PACKET = f"{ESC}000100000600{F*3}16{F}"
        JOIN_PACKET = f"{ESC}0002{self.calculate_byte_size(CHATNO):06}00{F}{CHATNO}{F*5}"
        PING_PACKET = f"{ESC}000000000100{F}"
        try:
            self.websocket = await websockets.connect(
                uri,
                subprotocols=["chat"],
                ssl=self.ssl_context,
                ping_interval=None,
            )
            await self.websocket.send(CONNECT_PACKET)
            self.chat_queue.enqueue_message("  연결 성공, 채팅방 정보 수신 대기중...")
            print("  연결 성공, 채팅방 정보 수신 대기중...")
            await asyncio.sleep(2)
            await self.websocket.send(JOIN_PACKET)

            async def ping():
                while not self.stop_event.is_set():
                    try:
                        await asyncio.sleep(60)  # 1분 = 60초
                        await self.websocket.send(PING_PACKET)
                    except Exception as e:
                        self.chat_queue.enqueue_message(f"  ERROR: ping() error - {e}")
                        print(f"  ERROR: ping() error - {e}")
                        break

            async def receive_messages():
                while not self.stop_event.is_set():
                    try:
                        data = await self.websocket.recv()
                        self.decode_message(data)
                    except Exception as e:
                        self.chat_queue.enqueue_message(f"  ERROR: receive_messages() error - {e}")
                        print(f"  ERROR: receive_messages() error - {e}")
                        break

            self.ping_task = asyncio.create_task(ping())
            self.receive_task = asyncio.create_task(receive_messages())

            done, pending = await asyncio.wait([self.ping_task, self.receive_task], return_when=asyncio.FIRST_COMPLETED)

            for task in pending:
                task.cancel()

            await asyncio.gather(*pending, return_exceptions=True)
            await self.websocket.close(reason="Client shutdown")
            print("  INFO: 웹소켓 연결이 종료됐습니다.")
        except RuntimeError as e:
            self.chat_queue.enqueue_message(f"  ERROR: 웹소켓 런타임 오류 - {e}")
            print(f"  ERROR: 웹소켓 런타임 오류 - {e}")
            return

if __name__ == "__main__":
    bid = "243000"
    bno = get_bno(bid)
    websocket_thread = MessageThread(bid=bid, bno=bno)
    websocket_thread.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        websocket_thread.stop()
        websocket_thread.join()