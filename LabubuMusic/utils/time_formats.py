import json
import subprocess

def get_readable_time(total_seconds: int) -> str:
    t_count = 0
    formatted_time = ""
    val_list = []
    suffix_list = ["s", "ᴍ", "ʜ", "ᴅᴀʏs"]
    
    while t_count < 4:
        t_count += 1
        if t_count < 3:
            rem, res = divmod(total_seconds, 60)
        else:
            rem, res = divmod(total_seconds, 24)
        if total_seconds == 0 and rem == 0:
            break
        val_list.append(int(res))
        total_seconds = int(rem)
        
    for idx in range(len(val_list)):
        val_list[idx] = f"{val_list[idx]}{suffix_list[idx]}"
        
    if len(val_list) == 4:
        formatted_time += f"{val_list.pop()}, "
    
    val_list.reverse()
    formatted_time += ":".join(val_list)
    return formatted_time

def time_to_seconds(t_str: str) -> int:
    t_parts = t_str.split(":")
    if len(t_parts) == 3:
        h, m, s = map(int, t_parts)
        return (h * 3600) + (m * 60) + s
    elif len(t_parts) == 2:
        m, s = map(int, t_parts)
        return (m * 60) + s
    return 0

def seconds_to_min(total_secs: int) -> str:
    if total_secs is not None:
        total_secs = int(total_secs)
        d_val, rem = divmod(total_secs, 86400)
        h_val, rem = divmod(rem, 3600)
        m_val, s_val = divmod(rem, 60)
        
        parts = []
        if d_val > 0: parts.append(f"{d_val:02d}")
        if h_val > 0: parts.append(f"{h_val:02d}")
        parts.append(f"{m_val:02d}")
        parts.append(f"{s_val:02d}")
        return ":".join(parts)
    return "00:00"

def convert_bytes(b_size: float) -> str:
    if not b_size:
        return "0 B"
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    for u in units:
        if b_size < 1024.0:
            return f"{b_size:3.2f} {u}"
        b_size /= 1024.0
    return f"{b_size:3.2f} PB"

def speed_converter(played_str: str, speed_mult: float):
    p_parts = played_str.split(":")
    if len(p_parts) == 3:
        h, m, s = map(int, p_parts)
        t_sec = (h * 3600) + (m * 60) + s
    elif len(p_parts) == 2:
        m, s = map(int, p_parts)
        t_sec = (m * 60) + s
    else:
        t_sec = 0

    adj_sec = t_sec / speed_mult
    return seconds_to_min(int(adj_sec)), int(adj_sec)

def check_duration(file_loc):
    cmd_args = [
        "ffprobe", "-loglevel", "quiet", "-print_format", "json",
        "-show_format", "-show_streams", file_loc,
    ]
    process = subprocess.Popen(cmd_args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out_res, _ = process.communicate()
    json_res = json.loads(out_res)

    if "format" in json_res and "duration" in json_res["format"]:
        return float(json_res["format"]["duration"])
    if "streams" in json_res:
        for s_data in json_res["streams"]:
            if "duration" in s_data:
                return float(s_data["duration"])
    return "Unknown"

formats = [
    "webm", "mkv", "flv", "vob", "ogv", "ogg", "rrc", "gifv", "mng", "mov", "avi", "qt",
    "wmv", "yuv", "rm", "asf", "amv", "mp4", "m4p", "m4v", "mpg", "mp2", "mpeg", "mpe",
    "mpv", "m4v", "svi", "3gp", "3g2", "mxf", "roq", "nsv", "flac", "f4v", "f4p", "f4a", "f4b"
]