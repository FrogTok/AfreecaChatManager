from pydantic import BaseModel

class Broadcast(BaseModel):
    broad_no: int
    CHDOMAIN: str
    CHATNO: str
    FTK: str
    TITLE: str
    BJID: str
    CHPT: str


class Bj(BaseModel):
    id: str
    station_no: str
    user_id: str
    user_nick: str
    station_name: str
    station_title: str
    broad_start: str
    total_broad_time: str
    grade: str
    fan_cnt: str
    total_visit_cnt: str
    total_ok_cnt: str
    total_view_cnt: str
    today_visit_cnt: str
    today_ok_cnt: str
    today_fav_cnt: str
