from datetime import datetime
from viewer import db
import os
import sys
import platform
import subprocess
import psutil

#if platform.system() == 'Windows':
#    sys.path.append("C:\\mpv\\")

def utc_to_local(utc_dt_string):
    utc_dt = datetime.strptime(utc_dt_string, "%Y-%m-%dT%H:%M:%S.%fZ")
    local_dt = utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)
    return datetime.strftime(local_dt, "%Y-%m-%d %I:%M %p")

class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=False, nullable=False)
    channelName = db.Column(db.String(20), unique=False, nullable=False)
    channelID = db.Column(db.String(20), unique=False, nullable=False)
    channelImg = db.Column(db.String(50), unique=False, nullable=False)
    publishedAt = db.Column(db.String(20), unique=False, nullable=False)
    videoID = db.Column(db.String(20), unique=False, nullable=False)
    videoUrl = db.Column(db.String(50), unique=False, nullable=False)
    image = db.Column(db.String(60), unique=False, nullable=True, default="")
    mp4file = db.Column(db.String(100), unique=False, nullable=True, default="")
    description = db.Column(db.String(1000))
    mpvPid = db.Column(db.Integer, default=-1)

    def __repr__(self):
        return f"Video('{self.title}', '{self.videoID}', '{self.channelName}', '{self.image}')"

    def play_mpv(self):
        try:
            if self.mp4file == "":
                print("playing from url")
                if platform.system() != 'Windows':
                    mpvProcess = subprocess.Popen(['setsid','mpv', self.videoUrl, '&'], shell=False)
                else:
                    mpvProcess = subprocess.Popen(['start','C:\\mpv\\mpv.exe', self.videoUrl], shell=True)
            else:
                print("playing from file")
                if platform.system() != 'Windows':
                    mpvProcess = subprocess.Popen(['setsid','mpv', self.mp4file, '&'], shell=False)
                else:
                    mpvProcess = subprocess.Popen(['start', 'C:\\mpv\\mpv.exe', self.mp4file], shell=True)
            self.mpvPid = mpvProcess.pid
            db.session.commit()
            return True
        except:
            return False

    def kill_mpv(self):
        proc = psutil.Process(self.mpvPid)
        try:
            children = proc.children()
            for child in children:
                try:
                    child.terminate()
                except:
                    pass
            gone, still_alive = psutil.wait_procs(children, timeout=3)
            for p in still_alive:
                p.kill()
            proc.kill()
        except:
            pass

    def status(self):
        if self.mpvPid:
            if psutil.pid_exists(self.mpvPid):
                p = psutil.Process(self.mpvPid)
                status = p.status()
                if status == 'zombie':
                    self.mpvPid = -1
                    db.session.commit()
                    return False
                else:
                    return True
            else:
                return False
        else:
            return False


#class Channel(db.Model):
