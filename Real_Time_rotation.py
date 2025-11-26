import maya.cmds as cmds
import datetime

# === CONFIG ===
HOUR_PIVOT   = "hour_pivot"
MINUTE_PIVOT = "minute_pivot"
SECOND_PIVOT = "second_pivot"
ROTATE_AXIS  = "rotateY"      # change to "rotateZ" if needed
# ==============


def _clock_update(*args):
    """Internal: update hand rotations from system time, then reschedule itself."""
    now  = datetime.datetime.now()
    hr   = now.hour % 12
    mins = now.minute
    secs = now.second + now.microsecond / 1e6  # smooth seconds

    # angles (0 at 12 o'clock, negative = clockwise)
    sec_angle = -(secs * 6.0)                       # 360 / 60
    min_angle = -(mins * 6.0 + secs * 0.1)          # 6° per min + 0.1° per sec
    hr_angle  = -(hr * 30.0 + mins * 0.5)           # 30° per hour + 0.5° per min

    try:
        if cmds.objExists(SECOND_PIVOT):
            cmds.setAttr(f"{SECOND_PIVOT}.{ROTATE_AXIS}", sec_angle)
        if cmds.objExists(MINUTE_PIVOT):
            cmds.setAttr(f"{MINUTE_PIVOT}.{ROTATE_AXIS}", min_angle)
        if cmds.objExists(HOUR_PIVOT):
            cmds.setAttr(f"{HOUR_PIVOT}.{ROTATE_AXIS}", hr_angle)
    except Exception as e:
        print("Clock update error:", e)

    # schedule next update on idle
    cmds.scriptJob(runOnce=True, idleEvent=_clock_update)


def stop_clock():
    """Kill all scriptJobs related to this real-time clock."""
    jobs = cmds.scriptJob(listJobs=True) or []
    killed = []
    for j in jobs:
        txt = j.lower()
        if "clock_update" in txt or "_clock_update" in txt or "update_clock" in txt:
            job_id = int(j.split(":")[0])
            try:
                cmds.scriptJob(kill=job_id, force=True)
                killed.append(job_id)
            except Exception:
                pass
    if killed:
        print("⏹ Stopped clock scriptJobs:", killed)
    else:
        print("No clock scriptJobs found.")


def start_clock():
    """Start real-time clock (stops any old instances first)."""
    # make sure rotate axis is unlocked so setAttr works
    for p in (HOUR_PIVOT, MINUTE_PIVOT, SECOND_PIVOT):
        if cmds.objExists(p):
            try:
                cmds.setAttr(f"{p}.{ROTATE_AXIS}", lock=False)
            except Exception:
                pass

    # stop any old jobs to avoid duplicates
    stop_clock()

    # start new updater
    _clock_update()
    print("▶ Real-time clock started (system time). It runs even if timeline is not playing.")


print("Loaded start_clock() and stop_clock().")
print("Call start_clock() to begin real-time rotation, stop_clock() to stop.")
