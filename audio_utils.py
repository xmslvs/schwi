from typing import Optional

_mixer_initialized = False
_mixer_device = None

def ensure_mixer_initialized(devicename: Optional[str] = None) -> bool:
    """Ensure pygame mixer is initialized once and usable."""
    global _mixer_initialized, _mixer_device

    try:
        from pygame import mixer
    except Exception as e:
        print("pygame is not available:", e)
        return False

    # Already initialized with same device
    if _mixer_initialized and mixer.get_init():
        if devicename is None or devicename == _mixer_device:
            return True

    try:
        # Do NOT call mixer.quit() here — it breaks RealtimeSTT coexistence
        if devicename:
            mixer.init(devicename=devicename)
            _mixer_device = devicename
        else:
            mixer.init()
            _mixer_device = None

        _mixer_initialized = True
        return True

    except Exception as e:
        print("Failed to init pygame mixer:", e)
        _mixer_initialized = False
        _mixer_device = None
        return False
