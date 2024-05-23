USERLEVEL_FRONT = {
    "ADMIN": 1,
    "HIDDEN": 2,
    "BJ": 4,
    "DUMB": 8,
    "GUEST": 16,
    "FANCLUB": 32,
    "AUTOMANAGER": 64,
    "MANAGERLIST": 128,
    "MANAGER": 256,
    "FEMALE": 512,
    "AUTODUMB": 1024,
    "DUMB_BLIND": 2048,
    "DOBAE_BLIND": 4096,
    "DOBAE_BLIND2": 16777216,  # 1 << 24
    "EXITUSER": 8192,
    "MOBILE": 16384,
    "TOPFAN": 32768,
    "REALNAME": 65536,
    "NODIRECT": 131072,  # 1 << 17
    "GLOBAL_APP": 262144,  # 1 << 18
    "QUICKVIEW": 524288,  # 1 << 19
    "SPTR_STICKER": 1048576,  # 1 << 20
    "CHROMECAST": 2097152,  # 1 << 21
    "FOLLOWER": 268435456,  # 1 << 28
    "NOTIVODBALLOON": 1073741824,  # 1 << 30
    "NOTITOPFAN": -2147483648,  # 1 << 31 (negative value indicates signed 32-bit integer wrap-around)
}

USERLEVEL_BACK = {
    "GLOBAL_PC": 1,
    "CLAN": 2,
    "TOPCLAN": 4,
    "TOP20": 8,
    "GAMEGOD": 16,
    "GAMEIMO": 32,
    "NOSUPERCHAT": 64,
    "NORECVCHAT": 128,
    "FLASH": 256,
    "CLEANATI": 2048,
    "POLICE": 4096,
    "ADMINCHAT": 8192,
    "PC": 16384,
    "SPECIFY": 32768,  # 1 << 15
    "NEW_STUDIO": 65536,  # 1 << 16
    "HTML5": 131072,  # 1 << 17
    "FOLLOWER_PERIOD_3": 8388608,  # 1 << 23
    "FOLLOWER_PERIOD_6": 262144,  # 1 << 18
    "FOLLOWER_PERIOD_12": 524288,  # 1 << 19
    "FOLLOWER_PERIOD_24": 1048576,  # 1 << 20
    "FOLLOWER_PERIOD_36": 4194304,  # 1 << 22
    "HIDE_SEX": 33554432,  # 1 << 25
}


def has_role_front(userlevel_front, role):
    return userlevel_front & USERLEVEL_FRONT[role] != 0


def has_role_back(userlevel_back, role):
    return userlevel_back & USERLEVEL_BACK[role] != 0
